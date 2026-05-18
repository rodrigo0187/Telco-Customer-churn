from src.ingestion.load_csv import cargar_csv
from src.storage.load_db import subir_a_postgres
from src.cleaning.quality_check import QualityCheck
from src.cleaning.remove_null import remove_nulls
from src.utils.normalize_text import normalize_text
from src.cleaning.remove_duplicates import remove_customer_duplicates
from src.utils.saved_dataset import saved_dataset
from src.feature_engineering.encoding import encode_features
from src.model.preprocessing.winsorizer import Winsorizer

MIN_QUALITY_SCORE = 50


def main():
    """
    Orquesta el pipeline de preparación de datos para el dataset de churn.

    Este pipeline implementa un flujo de data engineering y preparación de
    datos para Machine Learning, separando claramente la capa de datos de negocio
    (almacenada en base de datos) de la capa de datos para modelos ML.

    Flujo del pipeline:

    1. Ingesta del dataset desde archivo CSV.
    2. Evaluación inicial de calidad de los datos.
    3. Limpieza de datos:
        - Normalización de texto
        - Eliminación de valores nulos
        - Eliminación de duplicados de clientes
    4. Evaluación de calidad sobre datos limpios.
    5. Persistencia de datos limpios en base de datos (PostgreSQL).
    6. Aplicación de winsorización para tratamiento de outliers.
    7. Codificación de variables categóricas (preparación para ML).
    8. Persistencia de dataset procesado para Machine Learning.
    9. Evaluación final de calidad del dataset ML.

    Importante:
    - La base de datos "cliente" almacena únicamente datos limpios y originales.
    - El dataset codificado es utilizado exclusivamente para Machine Learning.
    - Se mantiene separación entre capa de negocio y capa de modelado.

    Returns:
        None
    """

    print("Inicializando pipeline")

    # 1. Ingesta
    df = cargar_csv("data/raw/churn.csv")

    if df is None:
        print("No se puede cargar el csv")
        return

    qc_before = QualityCheck(df)
    print("Quality score Before cleaning:", qc_before.quality_score_weight())

    # 2. Cleaning
    df = normalize_text(df)
    df = remove_nulls(df)
    df = remove_customer_duplicates(df)

    qc_clean = QualityCheck(df)

    # Guardado en BD solo si cumple calidad mínima
    if qc_clean.quality_score_weight() >= MIN_QUALITY_SCORE:

        saved_dataset(df, "cleaned", "cleaned_churn.csv")
        subir_a_postgres(df, "cliente")

    else:
        print("Datos rechazados antes de BD")
        return

    # 3. Winsorizer
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

    print("Preprocessing completado correctamente")

    # 5. Quality check final (dataset ML)
    qc_ml = QualityCheck(df)
    print("Quality score ML dataset:", qc_ml.quality_score_weight())

    print("Columnas finales:")
    print(df.columns.tolist())


if __name__ == "__main__":
    main()