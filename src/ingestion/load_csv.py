import os
import re
import urllib.request
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cargar_csv(ruta_csv: str, carpeta_backup: str = 'data/backup/raw') -> pd.DataFrame:
    """Carga un archivo desde una URL (CSV o Google Sheets) y lo normaliza."""
    try:
        url_datos = os.environ.get('DATA_SOURCE_URL')

        if not os.path.exists(ruta_csv) and url_datos:
            logger.info("Archivo local no encontrado. Procesando origen desde Google Drive...")
            os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)
            
            # detecta si el archivo es hoja de estilo excel
            if "docs.google.com/spreadsheets" in url_datos:
                logger.info("Detectado formato Google Sheets. Generando URL de exportación a CSV...")
                # Extraemos el ID
                match_id = re.search(r"/d/([a-zA-Z0-9-_]+)", url_datos)
                if not match_id:
                    raise ValueError("No se pudo extraer el ID del Google Sheet.")
                
                file_id = match_id.group(1)
                # URL oficial de Google para exportar un Sheets directamente a CSV
                url_descarga_final = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
            
            # --- SI ES UN ARCHIVO CSV COMÚN EN DRIVE ---
            else:
                if "id=" in url_datos:
                    file_id = url_datos.split("id=")[-1].split("&")[0]
                else:
                    raise ValueError("No se pudo extraer el ID de Google Drive.")
                url_descarga_final = f"https://docs.google.com/uc?export=download&id={file_id}"

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