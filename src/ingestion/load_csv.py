# load_csv.py
import os
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cargar_csv(ruta_csv: str, carpeta_backup: str = 'data/backup/raw', sep: str = ',') -> pd.DataFrame:
    """Realiza la carga de un archivo CSV de forma estrictamente local,
    aplicando normalización de columnas, contratos de datos y un backup con timestamp.
    """    
    try:
        # --- FASE 1: VALIDACIÓN Y LECTURA LOCAL ---
        if not os.path.exists(ruta_csv):
            logger.critical(f"Archivo base no encontrado en la ruta especificada: {ruta_csv}")
            raise FileNotFoundError(f"No se encontró el archivo local requerido en: {ruta_csv}")
            
        logger.info(f"Cargando dataset local desde: {ruta_csv}")
        # Leemos el archivo local directamente desde el disco
        df = pd.read_csv(ruta_csv, low_memory=False, sep=sep)
        logger.info(f"CSV cargado exitosamente. Total registros iniciales: {len(df)} filas.")

        # --- FASE 2: CONTRATO Y NORMALIZACIÓN DE DATOS ---
        # Convertimos columnas a minúsculas y eliminamos espacios en blanco
        df.columns = df.columns.str.strip().str.lower()
        
        # Estandarización de la llave primaria del cliente
        if 'customer_id' in df.columns:
            df = df.rename(columns={'customer_id': 'customerid'})
            logger.info("Columna 'customer_id' normalizada a 'customerid'.")
            
        # Validación crítica para Telco Churn: Asegurar que TotalCharges sea numérico
        if 'totalcharges' in df.columns:
            # errors='coerce' transformará los strings vacíos " " (muy comunes en este dataset) en valores NaN
            df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
            logger.info("Conversión numérica aplicada a 'totalcharges'.")
        else:
            logger.warning(f"Advertencia: 'totalcharges' no encontrada. Columnas disponibles: {list(df.columns)}")

        # --- FASE 3: GENERACIÓN DE BACKUP HISTÓRICO ---
        os.makedirs(carpeta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'churn_{timestamp}.csv'
        ruta_backup = os.path.join(carpeta_backup, nombre_archivo)
        
        # Guardamos una copia exacta de cómo entra el archivo normalizado al pipeline
        df.to_csv(ruta_backup, index=False, sep=sep)
        logger.info(f'Backup histórico generado con éxito en: {ruta_backup}')

        return df

    except Exception as e:
        logger.exception('Error crítico en el flujo de ingesta de datos local')
        raise e