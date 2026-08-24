import os
import pandas as pd
from sqlalchemy import text
from db import conectar

CARPETA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CSV = os.path.join(CARPETA_PROYECTO, "Venta_online_c.csv")
RUTA_SCHEMA = os.path.join(CARPETA_PROYECTO, "sql", "schema.sql")

# llamo la funcion conectar que estableci en mi db.py
motor = conectar()


# Extracción: leer el CSV
print("\n=== Extraccion ===")

df = pd.read_csv(RUTA_CSV, sep=";")

print("Filas leídas:", len(df))
print("Columnas:", list(df.columns))


# Revision de los datos 

print("\n === Revision de datos ===")

print("\nValores nulos por columna:")
print(df.isna().sum())

print("\nFilas duplicadas completas:", df.duplicated().sum())
print("Id_cliente repetidos:", df["Id_cliente"].duplicated().sum())

print("\nValores únicos en las columnas de catálogo:")
print("  Genero:    ", sorted(df["Genero"].unique().tolist()))
print("  MetodoPago:", sorted(df["MetodoPago"].unique().tolist()))
print("  Navegador: ", sorted(df["Navegador"].unique().tolist()))
print("  Boletin:   ", sorted(df["Boletin"].unique().tolist()))
print("  Vale:      ", sorted(df["Vale"].unique().tolist()))

print("\nRangos de las columnas numéricas:")
for columna in ["Edad", "Venta_total", "N_Compras", "MontoCompra", "Tiempo"]:
    print(f"  {columna}: min = {df[columna].min()}, max = {df[columna].max()}")


# Limpieza de los datos
print("\n Limpieza de los datos")

filas_antes = len(df)

# Se quitan filas repetidas y filas con datos faltantes
df = df.drop_duplicates()
df = df.dropna()

# Se descartan valores imposibles según el diccionario de datos
df = df[df["Edad"] > 0]
df = df[df["MontoCompra"] > 0]
df = df[df["Venta_total"] > 0]
df = df[df["Genero"].isin([0, 1])]
df = df[df["MetodoPago"].isin([0, 1, 2])]
df = df[df["Navegador"].isin([0, 1, 2, 3, 4])]
df = df[df["Boletin"].isin([0, 1])]
df = df[df["Vale"].isin([0, 1])]

print("Filas antes de limpiar: ", filas_antes)
print("Filas después:", len(df))
print("Filas eliminadas:", filas_antes - len(df))


# Tranformación: nombres y tipos
print("\n=== Tranformación ===")

# Se pasan los nombres de columna a español en minúsculas, iguales a los de las tablas
df = df.rename(columns={
    "Id_cliente": "id_cliente",
    "Edad": "edad",
    "Genero": "id_genero",
    "Venta_total": "venta_total",
    "N_Compras": "n_compras",
    "FechaCompra": "fecha_compra",
    "MontoCompra": "monto_compra",
    "MetodoPago": "id_metodo_pago",
    "Tiempo": "tiempo",
    "Navegador": "id_navegador",
    "Boletin": "boletin",
    "Vale": "vale",
})

# La fecha viene como texto en formato día.mes.año con el año de 2 dígitos
df["fecha_compra"] = pd.to_datetime(df["fecha_compra"], format="%d.%m.%y")

print("Tipos de datos ya convertidos:")
print(df.dtypes)


# armar las tablas
print("\n=== Armar las tablas ===")

# Los catálogos se escriben a mano: son los códigos del diccionario
df_genero = pd.DataFrame({
    "id_genero": [0, 1],
    "nombre": ["Masculino", "Femenino"],
})

df_metodo_pago = pd.DataFrame({
    "id_metodo_pago": [0, 1, 2],
    "nombre": ["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito"],
})

df_navegador = pd.DataFrame({
    "id_navegador": [0, 1, 2, 3, 4],
    "nombre": ["Tienda Física", "Navegador 1", "Navegador 2", "Navegador 3", "Navegador 4"],
})

# Columnas que describen al cliente
df_clientes = df[["id_cliente", "edad", "id_genero", "venta_total", "n_compras"]]

# Columnas que describen la compra.
df_compras = df[["id_cliente", "fecha_compra", "monto_compra", "id_metodo_pago", "id_navegador", "tiempo", "boletin", "vale"]]

print("Filas para clientes:", len(df_clientes))
print("Filas para compras: ", len(df_compras))


# Carga a la db

print("\n=== Carga de datos a la db ===")

# se recrean las tablas ejecutando el archivo schema.sql
archivo = open(RUTA_SCHEMA, "r", encoding="utf-8")
sql_schema = archivo.read()
archivo.close()

with motor.begin() as conexion:
    conexion.execute(text(sql_schema))
print("Tablas creadas")


# estos metodos method="multi" y chunksize agrupan los INSERT en lotes ya que sin esto
# yo estaria enviado fila por fila
df_genero.to_sql("genero", motor, if_exists="append", index=False)
df_metodo_pago.to_sql("metodo_pago", motor, if_exists="append", index=False)
df_navegador.to_sql("navegador", motor, if_exists="append", index=False)
print("Catálogos cargados")

df_clientes.to_sql("clientes", motor, if_exists="append", index=False, method="multi", chunksize=1000)
print("Clientes cargados")

df_compras.to_sql("compras", motor, if_exists="append", index=False, method="multi", chunksize=1000)
print("Compras cargadas")


print("\n === Verificacion de datos ===")

with motor.connect() as conexion:
    for tabla in ["genero", "metodo_pago", "navegador", "clientes", "compras"]:
        total = conexion.execute(text(f"SELECT COUNT(*) FROM {tabla}")).fetchone()[0]
        print(f"  {tabla}: {total} filas")