import os
import re
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cargar_csv(ruta_csv: str, carpeta_backup: str = 'data/backup/raw', sep: str = ',') -> pd.DataFrame:
    """Realiza la carga de un archivo CSV de forma local o es obtenida desde la nube (OneDrive/Google/Directo).

    Args:
        ruta_csv (str): Destino temporal local donde se guardará o leerá el csv.
        carpeta_backup (str, optional): Genera una copia del archivo CSV como respaldo. por defecto se almacena en 'data/backup/raw'.
        sep (str, optional): Delimitador del archivo CSV. Por defecto es ','.

    Raises:
        ValueError: Si no se puede extraer el ID del archivo de Google Drive/Sheets.
        FileNotFoundError: Si no se encuentra el archivo en la ruta específica después de la descarga.
        Exception: Genera un error genérico al cargar o procesar el csv.

    Returns:
        pd.DataFrame: Devuelve el DataFrame obtenido desde la URL o local.
    """    
    try:
        url_datos = os.environ.get('DATA_SOURCE_URL')
        url_descarga_final = None
        df = None

        # --- FASE 1: PROCESAMIENTO E INGESTA ---
        if not os.path.exists(ruta_csv) and url_datos:
            logger.info("Archivo local no encontrado. Procesando origen de datos...")
            os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)
            
            # Caso A: Estructura interna de Google Sheets
            if "docs.google.com/spreadsheets" in url_datos:
                logger.info("Detectado formato Google Sheets. Generando URL de exportación a CSV...")
                match_id = re.search(r"/d/([a-zA-Z0-9-_]+)", url_datos)
                if not match_id:
                    raise ValueError("No se pudo extraer el ID del Google Sheet.")
                file_id = match_id.group(1)
                url_descarga_final = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid=0"
            
            # Caso B: Archivo común en Google Drive
            elif "drive.google.com" in url_datos or "id=" in url_datos:
                logger.info("Detectado archivo común en Google Drive...")
                if "id=" in url_datos:
                    file_id = url_datos.split("id=")[-1].split("&")[0]
                else:
                    match_id = re.search(r"/d/([a-zA-Z0-9-_]+)", url_datos)
                    file_id = match_id.group(1) if match_id else None
                
                if not file_id:
                    raise ValueError("No se pudo extraer el ID de Google Drive.")
                url_descarga_final = f"https://docs.google.com/uc?export=download&id={file_id}"
            
            # Caso C: OneDrive o Enlaces Directos de Descarga Externa
            else:
                logger.info("URL directa u origen OneDrive detectado.")
                url_descarga_final = url_datos

            logger.info(f"Conectando y leyendo directamente desde la fuente remota...")
            
            # Definimos cabeceras de navegador para evitar bloqueos por Agentes Automatizados
            storage_options = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            # Pandas lee el flujo directamente desde internet de forma segura
            df = pd.read_csv(url_descarga_final, low_memory=False, sep=sep, storage_options=storage_options)
            
            # Guardamos localmente el dataset limpio para futuras lecturas rápidas sin llamadas a red
            df.to_csv(ruta_csv, index=False, sep=sep)
            logger.info(f"Descarga e inicialización completada con éxito en: {ruta_csv}")

        # --- FASE 2: LECTURA LOCAL (Si ya fue descargado previamente) ---
        if df is None:
            if not os.path.exists(ruta_csv):
                raise FileNotFoundError(f'No se encontró el archivo local ni remoto válido: {ruta_csv}')
            df = pd.read_csv(ruta_csv, low_memory=False, sep=sep)
            logger.info(f'CSV cargado exitosamente desde almacenamiento local: {len(df)} filas.')

        # --- FASE 3: TRANSFORMACIONES Y CONTRATO DE DATOS ---
        # Normalización estándar de columnas
        df.columns = df.columns.str.strip().str.lower()
        
        if 'customer_id' in df.columns:
            df = df.rename(columns={'customer_id': 'customerid'})
            
        if 'totalcharges' in df.columns:
            df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
        else:
            logger.warning(f"Advertencia: 'totalcharges' no encontrada. Columnas disponibles: {list(df.columns)}")

        # --- FASE 4: RESPALDO / BACKUP ---
        os.makedirs(carpeta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'churn_{timestamp}.csv'
        ruta_backup = os.path.join(carpeta_backup, nombre_archivo)
        df.to_csv(ruta_backup, index=False)
        logger.info(f'Backup histórico generado con éxito: {ruta_backup}')

        return df

    except Exception as e:
        logger.exception('Error crítico en el módulo de ingesta al procesar el origen CSV')
        raise e