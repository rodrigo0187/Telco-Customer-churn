# src/pipeline.py
import os
import glob
from datetime import datetime
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
    """Orquesta el pipeline de preparación de datos para el dataset de churn.

    Este pipeline implementa un flujo de data engineering y preparación de
    datos para Machine Learning, separando claramente la capa de datos de negocio
    (almacenada en base de datos) de la capa de datos para modelos ML.

    Flujo del pipeline:
    1. Detectar de manera automatica el CSV
    1. Ingesta del dataset desde archivo CSV.
    2. Evaluación inicial de calidad de los datos.
    3. Limpieza de datos.
    4. Evaluación de calidad sobre datos limpios.
    5. Persistencia de datos limpios en base de datos (PostgreSQL).
    6. Aplicación de winsorización para tratamiento de outliers.
    7. Codificación de variables categóricas (preparación para ML).
    8. Persistencia de dataset procesado para Machine Learning.
    9. Evaluación final de calidad del dataset ML.
    10. Fase de Machine Learning: Entrenamiento y Evaluación del modelo.

    Returns:
        None
    """
    # declaración de la ruta local como constante
    RUTA_LOCAL_PATTERN = 'data/raw/*.csv'  
    
    logger.info('Pipeline_principal')
    
    logger.info("Incializando pipeline de datos")
    
    # Normalización del escaneo para evitar fallos de ruta en Docker/Render
    # Excluye archivos temporales que empiecen con 'ingesta_'
    archivos_raw = [
        f for f in glob.glob(RUTA_LOCAL_PATTERN)
        if not os.path.basename(f).startswith('ingesta_')
    ]
    
    if archivos_raw:
        ruta_archivo = max(archivos_raw, key=os.path.getmtime)
        logger.info(f'Archivo detectado localmente en {len(archivos_raw)} Procesando el mas reciente: {ruta_archivo}')
    else:
        # se descarga el archivo localmente desde la nube y se generar por defecto el nombre de ingesta_actual.csv
        timestime_ingesta = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = f'data/raw/ingesta_{timestime_ingesta}.csv'
        logger.info(f'Modo OneDrive, se generar archivo en Directorio data/raw/ {ruta_archivo}')
    
    # Ingesta
    df = cargar_csv(ruta_archivo)
    logger.info(f'Arvhivo cargado: {len(df)} filas' if df is not None else "Archivo vacío o no encontrado")
    if df is None:
        logger.error("No se puede cargar el csv")
        return
    logger.info(f'Archivo cargado con éxito {len(df)} filas.')
    
    # validador de schema, regla de negocio
    if not auditar_validar_dataset(df):
        logger.critical('El archivo actual no es compatible con el contrato de datos.')
        return
    
    qc_before = QualityCheck(df)
    logger.info(f"Quality score Before cleaning: {qc_before.quality_score_weight()}")

    # Cleaning
    df = fix_data_types(df)
    df = normalize_text(df)
    df = normalize_nulls(df)
    df = remove_duplicates_customers(df)  # Remueve nulos solo en customerid

    qc_clean = QualityCheck(df)

    # Guardado en BD solo si cumple calidad mínima
    if qc_clean.quality_score_weight() >= MIN_QUALITY_SCORE:
        saved_dataset(df, "cleaned", "cleaned_churn.csv")
        subir_a_postgres(df, "cliente")
    else:
        logger.error("¡Datos rechazados antes de BD!")
        return

    # Winsorizer
    winsorizer = Winsorizer(
        limits=(0.05, 0.05),
        exclude_cols=["customerid", "churn"]
    )

    winsorizer.fit(df)
    df = winsorizer.transform(df)

    saved_dataset(df, "winsorized", "winsorized_churn.csv")

    # 4. Encoding (solo para ML)
    df = encode_features(df)
    saved_dataset(df, "encoded", "encoded_churn.csv")

    logger.info("Preprocessing completado correctamente")

    # 5. Quality check final (dataset ML)
    qc_ml = QualityCheck(df)
    
    logger.info(f"Quality score ML dataset: {qc_ml.quality_score_weight()}")

    grid_cols = df.columns.tolist() if hasattr(df, 'columns') else []
    logger.info(f"Columnas finales: {grid_cols}")
    logger.info('Pipeline de datos finalizado con éxito')
    
    # FASE DE MACHINE LEARNING
    logger.info('Iniciando fase de Machine Learning')
    
    try:
        logger.info('Ejecución de Fase 1: Entrenamiento del modelo')
        train_model()
        
        logger.info('Ejecución de Fase 2: Evaluación y cálculo de métricas')
        evaluate_model()
        
        logger.info('Proceso de Machine Learning completado exitosamente')
        logger.info('Reportes gráficos guardados correctamente en "results/"')
        
    except Exception as e:
        # Optimización: exc_info=True guarda el reporte detallado del error en logs
        logger.error(f'Error crítico en la fase de Machine Learning: {str(e)}', exc_info=True)
        raise e


if __name__ == "__main__":
    main()