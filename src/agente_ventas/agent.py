import os
import base64
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types as genai_types
from mcp import StdioServerParameters

# --------------------------------------------------------------------
# 1. Variables de entorno
# --------------------------------------------------------------------
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(RAIZ_PROYECTO, ".env"))

ENTORNO_SUBPROCESO = dict(os.environ)

# --------------------------------------------------------------------
# 2. Ubicar el servidor MCP (src/mcp_server.py, hecho por ③)
# --------------------------------------------------------------------
CARPETA_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_MCP_SERVER = os.path.join(CARPETA_SRC, "mcp_server.py")

import sys
PYTHON_INTERPRETE = sys.executable

# --------------------------------------------------------------------
# 3. Modelo
# --------------------------------------------------------------------
MODELO = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")

# --------------------------------------------------------------------
# 4. Toolset -> conecta con el servidor MCP real de ③
# --------------------------------------------------------------------
mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=PYTHON_INTERPRETE,
            args=[RUTA_MCP_SERVER],
            env=ENTORNO_SUBPROCESO,
        ),
        timeout=60,
    ),
)

# --------------------------------------------------------------------
# 5. Instrucción del agente
# --------------------------------------------------------------------
INSTRUCCION = """
Eres un analista de datos Junior de una empresa que vende en línea y que
está por abrir su primera sucursal física. Tu trabajo es responder
preguntas sobre las ventas del año 2021 usando ÚNICAMENTE las
herramientas (tools) que tienes disponibles — nunca inventes cifras.

## Cómo elegir la herramienta
- estadisticas_basicas: media, mediana, moda, mínimo y máximo de edad,
  venta_total, monto_compra y n_compras. Úsala para preguntas generales
  tipo "cuál es el promedio de..." o "cuéntame un resumen de los datos".
- ventas_por_mes: totales de venta por mes, mes con más y con menos
  ventas, tendencia a lo largo del año.
- ranking_navegadores: uso y ventas por navegador (Navegador 1-4) y
  por Tienda Física; cuál canal es más y menos usado.
- ventas_por_metodo_pago: distribución entre Efectivo, Tarjeta de
  Crédito y Tarjeta de Débito, y cuánto se vendió contra entrega/efectivo.
- segmentacion_por_edad: patrones de compra por rango de edad
  (18-25, 26-35, 36-45, 46-60, 61+), qué grupo gasta más.
- comparativa_generos: diferencias de comportamiento de compra entre
  géneros, y método de pago preferido por cada uno.
- uso_boletin_vale: cuántos clientes usan boletín y/o vale, y en qué
  meses se usan más.
- patrones_boletin_vale: cruza boletín y vale (con/sin ambos) y compara
  el gasto promedio de cada combinación.
- correlaciones: relación estadística entre venta total y edad, entre
  género y método de pago, y entre uso de boletín y vale.

Cada tool tiene los parámetros opcionales `incluir_datos` e
`incluir_grafica` (True por defecto). Si el usuario solo pide un dato o
un número puntual, puedes poner incluir_grafica=False para responder
más rápido. Si pide "muéstrame", "gráfica" o "visualiza", deja
incluir_grafica=True.

## Cómo responder
- Responde en español, en un tono profesional pero claro, como si le
  hablaras a un gerente sin conocimientos técnicos de estadística.
- No repitas el JSON crudo que devuelve la tool: interpreta los números
  y dilos en una o dos oraciones (ej. "El mes con más ventas fue julio,
  con Q45,230.10").
- Si la tool devuelve una imagen, menciona que la gráfica se generó y
  descríbela brevemente en una frase (qué muestra, qué patrón resalta).
- Si una pregunta necesita combinar dos tools (ej. "compara ventas por
  mes y por navegador"), llama ambas tools y sintetiza una sola
  respuesta.
- Si preguntan algo que NINGUNA tool puede responder (por ejemplo datos
  de años distintos a 2021, o predicciones futuras), dilo con honestidad:
  explica qué información sí tienes disponible en vez de inventar un
  número.
- Si una tool falla o la base de datos no responde, informa el error de
  forma clara y sugiere reintentar; nunca inventes un resultado de
  respaldo.

## Contexto de negocio
La empresa quiere usarte para tomar decisiones sobre su nueva sucursal
física y para mejorar sus ventas online, así que cuando sea relevante
puedes añadir una frase de contexto de negocio (ej. si el canal
"Tienda Física" ya representa ventas pese a no existir aún físicamente,
puede ser un dato interesante de mencionar), pero sin inventar
recomendaciones que no estén respaldadas por los datos.
"""

# --------------------------------------------------------------------
# 6. Callback: guarda las gráficas de las tools como "artifacts"
# --------------------------------------------------------------------
async def guardar_imagenes_como_artifacts(tool, args, tool_context, tool_response):
    if not tool_response:
        return None

    if isinstance(tool_response, dict) and "content" in tool_response:
        bloques = tool_response["content"]
    elif isinstance(tool_response, list):
        bloques = tool_response
    else:
        bloques = [tool_response]

    contador = 0

    for bloque in bloques:
        # Caso 1: el bloque ya es un google.genai.types.Part con imagen inline
        inline = getattr(bloque, "inline_data", None)
        if inline is not None:
            contador += 1
            nombre = f"{tool.name}_{contador}.png"
            try:
                await tool_context.save_artifact(filename=nombre, artifact=bloque)
            except Exception as e:
                print(f"[guardar_imagenes_como_artifacts] No se pudo guardar {nombre}: {e}")
            continue

        # Caso 2: el bloque viene como dict u objeto MCP (TextContent/ImageContent)
        tipo = bloque.get("type") if isinstance(bloque, dict) else getattr(bloque, "type", None)
        if tipo != "image":
            continue

        datos_b64 = bloque.get("data") if isinstance(bloque, dict) else getattr(bloque, "data", None)
        mime = (
            bloque.get("mimeType") if isinstance(bloque, dict) else getattr(bloque, "mimeType", None)
        ) or "image/png"

        if not datos_b64:
            continue

        try:
            datos_bytes = base64.b64decode(datos_b64)
            contador += 1
            nombre = f"{tool.name}_{contador}.png"
            parte = genai_types.Part.from_bytes(data=datos_bytes, mime_type=mime)
            await tool_context.save_artifact(filename=nombre, artifact=parte)
            print(f"[guardar_imagenes_como_artifacts] Guardado: {nombre}")
        except Exception as e:
            print(f"[guardar_imagenes_como_artifacts] No se pudo decodificar/guardar imagen: {e}")

    # No modifica lo que ve el modelo, solo guarda la imagen aparte
    return None


# --------------------------------------------------------------------
# 7. Agente raíz — ADK busca esta variable exacta ("root_agent")
# --------------------------------------------------------------------
root_agent = LlmAgent(
    model=MODELO,
    name="analista_ventas_junior",
    description="Analista de datos Junior que responde preguntas sobre las ventas online 2021 usando el servidor MCP de análisis.",
    instruction=INSTRUCCION,
    tools=[mcp_toolset],
    after_tool_callback=guardar_imagenes_como_artifacts,
)
