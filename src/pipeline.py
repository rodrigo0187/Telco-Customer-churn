from src.ingestion.load_csv import cargar_csv
from src.storage.load_db import subir_a_postgres
from src.cleaning.quality_check import QualityCheck
from src.cleaning.remove_null import remove_nulls
from src.utils.normalize_text import normalize_text
from src.cleaning.remove_duplicates import remove_customer_duplicates
# from src.feature_engineering.creation_features import create_features
from src.utils.saved_dataset import saved_dataset
from src.feature_engineering.encoding import encode_features
# from src.feature_engineering.handle_nulls import handle_nulls_post_fe
from src.model.preprocessing import Winsorizer

MIN_QUALITY_SCORE = 50

def main():
    """
    Orquesta el pipeline de preparación de datos para el dataset de churn.

    El flujo ejecuta las siguientes etapas:

    1. Ingesta del dataset desde archivo CSV.
    2. Evaluación inicial de calidad del dataset.
    3. Limpieza de datos:
        - Normalización de texto
        - Eliminación de valores nulos
        - Eliminación de duplicados de clientes
    4. Persistencia del dataset limpio.
    5. Aplicación de winsorización para tratamiento de outliers.
    6. Persistencia del dataset winsorizado.
    7. Codificación de variables categóricas.
    8. Persistencia del dataset codificado.
    9. Evaluación final de calidad del dataset.
    10. Decisión de carga en base de datos según score de calidad.

    El objetivo del pipeline es generar un dataset consistente,
    limpio y preparado para ser utilizado en modelos de Machine Learning.

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

    saved_dataset(df, "cleaned", "cleaned_churn.csv")

    # 3. Feature Engineering (opcional)
    # df = create_features(df)

    # 4. Winsorizer (ANTES de encoding es más coherente conceptualmente)
    winsorizer = Winsorizer(
        limits=(0.05, 0.05),
        exclude_cols=["customerid", "churn"]
    )
    df = winsorizer.transform(df)

    saved_dataset(df, "winsorized", "winsorized_churn.csv")

    # 5. Encoding
    df = encode_features(df)

    saved_dataset(df, "encoded", "encoded_churn.csv")

    print("Preprocessing completado correctamente")

    # 6. Quality Check final
    qc_after = QualityCheck(df)

    report = qc_after.quality_report()
    score = qc_after.quality_score_weight()

    print("Quality report After cleaning:", report)
    print("Quality score After cleaning:", score)

    print("Columnas finales:")
    print(df.columns.tolist())

    # 7. Decisión de carga
    if score >= 70:
        print("Datos cargados en BD")
        subir_a_postgres(df, "cliente")
    else:
        print(f"Dataset con mala calidad ({score}), no se inserta en BD.")
        
if __name__ == "__main__":
    main()