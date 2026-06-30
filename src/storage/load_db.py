<<<<<<< HEAD
# load_db.py
=======
>>>>>>> linea-local-funcional
import os
import pandas as pd
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
logger = logging.getLogger(__name__)

def get_engine():
    """Genera un motor (engine) de conexión para PostgreSQL.
    
    Soporta de manera híbrida la conexión mediante una URI directa (DATABASE_URL)
    ideal para entornos de nube como Render, o mediante variables individuales para Local/Docker.
    """
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Corrección de protocolo requerida por SQLAlchemy para esquemas postgres:// heredados de Render
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        try:
            logger.info('Inicializando engine mediante DATABASE_URL (Modo Nube/Render).')
            return create_engine(database_url)
        except SQLAlchemyError as e:
            logger.error('Error crítico al inicializar el engine con DATABASE_URL')
            raise e

    # Configuración por variables individuales (Local / Docker Compose)
    REQUIRED_DB_VARS = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'DB_HOST', 'DB_PORT', 'POSTGRES_DB']
    env_vars = {var: os.getenv(var) for var in REQUIRED_DB_VARS}
    missing_vars = [var for var, val in env_vars.items() if not val]
    
    if missing_vars:
        error_msg = f'Faltan variables de entorno para configurar la BD local: {", ".join(missing_vars)}'
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        logger.info('Inicializando engine mediante variables estructuradas individuales (Modo Local/Docker).')
        url = f"postgresql://{env_vars['POSTGRES_USER']}:{env_vars['POSTGRES_PASSWORD']}@{env_vars['DB_HOST']}:{env_vars['DB_PORT']}/{env_vars['POSTGRES_DB']}"
        return create_engine(url)
    except SQLAlchemyError as e:
        logger.error('Error crítico al inicializar el engine SQLAlchemy local')
        raise e

def subir_a_postgres(df: pd.DataFrame, nombre_tabla: str, if_exists: str = 'append') -> None:
    """Inserta un DataFrame de Pandas en una tabla específica de PostgreSQL."""
    if df is None or df.empty:
        logger.warning("El DataFrame enviado a la base de datos está vacío. Cancelando inserción.")
        return

    try:
        engine = get_engine()
        logger.info('Conexión con el servidor PostgreSQL establecida con éxito.')

        df_to_insert = df.reset_index(drop=True)

        # Eliminar duplicados operacionales basados en llave de negocio (si aplica)
        if 'customerid' in df_to_insert.columns:
            total_antes = len(df_to_insert)
            df_to_insert = df_to_insert.drop_duplicates(subset=['customerid'])
            total_despues = len(df_to_insert)
            if total_antes > total_despues:
                logger.info(f"Se filtraron {total_antes - total_despues} filas duplicadas por 'customerid' antes de subir a BD.")

        # Inserción física en la Base de Datos
        df_to_insert.to_sql(nombre_tabla, engine, if_exists=if_exists, index=False)
        logger.info(f'Éxito: {len(df_to_insert)} registros guardados en la tabla "{nombre_tabla}".')

    except Exception as e:
        logger.error(f'Error de escritura en PostgreSQL en la tabla "{nombre_tabla}": {str(e)}')
        raise