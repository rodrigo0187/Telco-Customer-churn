# load_csv
import os
import re
import pandas as pd
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cargar_csv(ruta_csv: str, carpeta_backup: str = 'data/backup/raw', sep: str = ',') -> pd.DataFrame:
    """Realiza la carga de un archivo CSV de forma local o remota (OneDrive/Google Docs) 
    utilizando lectura directa por flujo de Pandas y validación de cabeceras HTML.
    """    
    try:
        url_datos = os.environ.get('DATA_SOURCE_URL')
        url_descarga_final = None
        df = None

        # --- FASE 1: DETERMINAR Y VALIDAR LA URL ---
        if not os.path.exists(ruta_csv) and url_datos:
            logger.info("Archivo local no encontrado. Procesando origen de datos remoto...")
            os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)
            
            # Caso A: Google Sheets
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
            
            # Caso C: OneDrive o Enlaces Directos
            else:
                logger.info("URL directa o enlace de OneDrive detectado.")
                url_descarga_final = url_datos

            logger.info(f"Validando respuesta del servidor remoto...")
            
            # Cabeceras simulando un navegador real para evitar bloqueos
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            # Petición de prueba para interceptar errores de formato web
            respuesta_test = requests.get(url_descarga_final, headers=headers, timeout=15)
            contenido_inicial = respuesta_test.text[:500].strip().lower()
            
            # INTERCEPCIÓN CRÍTICA: Si empieza con etiquetas HTML, el enlace está devolviendo una página web, no un CSV
            if contenido_inicial.startswith("<!doctype html") or "<html" in contenido_inicial:
                logger.critical("=======================================================================")
                logger.critical("¡ERROR DE ORIGEN! El enlace NO está devolviendo un archivo CSV.")
                logger.critical("El servidor respondió con una página HTML. Muestra del contenido recibido:")
                logger.critical(f"\n{respuesta_test.text[:400]}")
                logger.critical("=======================================================================")
                raise ValueError("La URL configurada devuelve una interfaz web (HTML) en lugar de datos planos CSV.")

            # Si pasa la validación, dejamos que Pandas procese los datos limpios
            logger.info("Formato de respuesta inicial validado. Cargando datos en Pandas...")
            storage_options = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            df = pd.read_csv(url_descarga_final, low_memory=False, sep=sep, storage_options=storage_options)
            
            # Guardamos localmente el acierto
            df.to_csv(ruta_csv, index=False, sep=sep)
            logger.info(f"Descarga exitosa. Guardado temporal en: {ruta_csv}")

        # --- FASE 2: LECTURA LOCAL DE RESPALDO ---
        if df is None:
            if not os.path.exists(ruta_csv):
                raise FileNotFoundError(f'No se encontró el archivo local ni remoto válido: {ruta_csv}')
            df = pd.read_csv(ruta_csv, low_memory=False, sep=sep)
            logger.info(f'CSV cargado exitosamente desde disco: {len(df)} filas.')

        # --- FASE 3: CONTRATO Y NORMALIZACIÓN DE DATOS ---
        df.columns = df.columns.str.strip().str.lower()
        
        if 'customer_id' in df.columns:
            df = df.rename(columns={'customer_id': 'customerid'})
            
        if 'totalcharges' in df.columns:
            df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
        else:
            logger.warning(f"Advertencia: 'totalcharges' no encontrada. Columnas disponibles: {list(df.columns)}")

        # --- FASE 4: BACKUP ---
        os.makedirs(carpeta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'churn_{timestamp}.csv'
        ruta_backup = os.path.join(carpeta_backup, nombre_archivo)
        df.to_csv(ruta_backup, index=False)
        logger.info(f'Backup generado: {ruta_backup}')

        return df

    except Exception as e:
        logger.exception('Error crítico en el flujo de ingesta de datos')
        raise e