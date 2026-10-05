import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

CARPETA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def conectar():
    load_dotenv(os.path.join(CARPETA_PROYECTO, ".env"))

    url = os.getenv("DATABASE_URL")

    if not url:
        raise Exception(" No se encontró url de la db ")

    return create_engine(url)


if __name__ == "__main__":
    motor = conectar()

    with motor.connect() as conexion:
        resultado = conexion.execute(text("SELECT version()"))
        version = resultado.fetchone()[0]

    print("Conexión exitosa a Neondb!")
    print(version)
