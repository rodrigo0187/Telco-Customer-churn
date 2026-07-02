# src/pipeline.py
import os
import glob
import sys
import logging
from src.cleaning.duplicates import remove_duplicates_customers
from src.cleaning.normalize_text import normalize_text
from src.cleaning.null import normalize_nulls
from src.cleaning.quality_check import QualityCheck
from src.cleaning.types import fix_data_types
from src.feature_engineering.encoding import encode_features
from src.ingestion.load_csv import cargar_csv
from src.model.predict import evaluate_model
from src.model.preprocessing.winsorizer import Winsorizer
from src.model.train import train_model
from src.storage.load_db import subir_a_postgres
from src.utils.logging_config import get_logger
from src.utils.saved_dataset import saved_dataset
from src.utils.schema_validator import auditar_validar_dataset

MIN_QUALITY_SCORE = 70
logger = get_logger('main_app')

LOG_DIR = "results/logs"
LOG_FILE =os.path.join(LOG_DIR,"pipeline.log")
os.makedirs(LOG_DIR,exist_ok=True)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    handlers=[logging.handlers(LOG_FILE,encoding ="utf-8"),logging.StreamHandler])
logger =logging.getLogger("pipeline_ingestion")

def main():
    """Orquesta el pipeline local de preparación de datos y Machine Learning para Churn."""
    RUTA_LOCAL_PATTERN = 'data/raw/*.csv'  
    
    logger.info('=== INICIALIZANDO PIPELINE DE DATOS LOCAL/DOCKER ===')
    
    # Escaneo de archivos CSV en el volumen local mapeado
    archivos_raw = [
        f for f in glob.glob(RUTA_LOCAL_PATTERN)
        if not os.path.basename(f).startswith('ingesta_')
    ]
    
    if archivos_raw:
        # Se procesa el archivo modificado más recientemente de forma dinámica
        ruta_archivo = max(archivos_raw, key=os.path.getmtime)
        logger.info(f'Se detectaron {len(archivos_raw)} archivos en data/raw/. Procesando el más reciente: {ruta_archivo}')
    else:
        # Estrategia Fail-Fast: Si no hay archivos locales, el pipeline Dockerizado/CI-CD se detiene limpiamente informando el fallo.
        logger.critical(f'Error Crítico: No se encontraron archivos CSV para procesar en "{RUTA_LOCAL_PATTERN}". Verifique el montaje de volúmenes en Docker.')
        sys.exit(1)
    
    # Ingesta Local
    df = cargar_csv(ruta_archivo)
    
    if df is None or df.empty:
        logger.error("No se pudo proceder: El DataFrame extraído está vacío.")
        sys.exit(1)
        
    logger.info(f'Archivo cargado con éxito en memoria: {len(df)} registros.')
    
    # Validador de Schema / Reglas de negocio del contrato de datos
    if not auditar_validar_dataset(df):
        logger.critical('El archivo actual NO cumple con el contrato de datos (Schema inválido). Deteniendo pipeline.')
        sys.exit(1)
    
    # Control de Calidad Pre-Limpieza
    qc_before = QualityCheck(df)
    logger.info(f"Score de Calidad Inicial (Antes de limpieza): {qc_before.quality_score_weight()}")

    # Flujo Secuencial de Limpieza (Data Cleaning)
    df = fix_data_types(df)
    df = normalize_text(df)
    df = normalize_nulls(df)
    df = remove_duplicates_customers(df) 

    # Control de Calidad Post-Limpieza
    qc_clean = QualityCheck(df)
    score_limpio = qc_clean.quality_score_weight()
    logger.info(f"Score de Calidad Final (Post limpieza): {score_limpio}")

    # Persistencia en PostgreSQL condicionado por Umbral de Calidad Mínima
    if score_limpio >= MIN_QUALITY_SCORE:
        saved_dataset(df, "cleaned", "cleaned_churn.csv")
        
        # Carga en la base de datos PostgreSQL de Render
        logger.info("Iniciando carga de datos limpios en PostgreSQL...")
        subir_a_postgres(df, "cliente")
        logger.info("Datos persistidos con éxito en la base de datos.")
    else:
        logger.critical(f"Pipeline Detenido: Los datos limpios no superan el umbral mínimo de calidad ({score_limpio} < {MIN_QUALITY_SCORE}). Datos rechazados antes de persistencia.")
        sys.exit(1)

    # Fase de Tratamiento de Outliers (Winsorizer)
    winsorizer = Winsorizer(
        limits=(0.05, 0.05),
        exclude_cols=["customerid", "churn"]
    )
    winsorizer.fit(df)
    df = winsorizer.transform(df)
    saved_dataset(df, "winsorized", "winsorized_churn.csv")

    # Codificación de Variables Categóricas (Preparación estricta para ML)
    df = encode_features(df)
    saved_dataset(df, "encoded", "encoded_churn.csv")
    logger.info("Fase de Preprocessing y Feature Engineering finalizada de manera exitosa.")

    # Evaluación Final de Datos destinados a ML
    qc_ml = QualityCheck(df)
    logger.info(f"Score de Calidad Dataset Final (ML): {qc_ml.quality_score_weight()}")
    
    grid_cols = df.columns.tolist() if hasattr(df, 'columns') else []
    logger.info(f"Columnas finales inyectadas al modelo: {grid_cols}")
    logger.info('=== PIPELINE DE DATOS FINALIZADO CON ÉXITO ===')
    
    # FASE DE MACHINE LEARNING (Entrenamiento & Inferencia de Métricas)
    logger.info('Iniciando fase ejecutiva de Machine Learning...')
    try:
        logger.info('Ejecutando Fase 1: Entrenamiento del Modelo de Clasificación (Train)')
        train_model()
        
        logger.info('Ejecutando Fase 2: Evaluación General y Exportación de Métricas')
        evaluate_model()
        
        logger.info('Ciclo de Machine Learning finalizado exitosamente. Artefactos y reportes guardados en "results/"')
        
    except Exception as e:
        logger.error(f'Error crítico no controlado en la fase de Machine Learning: {str(e)}', exc_info=True)
        raise e

if __name__ == "__main__":
    main()