# Carga variables de entorno
import os
import pandas as pd
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


load_dotenv()

logger = logging.getLogger(__name__)

def get_engine():
    """Genera un motor (engine) de conexión para una base de datos PostgreSQL.

    Soporta de manera híbrida la conexión mediante una URI directa (DATABASE_URL)
    ideal para entornos de nube como Render, o mediante variables estructuradas individuales
    para entornos locales (.env).

    Raises:
        ValueError: Si no se encuentra ninguna configuración válida de base de datos.
        SQLAlchemyError: Si ocurre un fallo de inicialización interno en SQLAlchemy.

    Returns:
        Engine: Instancia de motor de SQLAlchemy conectada a la base de datos destino.
    """
    # Intentar primero con la URL unificada (Entorno de Nube / Render)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        try:
            logger.info('Inicializando engine mediante DATABASE_URL (Nube).')
            return create_engine(database_url)
        except SQLAlchemyError as e:
            logger.error('Error crítico al inicializar el engine con DATABASE_URL')
            raise e

    # Si no existe DATABASE_URL, proceder con la configuración por variables individuales (Local)
    REQUIRED_DB_VARS = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'DB_HOST', 'DB_PORT', 'POSTGRES_DB']
    env_vars = {var: os.getenv(var) for var in REQUIRED_DB_VARS}
    missing_var = [var for var, val in env_vars.items() if not val]
    
    if missing_var:
        error_msg = f'Faltan variables de entorno de configuración: {", ".join(missing_var)}'
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        logger.info('Inicializando engine mediante variables estructuradas (Local).')
        url = f"postgresql://{env_vars['POSTGRES_USER']}:{env_vars['POSTGRES_PASSWORD']}@{env_vars['DB_HOST']}:{env_vars['DB_PORT']}/{env_vars['POSTGRES_DB']}"
        return create_engine(url)
    
    except SQLAlchemyError as e:
        logger.error('Error crítico al inicializar el engine SQLAlchemy local')
        raise e

def subir_a_postgres(df: pd.DataFrame,nombre_tabla: str,if_exists: str = 'append') -> None:
    """Inserta un DataFrame de Pandas en una tabla específica de PostgreSQL.

    Realiza una preparación previa de los datos: resetea el índice, remueve registros 
    duplicados basados en la columna `customerid` (si está presente) y elimina espacios 
    en blanco en los nombres de las columnas para evitar errores de sintaxis en SQL.

    Args:
        df (pd.DataFrame): El conjunto de datos que se desea insertar en la base de datos.
        nombre_tabla (str): Nombre de la tabla destino en PostgreSQL.
        if_exists (str, optional): Comportamiento si la tabla ya existe en la base de datos.
            Opciones válidas: 'append' (añadir filas), 'replace' (recrear tabla) o 
            'fail' (lanzar error). Por defecto es 'append'.

    Raises:
        ValueError: Si la inicialización del motor de conexión falla por variables incompletas.
        Exception: Relanza cualquier error derivado de la inserción física en la base de datos 
            tras registrarlo en el log.

    Returns:
        None
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