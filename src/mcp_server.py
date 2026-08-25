from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from db import conectar
import analytics
import json
import base64

# Instanciar el servidor MCP
mcp = FastMCP("Servidor Practica1")

# Conexion compartida para todas las herramientas
conexion_global = conectar()

def empaquetar_respuesta(datos: dict = None, rutas_graficas: list = None) -> list:
    """Empaqueta datos en JSON e imágenes en Base64 para el cliente MCP."""
    respuesta = []
    
    if datos:
        respuesta.append(TextContent(
            type="text",
            text=json.dumps(datos, ensure_ascii=False, indent=2)
        ))
        
    if rutas_graficas:
        for ruta in rutas_graficas:
            if not ruta: continue
            try:
                with open(ruta, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    respuesta.append(ImageContent(
                        type="image",
                        data=img_data,
                        mimeType="image/png"
                    ))
            except Exception as e:
                respuesta.append(TextContent(
                    type="text",
                    text=f"[Error al cargar la imagen {ruta}: {str(e)}]"
                ))
                
    if not respuesta:
        respuesta.append(TextContent(type="text", text="Sin resultados"))
        
    return respuesta


@mcp.tool()
def estadisticas_basicas(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Obtiene las estadísticas básicas de clientes y ventas (media, mediana, moda).

    :param incluir_datos: Si es verdadero, incluye las métricas numéricas.
    :param incluir_grafica: Si es verdadero, incluye la gráfica de distribución de edades.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.estadisticas_basicas(conexion_global)
    if incluir_grafica:
        res = analytics.grafico_distribucion_edad_histograma(conexion_global)
        rutas.append(res.get("grafico"))
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def ventas_por_mes(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Analiza la distribución y tendencia de ventas por mes a lo largo del año.

    :param incluir_datos: Si es verdadero, incluye las sumatorias y métricas por mes.
    :param incluir_grafica: Si es verdadero, incluye gráficas de barras y de tendencia (líneas).
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.ventas_por_mes(conexion_global)
    if incluir_grafica:
        res1 = analytics.grafico_ventas_por_mes_barras(conexion_global)
        res2 = analytics.grafico_tendencia_ventas_lineas(conexion_global)
        rutas.extend([res1.get("grafico"), res2.get("grafico")])
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def ranking_navegadores(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Obtiene el uso y ventas generadas por cada navegador web o canal físico.

    :param incluir_datos: Si es verdadero, incluye datos numéricos por navegador.
    :param incluir_grafica: Si es verdadero, incluye la gráfica de compras por navegador.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.ranking_navegadores(conexion_global)
    if incluir_grafica:
        res = analytics.grafico_compras_por_navegador_barras(conexion_global)
        rutas.append(res.get("grafico"))
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def ventas_por_metodo_pago(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Analiza las ventas distribuidas por método de pago.

    :param incluir_datos: Si es verdadero, incluye totales por método.
    :param incluir_grafica: Si es verdadero, incluye gráfica de pastel.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.ventas_por_metodo_pago(conexion_global)
    if incluir_grafica:
        res = analytics.grafico_metodo_pago_pastel(conexion_global)
        rutas.append(res.get("grafico"))
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def segmentacion_por_edad(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Agrupa a los clientes por rango de edad y muestra sus patrones de compra.

    :param incluir_datos: Si es verdadero, incluye promedios por grupo de edad.
    :param incluir_grafica: Si es verdadero, incluye gráfica de dispersión edad vs ventas.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.segmentacion_por_edad(conexion_global)
    if incluir_grafica:
        res = analytics.grafico_edad_vs_ventas_barras_agrupadas(conexion_global)
        rutas.append(res.get("grafico"))
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def comparativa_generos(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Compara el comportamiento de compra entre los diferentes géneros.

    :param incluir_datos: Si es verdadero, incluye métricas comparativas.
    :param incluir_grafica: Si es verdadero, incluye gráfica boxplot de compras por género.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.comparativa_generos(conexion_global)
    if incluir_grafica:
        res = analytics.grafico_compras_por_genero_densidad(conexion_global)
        rutas.append(res.get("grafico"))
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def uso_boletin_vale(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Analiza las diferencias en compras de quienes usan boletines y vales frente a los que no.

    :param incluir_datos: Si es verdadero, incluye estadísticas sobre su uso.
    :param incluir_grafica: Si es verdadero, incluye gráfica sobre el uso de boletín y vale.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.uso_boletin_vale(conexion_global)
    if incluir_grafica:
        res1 = analytics.grafico_boletin_pastel(conexion_global)
        res2 = analytics.grafico_vale_pastel(conexion_global)
        rutas.extend([res1.get("grafico"), res2.get("grafico")])
        
    return empaquetar_respuesta(datos, rutas)


@mcp.tool()
def patrones_boletin_vale(incluir_datos: bool = True) -> list:
    """
    Agrupa los clientes por uso de boletín y vales y analiza sus patrones de compra.

    :param incluir_datos: Si es verdadero, incluye métricas comparativas.
    """
    datos = {}
    if incluir_datos:
        datos["datos"] = analytics.patrones_boletin_vale(conexion_global)
    return empaquetar_respuesta(datos, None)


@mcp.tool()
def correlaciones(incluir_datos: bool = True, incluir_grafica: bool = True) -> list:
    """
    Calcula coeficientes de correlación de Pearson e identifica patrones relacionados.

    :param incluir_datos: Si es verdadero, incluye coeficientes y su interpretación.
    :param incluir_grafica: Si es verdadero, incluye un mapa de calor de las variables numéricas.
    """
    datos = {}
    rutas = []
    
    if incluir_datos:
        datos["datos"] = analytics.correlaciones(conexion_global)
    if incluir_grafica:
        res = analytics.grafico_correlacion_heatmap(conexion_global)
        rutas.append(res.get("grafico"))
        
    return empaquetar_respuesta(datos, rutas)


if __name__ == "__main__":
    # Arrancar el servidor MCP usando entrada y salida estándar
    mcp.run(transport="stdio")
