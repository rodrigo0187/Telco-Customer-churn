# load_csv.py
import os
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cargar_csv(ruta_csv: str, carpeta_backup: str = 'data/backup/raw') -> pd.DataFrame:
    """Realiza la carga de un archivo CSV local de forma robusta y genera un respaldo.

    Args:
        ruta_csv (str): Ruta al archivo CSV local.
        carpeta_backup (str, optional): Directorio donde se almacenará la copia de respaldo.
                                        Por defecto es 'data/backup/raw'.

    Raises:
        FileNotFoundError: Si no se encuentra el archivo en la ruta especificada.
        Exception: Captura errores genéricos en la lectura o procesamiento del dataframe.

    Returns:
        pd.DataFrame: DataFrame de Pandas cargado y con pre-normalización básica de columnas.
    """    
    try:
        logger.info(f"Iniciando carga de archivo local: {ruta_csv}")

        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f'Error: El archivo requerido no existe en el contenedor/volumen: {ruta_csv}')

        # Lectura segura del CSV local
        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        logger.info(f'CSV cargado exitosamente. Registros iniciales: {len(df)} filas.')

        if df.empty:
            logger.warning(f"El archivo {ruta_csv} está vacío.")
            return df

        # Normalización estándar (Pasar todo a minúsculas y limpiar espacios en blanco)
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapeo de columnas críticas bajo reglas de negocio uniformes
        if 'customer_id' in df.columns:
            df = df.rename(columns={'customer_id': 'customerid'})
            logger.info("Columna 'customer_id' normalizada a 'customerid'.")
            
        # Validación crítica para Telco Churn: Asegurar que TotalCharges sea numérico
        if 'totalcharges' in df.columns:
            # errors='coerce' transformará los strings vacíos " " (muy comunes en este dataset) en valores NaN
            df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
            logger.info("Conversión numérica aplicada a 'totalcharges'.")
        else:
            logger.warning(f"Advertencia: Columna 'totalcharges' no encontrada. Columnas actuales: {list(df.columns)}")

        # Generar histórico de Backups locales de auditoría
        os.makedirs(carpeta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'churn_{timestamp}.csv'
        ruta_backup = os.path.join(carpeta_backup, nombre_archivo)
        
        df.to_csv(ruta_backup, index=False)
        logger.info(f'Backup de auditoría local generado en: {ruta_backup}')

        return df

    except FileNotFoundError as fnf:
        logger.error(str(fnf))
        raise fnf
    except Exception as e:
        logger.exception('Error crítico irreversible durante la carga o parsing del CSV local')
        raise e