# Carga variables de entorno
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    """Genera un engine de conexion para PostgreSQL

    Returns:
        _type_: Instancia con sqlAlchemy engine conectada a la base de datos.
    """    
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')

    url = (f'postgresql://{user}:{password}'f'@{host}:{port}/{db_name}')

    return create_engine(url)


def subir_a_postgres(df: pd.DataFrame,nombre_tabla: str,if_exists: str = 'append') -> None:
    """
    Inserta un DataFrame en PostgreSQL.

    Args:
        df (pd.DataFrame): DataFrame a insertar.
        nombre_tabla (str): Nombre tabla destino.
        if_exists (str): replace, append o fail.
    """

    try:

        engine = get_engine()

        print('Conexión PostgreSQL exitosa.')

        df = df.reset_index(drop=True)

        # eliminar duplicados si existe customerid
        if 'customerid' in df.columns:
            df = df.drop_duplicates(subset=['customerid'])

        # limpiar nombres columnas
        df.columns = [str(c).strip()for c in df.columns]

        # insertar
        df.to_sql(nombre_tabla,engine,if_exists=if_exists,index=False)

        print(f'Datos insertados en tabla: {nombre_tabla}')

    except Exception as e:
        print(f'Error PostgreSQL: {e}')
        raise