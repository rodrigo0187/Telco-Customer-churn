import os
import re
import urllib.request
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cargar_csv(ruta_csv: str, carpeta_backup: str = 'data/backup/raw') -> pd.DataFrame:
    """Realiza la carga de un archivo CSV de forma local o es obtenida desde la nube (Google Drive/Sheets).

    Args:
        ruta_csv (str): Obtiene los datos crudos desde un csv local o desde la nube.
        carpeta_backup (str, optional): Genera una copia del archivo CSV como respaldo. por defecto se almacena en 'data/backup/raw'.

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

        if not os.path.exists(ruta_csv) and url_datos:
            logger.info("Archivo local no encontrado. Procesando origen de datos...")
            os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)
            
            # --- CASO 1: SI ES UN GOOGLE SHEET (Tu caso principal actual) ---
            if "docs.google.com/spreadsheets" in url_datos:
                logger.info("Detectado formato Google Sheets. Generando URL de exportación a CSV...")
                # Extraemos el ID
                match_id = re.search(r"/d/([a-zA-Z0-9-_]+)", url_datos)
                if not match_id:
                    raise ValueError("No se pudo extraer el ID del Google Sheet.")
                
                file_id = match_id.group(1)
                # URL oficial de Google para exportar un Sheets directamente a CSV con gid=0 (Pestaña principal)
                url_descarga_final = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid=0"
            
            # --- CASO 2: SI ES UN ARCHIVO CSV COMÚN EN DRIVE ---
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
            
            # --- CASO 3: CUALQUIER OTRA URL DIRECTA (Respaldo seguro) ---
            else:
                logger.info("URL no requiere transformación previa.")
                url_descarga_final = url_datos

            # Descarga del archivo definitivo
            logger.info(f"Descargando datos desde: {url_descarga_final}")
            req = urllib.request.Request(url_descarga_final, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(ruta_csv, 'wb') as out_file:
                out_file.write(response.read())
                
            logger.info(f"Descarga completada con éxito y guardada en: {ruta_csv}")

        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f'No se encontró el archivo: {ruta_csv}')

        # Lectura del CSV descargado
        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        logger.info(f'CSV cargado exitosamente: {len(df)} filas.')

        # Normalización estándar (Pasar todo a minúsculas y limpiar espacios)
        df.columns = df.columns.str.strip().str.lower()
        
        if 'customer_id' in df.columns:
            df = df.rename(columns={'customer_id': 'customerid'})
            
        if 'totalcharges' in df.columns:
            df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
        else:
            logger.warning(f"Advertencia: 'totalcharges' no encontrada. Columnas disponibles: {list(df.columns)}")

        # Generar Backup
        os.makedirs(carpeta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'churn_{timestamp}.csv'
        ruta_backup = os.path.join(carpeta_backup, nombre_archivo)
        df.to_csv(ruta_backup, index=False)
        logger.info(f'Backup generado: {ruta_backup}')

        return df

    except Exception as e:
        logger.exception('Error crítico al cargar o procesar el CSV')
        raise e