# Carga variables de entorno
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


load_dotenv()

logger = logging.getLogger(__name__)

def get_engine():
    """Genera un engine de conexion para PostgreSQL

    Returns:
        _type_: Instancia con sqlAlchemy engine conectada a la base de datos.
    """
    REQUIRED_DB_VARS = ['POSTGRES_USER','POSTGRES_PASSWORD','DB_HOST','DB_PORT','POSTGRES_DB']
    
    env_vars = {var: os.getenv(var) for var in REQUIRED_DB_VARS}
    
    missing_var = [var for var, val in env_vars.items() if not val]
    
    if missing_var:
        error_msg = f'Faltan variables de entorno de configuración {", " .join(missing_var)}'
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        url = (f"postgresql://{env_vars['POSTGRES_USER']}:{env_vars['POSTGRES_PASSWORD']}@{env_vars['DB_HOST']}:{env_vars['DB_PORT']}/{env_vars['POSTGRES_DB']}")
        return create_engine(url)
    
    except SQLAlchemyError as e:
        logger.error(f'Error critico al inicializar el engine SQLAlchemy')
        raise e

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

        logger.info('Conexión PostgreSQL exitosa.')

        df = df.reset_index(drop=True)

        # eliminar duplicados si existe customerid
        if 'customerid' in df.columns:
            df = df.drop_duplicates(subset=['customerid'])

        # limpiar nombres columnas
        df.columns = [str(c).strip()for c in df.columns]

        # insertar
        df.to_sql(nombre_tabla,engine,if_exists=if_exists,index=False)

        logger.info(f'Datos insertados en tabla: {nombre_tabla}')

    except Exception as e:
        logger.error(f'Error PostgreSQL: {e}')
        raise