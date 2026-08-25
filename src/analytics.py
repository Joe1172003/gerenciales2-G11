from db import conectar
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
sns.set_theme(style="whitegrid", palette="muted")


# Se utiliza para que el agente responda "marzo" y no "3"
MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


# 2.1 - Obtener los datos de la base de datos
# Se hace en un solo lugar para no repetir la consulta en cada funcion
def cargar_datos(conexion):
    consulta = """
        SELECT
            cli.id_cliente,
            cli.edad,
            cli.venta_total,
            cli.n_compras,
            gen.nombre AS genero,
            com.fecha_compra,
            com.monto_compra,
            com.tiempo,
            com.boletin,
            com.vale,
            met.nombre AS metodo_pago,
            nav.nombre AS navegador
        FROM compras com
        JOIN clientes cli
            ON com.id_cliente = cli.id_cliente
        JOIN genero gen
            ON cli.id_genero = gen.id_genero
        JOIN metodo_pago met
            ON com.id_metodo_pago = met.id_metodo_pago
        JOIN navegador nav
            ON com.id_navegador = nav.id_navegador
    """

    # Realiza la consulta y devuelve un DataFrame de pandas con los datos
    df = pd.read_sql(consulta, conexion)

    # Convierte los valores a float
    df["venta_total"] = df["venta_total"].astype(float)
    df["monto_compra"] = df["monto_compra"].astype(float)

    # Se convierte la fecha a datetime y se extrae el mes
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes"] = df["fecha_compra"].dt.month

    return df


# Funciones de apoyo: ayudan a dar formato a los resultados
def a_diccionario(serie):
    return {str(llave): round(float(valor), 2) for llave, valor in serie.items()}


def a_diccionario_entero(serie):
    return {str(llave): int(valor) for llave, valor in serie.items()}


# 2.2 - Calcular estadisticas basicas (media, mediana, moda)
# Las variables numericas del archivo son cuatro:
# edad, venta_total, monto_compra y n_compras
def estadisticas_basicas(conexion) -> dict:
    df = cargar_datos(conexion)

    resultado = {}
    for columna in ["edad", "venta_total", "monto_compra", "n_compras"]:
        resultado[columna] = {
            "media": round(float(df[columna].mean()), 2),
            "mediana": round(float(df[columna].median()), 2),
            # mode() puede devolver varios valores si empatan, se toma el primero
            "moda": round(float(df[columna].mode()[0]), 2),
            "minimo": round(float(df[columna].min()), 2),
            "maximo": round(float(df[columna].max()), 2),
        }

    return {
        "total_registros": int(len(df)),
        "estadisticas": resultado,
    }


# 2.3 - Distribucion de ventas por mes (ventas_por_mes)
# 3.1 - Determinar los meses con mayores y menores ventas (mes_mayor_venta y mes_menor_venta)
def ventas_por_mes(conexion) -> dict:
    df = cargar_datos(conexion)

    # Agrupa las compras por mes y suma el monto vendido en cada uno
    ventas = df.groupby("mes")["monto_compra"].sum()

    # Agrupa las compras por mes y cuenta cuantas hubo en cada mes
    cantidad = df.groupby("mes").size()

    return {
        "ventas_por_mes": {MESES[m]: round(float(v), 2) for m, v in ventas.items()},
        "compras_por_mes": {MESES[m]: int(v) for m, v in cantidad.items()},
        "mes_mayor_venta": MESES[ventas.idxmax()],
        "monto_mes_mayor": round(float(ventas.max()), 2),
        "mes_menor_venta": MESES[ventas.idxmin()],
        "monto_mes_menor": round(float(ventas.min()), 2),
    }


# 2.3 - Distribucion de ventas por metodo de pago (ventas_por_metodo)
# 3.3 - Identificar el total de ventas pagadas contra entrega o en efectivo (total_efectivo)
def ventas_por_metodo_pago(conexion) -> dict:
    df = cargar_datos(conexion)

    # Agrupa por metodo de pago y suma el monto de las compras
    ventas = df.groupby("metodo_pago")["monto_compra"].sum()

    # Agrupa por metodo de pago y cuenta cuantas compras hubo en cada uno
    cantidad = df.groupby("metodo_pago").size()

    # El efectivo es lo que la empresa cobra contra entrega
    ventas_efectivo = df[df["metodo_pago"] == "Efectivo"]["monto_compra"].sum()

    return {
        "ventas_por_metodo": a_diccionario(ventas),
        "compras_por_metodo": a_diccionario_entero(cantidad),
        "metodo_mas_usado": str(cantidad.idxmax()),
        "total_efectivo": round(float(ventas_efectivo), 2),
        "porcentaje_efectivo": round(float(ventas_efectivo / ventas.sum() * 100), 2),
    }


# 2.3 - Distribucion de ventas por navegador (compras_por_canal y ventas_por_canal)
# 3.2 - Identificar el navegador mas y menos popular (navegador_mas_usado y navegador_menos_usado)
def ranking_navegadores(conexion) -> dict:
    df = cargar_datos(conexion)

    cantidad = df.groupby("navegador").size()
    ventas = df.groupby("navegador")["monto_compra"].sum()

    # Solo navegadores (se quita la tienda fisica)
    solo_navegadores = df[df["navegador"] != "Tienda Física"]
    cantidad_navegadores = solo_navegadores.groupby("navegador").size()

    compras_tienda_fisica = int((df["navegador"] == "Tienda Física").sum())

    return {
        "compras_por_canal": a_diccionario_entero(cantidad),
        "ventas_por_canal": a_diccionario(ventas),
        "navegador_mas_usado": str(cantidad_navegadores.idxmax()),
        "navegador_menos_usado": str(cantidad_navegadores.idxmin()),
        "compras_en_tienda_fisica": compras_tienda_fisica,
        "porcentaje_tienda_fisica": round(compras_tienda_fisica / len(df) * 100, 2),
        "canal_mas_usado": str(cantidad.idxmax()),
    }


# 2.3 - Distribucion de ventas por Boletin y Vale (clientes_con_boletin / clientes_con_vale y sus contrarios)
# 3.4 - Identificar los meses con mayor uso de boletines y vales (mes_mas_boletines y mes_mas_vales)
def uso_boletin_vale(conexion) -> dict:
    df = cargar_datos(conexion)

    # Cuenta cuantos registros tienen boletin y cuantos tienen vale
    con_boletin = int((df["boletin"] == 1).sum())
    con_vale = int((df["vale"] == 1).sum())

    # Filtra los registros con boletin/vale y cuenta cuantos hay en cada mes
    boletin_por_mes = df[df["boletin"] == 1].groupby("mes").size()
    vale_por_mes = df[df["vale"] == 1].groupby("mes").size()

    return {
        "clientes_con_boletin": con_boletin,
        "clientes_sin_boletin": int(len(df) - con_boletin),
        "clientes_con_vale": con_vale,
        "clientes_sin_vale": int(len(df) - con_vale),
        "boletines_por_mes": {MESES[m]: int(v) for m, v in boletin_por_mes.items()},
        "vales_por_mes": {MESES[m]: int(v) for m, v in vale_por_mes.items()},
        "mes_mas_boletines": MESES[boletin_por_mes.idxmax()],
        "mes_mas_vales": MESES[vale_por_mes.idxmax()],
    }


# 4.1 - Agrupar clientes por edad y analizar patrones de compra
def segmentacion_por_edad(conexion) -> dict:
    df = cargar_datos(conexion)

    # El 17 es para que el cliente de 18 quede incluido
    cortes = [17, 25, 35, 45, 60, 120]
    etiquetas = ["18-25", "26-35", "36-45", "46-60", "61 o más"]

    # Clasifica cada edad en un rango, usando los limites de cortes y los nombres de etiquetas
    df["rango_edad"] = pd.cut(df["edad"], bins=cortes,
                              labels=etiquetas).astype(str)

    # Agrupa por rango de edad y calcula para cada grupo:
    resumen = df.groupby("rango_edad").agg(
        clientes=("id_cliente", "count"),
        venta_total_promedio=("venta_total", "mean"),
        monto_compra_promedio=("monto_compra", "mean"),
        compras_promedio=("n_compras", "mean"),
    )

    resultado = {}
    for rango in resumen.index:
        resultado[rango] = {
            "clientes": int(resumen.loc[rango, "clientes"]),
            "venta_total_promedio": round(float(resumen.loc[rango, "venta_total_promedio"]), 2),
            "monto_compra_promedio": round(float(resumen.loc[rango, "monto_compra_promedio"]), 2),
            "compras_promedio": round(float(resumen.loc[rango, "compras_promedio"]), 2),
        }

    return {
        "segmentacion_por_edad": resultado,
        "rango_que_mas_gasta": str(resumen["venta_total_promedio"].idxmax()),
        "rango_con_mas_clientes": str(resumen["clientes"].idxmax()),
    }


# 4.2 - Comparar el comportamiento de compra entre géneros
def comparativa_generos(conexion) -> dict:
    df = cargar_datos(conexion)

    resumen = df.groupby("genero").agg(
        clientes=("id_cliente", "count"),
        edad_promedio=("edad", "mean"),
        venta_total_promedio=("venta_total", "mean"),
        monto_compra_promedio=("monto_compra", "mean"),
        compras_promedio=("n_compras", "mean"),
    )

    resultado = {}
    for genero in resumen.index:
        resultado[genero] = {
            "clientes": int(resumen.loc[genero, "clientes"]),
            "edad_promedio": round(float(resumen.loc[genero, "edad_promedio"]), 2),
            "venta_total_promedio": round(float(resumen.loc[genero, "venta_total_promedio"]), 2),
            "monto_compra_promedio": round(float(resumen.loc[genero, "monto_compra_promedio"]), 2),
            "compras_promedio": round(float(resumen.loc[genero, "compras_promedio"]), 2),
        }

    # Crea una tabla que cuenta los metodos de pago usados por cada genero
    tabla = pd.crosstab(df["genero"], df["metodo_pago"])

    # Obtiene para cada genero, el metodo de pago mas utilizado
    preferido = {str(genero): str(
        tabla.loc[genero].idxmax()) for genero in tabla.index}

    return {
        "comparativa_generos": resultado,
        "metodo_pago_preferido": preferido,
        "genero_que_mas_gasta": str(resumen["venta_total_promedio"].idxmax()),
    }


# 4.3 - Agrupar clientes por boletin y vale, y analizar patrones de compra
def patrones_boletin_vale(conexion) -> dict:
    df = cargar_datos(conexion)

    # Crea una columna grupo que clasifica cada registro segun tenga bolentin y/o vale
    df["grupo"] = df.apply(
        lambda fila: ("con boletín" if fila["boletin"] == 1 else "sin boletín")
        + " / "
        + ("con vale" if fila["vale"] == 1 else "sin vale"),
        axis=1,
    )

    resumen = df.groupby("grupo").agg(
        clientes=("id_cliente", "count"),
        venta_total_promedio=("venta_total", "mean"),
        compras_promedio=("n_compras", "mean"),
    )

    resultado = {}
    for grupo in resumen.index:
        resultado[grupo] = {
            "clientes": int(resumen.loc[grupo, "clientes"]),
            "venta_total_promedio": round(float(resumen.loc[grupo, "venta_total_promedio"]), 2),
            "compras_promedio": round(float(resumen.loc[grupo, "compras_promedio"]), 2),
        }

    return {
        "patrones_boletin_vale": resultado,
        "grupo_que_mas_gasta": str(resumen["venta_total_promedio"].idxmax()),
    }


# 5.1 - Relacion entre el total de venta y la edad del cliente (venta_total_vs_edad)
# 5.2 - Correlacion entre genero del cliente y metodo de pago preferido (genero_vs_metodo_pago)
# 5.3 - Correlacion entre clientes que utilizan boletines y vales (boletin_vs_vale)
def correlaciones(conexion) -> dict:
    df = cargar_datos(conexion)

    # 5.1
    correlacion_venta_edad = float(df["venta_total"].corr(df["edad"]))

    # 5.2
    tabla_genero_pago = pd.crosstab(
        df["genero"], df["metodo_pago"], normalize="index"
    ) * 100

    porcentajes = {}
    for genero in tabla_genero_pago.index:
        porcentajes[str(genero)] = {
            str(metodo): round(float(tabla_genero_pago.loc[genero, metodo]), 2)
            for metodo in tabla_genero_pago.columns
        }

    # 5.3
    correlacion_boletin_vale = float(df["boletin"].corr(df["vale"]))

    tabla_boletin_vale = pd.crosstab(df["boletin"], df["vale"])
    conteo_boletin_vale = {}
    for boletin in tabla_boletin_vale.index:
        conteo_boletin_vale[f"boletin={boletin}"] = {
            f"vale={vale}": int(tabla_boletin_vale.loc[boletin, vale])
            for vale in tabla_boletin_vale.columns
        }

    return {
        "venta_total_vs_edad": {
            "coeficiente_pearson": round(correlacion_venta_edad, 4),
            "interpretacion": interpretar_correlacion(correlacion_venta_edad),
        },
        "genero_vs_metodo_pago": {
            "porcentajes_por_genero": porcentajes,
            "nota": "Son dos variables categóricas, por eso se comparan porcentajes y no un coeficiente.",
        },
        "boletin_vs_vale": {
            "coeficiente_pearson": round(correlacion_boletin_vale, 4),
            "interpretacion": interpretar_correlacion(correlacion_boletin_vale),
            "tabla_de_conteo": conteo_boletin_vale,
        },
    }


# Funciones de generacion de graficos
def asegurar_directorio():
    ruta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'graficas')
    os.makedirs(ruta, exist_ok=True)
    return ruta


def grafico_ventas_por_mes_barras(conexion) -> dict:
    datos = ventas_por_mes(conexion)
    ventas_dicc = datos["ventas_por_mes"]

    df_grafico = pd.DataFrame(list(ventas_dicc.items()), columns=[
                              "mes_nombre", "monto_compra"])

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_grafico, x="mes_nombre",
                     y="monto_compra", color="skyblue")
    for contenedor in ax.containers:
        ax.bar_label(contenedor, fmt='%.2f', padding=3)
    plt.title("Ventas Totales por Mes")
    plt.xlabel("Mes")
    plt.ylabel("Monto de Compra")
    plt.xticks(rotation=45)

    ruta = os.path.join(asegurar_directorio(), "ventas_por_mes_barras.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/ventas_por_mes_barras.png", "tipo": "barras", "estado": "generado"}


def grafico_tendencia_ventas_lineas(conexion) -> dict:
    datos = ventas_por_mes(conexion)
    ventas_dicc = datos["ventas_por_mes"]

    df_grafico = pd.DataFrame(list(ventas_dicc.items()), columns=[
                              "mes_nombre", "monto_compra"])

    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    plt.plot(df_grafico["mes_nombre"],
             df_grafico["monto_compra"], marker="o", color="darkorange")

    # Agregar el valor numerico con recuadro
    for i, (mes, monto) in enumerate(zip(df_grafico["mes_nombre"], df_grafico["monto_compra"])):
        ax.annotate(f"{monto:,.0f}",
                    (i, monto),
                    textcoords="offset points",
                    xytext=(0, 12),
                    ha='center',
                    fontsize=8,
                    weight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkorange", alpha=0.8))

    plt.title("Tendencia de Ventas por Mes")
    plt.xlabel("Mes")
    plt.ylabel("Monto de Compra")
    plt.xticks(rotation=45)

    ruta = os.path.join(asegurar_directorio(), "tendencia_ventas_lineas.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/tendencia_ventas_lineas.png", "tipo": "lineas", "estado": "generado"}


def grafico_edad_vs_ventas_barras_agrupadas(conexion) -> dict:
    datos = segmentacion_por_edad(conexion)
    segmentacion = datos["segmentacion_por_edad"]

    rangos = list(segmentacion.keys())
    promedios = [info["venta_total_promedio"]
                 for info in segmentacion.values()]
    df_grafico = pd.DataFrame(
        {"Rango de Edad": rangos, "Venta Promedio": promedios})

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_grafico, x="Rango de Edad",
                     y="Venta Promedio", color="teal")

    for contenedor in ax.containers:
        ax.bar_label(contenedor, fmt='%.2f', padding=3)

    plt.title("Promedio de Venta Total por Rango de Edad")
    plt.xlabel("Rango de Edad")
    plt.ylabel("Venta Total Promedio")

    ruta = os.path.join(asegurar_directorio(),
                        "edad_vs_ventas_barras_agrupadas.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/edad_vs_ventas_barras_agrupadas.png", "tipo": "barras_agrupadas", "estado": "generado"}


def grafico_metodo_pago_pastel(conexion) -> dict:
    datos = ventas_por_metodo_pago(conexion)
    conteo_dicc = datos["compras_por_metodo"]

    etiquetas = list(conteo_dicc.keys())
    valores = list(conteo_dicc.values())

    plt.figure(figsize=(8, 8))
    plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=140)
    plt.title("Distribucion de Metodos de Pago")

    ruta = os.path.join(asegurar_directorio(), "metodo_pago_pastel.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/metodo_pago_pastel.png", "tipo": "pastel", "estado": "generado"}


def grafico_compras_por_genero_densidad(conexion) -> dict:
    df = cargar_datos(conexion)

    plt.figure(figsize=(10, 6))

    # Asignar un color a cada genero para mantener consistencia
    paleta = sns.color_palette()
    generos = df["genero"].unique()
    dict_colores = {gen: paleta[i] for i, gen in enumerate(generos)}

    ax = sns.kdeplot(data=df, x="monto_compra", hue="genero",
                     fill=True, common_norm=False, alpha=0.5, palette=dict_colores)

    # Calcular y dibujar los promedios
    promedios = df.groupby("genero")["monto_compra"].mean()
    for i, (genero, promedio) in enumerate(promedios.items()):
        color = dict_colores[genero]
        ax.axvline(promedio, color=color, linestyle='--', alpha=0.8)
        ax.text(promedio + 2, ax.get_ylim()[1] * (0.9 - i * 0.05),
                f"Promedio {genero}: {promedio:.2f}", color=color, weight='bold')

    plt.title("Densidad de Monto de Compra por Genero")
    plt.xlabel("Monto de Compra")
    plt.ylabel("Densidad")

    ruta = os.path.join(asegurar_directorio(), "compras_genero_densidad.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/compras_genero_densidad.png", "tipo": "densidad", "estado": "generado"}


def grafico_correlacion_heatmap(conexion) -> dict:
    df = cargar_datos(conexion)
    variables_numericas = df[[
        "edad", "venta_total", "monto_compra", "n_compras"]]

    # Renombrar columnas para que sea super facil de leer
    variables_numericas = variables_numericas.rename(columns={
        "edad": "Edad",
        "venta_total": "Venta Total",
        "monto_compra": "Monto por Compra",
        "n_compras": "N. de Compras"
    })

    correlacion = variables_numericas.corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(correlacion, annot=True, fmt=".2f",
                cmap="coolwarm", vmin=-1, vmax=1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .7})
    plt.title("Relación entre Variables de Compra")

    ruta = os.path.join(asegurar_directorio(), "correlacion_heatmap.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/correlacion_heatmap.png", "tipo": "heatmap", "estado": "generado"}


def grafico_distribucion_edad_histograma(conexion) -> dict:
    df = cargar_datos(conexion)

    plt.figure(figsize=(10, 6))

    # enteros para que el eje X sea exacto
    edad_min = int(df["edad"].min())
    edad_max = int(df["edad"].max())
    bins = range(edad_min, edad_max + 4, 3)

    ax = sns.histplot(data=df, x="edad", bins=bins, kde=True, color="purple")

    # Agregar el valor numerico encima de cada barra
    for c in ax.containers:
        etiquetas = [f"{int(v.get_height())}" if v.get_height()
                     > 0 else "" for v in c]
        ax.bar_label(c, labels=etiquetas, padding=3, fontsize=8, color="black")

    plt.xticks(bins, rotation=45)

    plt.title("Distribucion de Edades de Clientes")
    plt.xlabel("Rango de Edad")
    plt.ylabel("Frecuencia")

    ruta = os.path.join(asegurar_directorio(),
                        "distribucion_edad_histograma.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/distribucion_edad_histograma.png", "tipo": "histograma", "estado": "generado"}


def grafico_compras_por_navegador_barras(conexion) -> dict:
    datos = ranking_navegadores(conexion)
    compras_dicc = datos["compras_por_canal"]

    df_grafico = pd.DataFrame(list(compras_dicc.items()), columns=["navegador", "compras"])
    df_grafico = df_grafico.sort_values(by="compras", ascending=False)

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_grafico, x="compras", y="navegador", color="mediumpurple")
    for contenedor in ax.containers:
        ax.bar_label(contenedor, padding=3)

    plt.title("Distribucion de Compras por Navegador o Canal")
    plt.xlabel("Numero de Compras")
    plt.ylabel("Navegador o Canal")

    ruta = os.path.join(asegurar_directorio(), "compras_por_navegador_barras.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/compras_por_navegador_barras.png", "tipo": "barras_horizontales", "estado": "generado"}


def grafico_boletin_pastel(conexion) -> dict:
    datos = uso_boletin_vale(conexion)
    
    etiquetas = ["Con Boletín", "Sin Boletín"]
    valores = [datos["clientes_con_boletin"], datos["clientes_sin_boletin"]]
    
    plt.figure(figsize=(6, 6))
    plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90, colors=["#ff9999","#66b3ff"])
    plt.title("Uso de Boletín por los Clientes")

    ruta = os.path.join(asegurar_directorio(), "boletin_pastel.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/boletin_pastel.png", "tipo": "pastel", "estado": "generado"}


def grafico_vale_pastel(conexion) -> dict:
    datos = uso_boletin_vale(conexion)
    
    etiquetas = ["Con Vale", "Sin Vale"]
    valores = [datos["clientes_con_vale"], datos["clientes_sin_vale"]]
    
    plt.figure(figsize=(6, 6))
    plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90, colors=["#99ff99","#ffcc99"])
    plt.title("Uso de Vale por los Clientes")

    ruta = os.path.join(asegurar_directorio(), "vale_pastel.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return {"grafico": "graficas/vale_pastel.png", "tipo": "pastel", "estado": "generado"}


# Traduce el coeficiente a palabras para que el agente de IA lo explique
def interpretar_correlacion(valor):
    fuerza = abs(valor)

    if fuerza < 0.1:
        return "prácticamente no hay relación"
    if fuerza < 0.3:
        return "relación débil"
    if fuerza < 0.5:
        return "relación moderada"
    return "relación fuerte"


if __name__ == "__main__":
    motor = conectar()

    analisis = [
        ("2.2:", estadisticas_basicas),
        ("2.3 y 3.1:", ventas_por_mes),
        ("2.3 y 3.3:", ventas_por_metodo_pago),
        ("2.3 y 3.2:", ranking_navegadores),
        ("2.3 y 3.4:", uso_boletin_vale),
        ("4.1:", segmentacion_por_edad),
        ("4.2:", comparativa_generos),
        ("4.3:", patrones_boletin_vale),
        ("5.1, 5.2 y 5.3:", correlaciones),
        ("6.1:", grafico_ventas_por_mes_barras),
        ("6.2:", grafico_tendencia_ventas_lineas),
        ("6.3:", grafico_edad_vs_ventas_barras_agrupadas),
        ("6.4:", grafico_metodo_pago_pastel),
        ("6.5:", grafico_compras_por_genero_densidad),
        ("6.6:", grafico_correlacion_heatmap),
        ("6.7:", grafico_distribucion_edad_histograma),
        ("6.8:", grafico_compras_por_navegador_barras),
        ("6.9:", grafico_boletin_pastel),
        ("6.10:", grafico_vale_pastel),
    ]

    for titulo, funcion in analisis:
        print("\n" + "=" * 30)
        print(titulo)
        print("=" * 30)
        resultado = funcion(motor)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
