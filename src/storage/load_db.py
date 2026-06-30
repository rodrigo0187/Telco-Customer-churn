# load_db.py
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
    """
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Corrección crítica para compatibilidad de SQLAlchemy en entornos de nube
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        try:
            logger.info('Inicializando engine mediante DATABASE_URL (Nube).')
            return create_engine(database_url)
        except SQLAlchemyError as e:
            logger.error('Error crítico al inicializar el engine con DATABASE_URL')
            raise e

    # Configuración por variables individuales (Fallback Local)
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

def subir_a_postgres(df: pd.DataFrame, nombre_tabla: str, if_exists: str = 'append') -> None:
    """Inserta un DataFrame de Pandas en una tabla específica de PostgreSQL de manera optimizada.

    Realiza una preparación previa de los datos y ejecuta una carga por lotes (chunksize)
    para evitar fallos por latencia de red y mejorar el rendimiento de inserción.
    """
    try:
        engine = get_engine()
        logger.info('Conexión con el motor de base de datos exitosa.')

        df = df.reset_index(drop=True)

        # Eliminar duplicados si existe customerid
        if 'customerid' in df.columns:
            df = df.drop_duplicates(subset=['customerid'])
            logger.info("Duplicados removidos basados en 'customerid'.")

        # Limpiar nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]

        # --- OPTIMIZACIÓN CRÍTICA PARA RENDIMIENTO EN RENDER ---
        # 1. chunksize=1000: Envía los 7,000 registros en bloques de 1,000 en 1,000.
        #    Previene que el socket de red se sature y que Render cancele la petición por timeout.
        # 2. method='multi': Pasa de hacer un "INSERT" fila por fila a un "INSERT múltiple" masivo por bloque.
        logger.info(f"Iniciando la inserción masiva en la tabla '{nombre_tabla}'...")
        
        df.to_sql(
            name=nombre_tabla,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=1000,
            method='multi'
        )

        logger.info(f'¡Éxito! Todos los datos han sido insertados en la tabla: {nombre_tabla}')

    except Exception as e:
        logger.error(f'Error crítico durante el proceso de carga en PostgreSQL: {e}')
        raise