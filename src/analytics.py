import json
import pandas as pd
from db import conectar


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
    df["rango_edad"] = pd.cut(df["edad"], bins=cortes, labels=etiquetas).astype(str)

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
    preferido = {str(genero): str(tabla.loc[genero].idxmax()) for genero in tabla.index}

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
    ]
    
    for titulo, funcion in analisis:
        print("\n" + "=" * 30)
        print(titulo)
        print("=" * 30)
        resultado = funcion(motor)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
