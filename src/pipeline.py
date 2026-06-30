# src/pipeline.py
import os
import glob
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


def main():
    """Orquesta el pipeline local de preparación de datos para el dataset de churn.

    Flujo del pipeline:
    1. Ingesta del dataset desde un archivo CSV local controlado.
    2. Validación de esquema (contrato de datos).
    3. Evaluación inicial y limpieza profunda de datos.
    4. Persistencia de datos limpios en base de datos (PostgreSQL en Render).
    5. Transformaciones avanzadas para ML (Winsorización y Encoding).
    6. Fase de Machine Learning: Entrenamiento y Evaluación del modelo.
    """
    # Constante para buscar archivos crudos válidos en el repositorio
    RUTA_LOCAL_PATTERN = 'data/raw/*.csv'  
    
    logger.info("")
    logger.info("Inicializando pipeline de datos (MODO LOCAL)")
    logger.info("")
    
    # 1. Escaneo del directorio local omitiendo backups o archivos de ingestas viejas
    archivos_raw = [
        f for f in glob.glob(RUTA_LOCAL_PATTERN)
        if not os.path.basename(f).startswith('ingesta_')
    ]
    
    if archivos_raw:
        # Tomamos el archivo modificado más recientemente en la carpeta data/raw/
        ruta_archivo = max(archivos_raw, key=os.path.getmtime)
        logger.info(f'Archivo detectado para procesamiento: {ruta_archivo}')
    else:
        # Fallback explícito: si la carpeta está vacía, buscamos el nombre estándar esperado
        ruta_archivo = 'data/raw/churn.csv'
        logger.warning(f'No se detectaron archivos dinámicos. Usando ruta por defecto: {ruta_archivo}')

    # --- FASE DE INGESTA ---
    try:
        df = cargar_csv(ruta_archivo, sep=",")
    except Exception as e:
        logger.critical(f"Error fatal durante la invocación de cargar_csv: {e}")
        return

    if df is None or df.empty:
        logger.error("El DataFrame devuelto está vacío. Deteniendo el pipeline.")
        return
        
    logger.info(f'Dataset cargado exitosamente. Dimensiones iniciales: {df.shape[0]} filas, {df.shape[1]} columnas.')
    
    # --- FASE DE VALIDACIÓN Y CALIDAD INICIAL ---
    if not auditar_validar_dataset(df):
        logger.critical('CRÍTICO: El archivo no es compatible con el contrato de datos esperado.')
        return
    
    qc_before = QualityCheck(df)
    logger.info(f"Quality score inicial (Antes de limpieza): {qc_before.quality_score_weight()}")

    # --- FASE DE LIMPIEZA (CLEANING) ---
    logger.info("Aplicando transformaciones de limpieza...")
    df = fix_data_types(df)
    df = normalize_text(df)
    df = normalize_nulls(df)
    df = remove_duplicates_customers(df)  

    qc_clean = QualityCheck(df)
    score_limpio = qc_clean.quality_score_weight()
    logger.info(f"Quality score obtenido tras la limpieza: {score_limpio}")

    # --- PERSISTENCIA EN BASE DE DATOS ---
    if score_limpio >= MIN_QUALITY_SCORE:
        logger.info(f"Calidad aceptada (>= {MIN_QUALITY_SCORE}). Procediendo al resguardo de datos...")
        saved_dataset(df, "cleaned", "cleaned_churn.csv")
        
        # Carga en la base de datos PostgreSQL de Render
        logger.info("Iniciando carga de datos limpios en PostgreSQL...")
        subir_a_postgres(df, "cliente")
        logger.info("Datos persistidos con éxito en la base de datos.")
    else:
        logger.error(f"¡Datos rechazados! Score de calidad ({score_limpio}) inferior al mínimo requerido.")
        return

    # --- PREPARACIÓN AVANZADA PARA MACHINE LEARNING ---
    logger.info("Iniciando ingeniería de características (Feature Engineering)...")
    
    # Tratamiento de Outliers mediante Winsorización
    winsorizer = Winsorizer(
        limits=(0.05, 0.05),
        exclude_cols=["customerid", "churn"]
    )
    winsorizer.fit(df)
    df = winsorizer.transform(df)
    saved_dataset(df, "winsorized", "winsorized_churn.csv")

    # Codificación de variables cualitativas (Categorical Encoding)
    df = encode_features(df)
    saved_dataset(df, "encoded", "encoded_churn.csv")

    # Verificación final de salud del set de datos estructurado para el modelo
    qc_ml = QualityCheck(df)
    logger.info(f"Quality score final del dataset de Machine Learning: {qc_ml.quality_score_weight()}")
    
    grid_cols = df.columns.tolist() if hasattr(df, 'columns') else []
    logger.info(f"Estructura de características final lista ({len(grid_cols)} columnas).")
    logger.info('Pipeline de datos finalizado con éxito.')
    
    # --- FASE DE MACHINE LEARNING (ENTRENAMIENTO Y EVALUACIÓN) ---
    logger.info('')
    logger.info('Iniciando ejecución de modelos predictivos')
    logger.info('')
    
    try:
        logger.info('Ejecutando Fase 1: Entrenamiento del modelo (train_model)')
        train_model()
        
        logger.info('Ejecutando Fase 2: Evaluación del rendimiento (evaluate_model)')
        evaluate_model()
        
        logger.info('Proceso de Machine Learning completado de forma exitosa.')
        logger.info('Métricas guardadas y reportes gráficos exportados a "results/"')
        
    except Exception as e:
        logger.error(f'Error crítico en la fase de Machine Learning: {str(e)}', exc_info=True)
        raise e


if __name__ == "__main__":
    main()