from src.ingestion.load_csv import cargar_csv
from src.storage.load_db import subir_a_postgres
from src.cleaning.quality_check import QualityCheck
from src.cleaning.remove_null import remove_nulls
from src.utils.normalize_text import normalize_text
from src.cleaning.remove_duplicates import remove_customer_duplicates
from src.feature_engineering.creation_features import create_features
from src.utils.saved_dataset import saved_dataset
from src.feature_engineering.encoding import encode_features

MIN_QUALITY_SCORE = 50

def main():
    print('Inicializando pipeline')
    # ingesta de datos churn    
    df = cargar_csv("data/raw/churn.csv")
    if df is None:
        print('No se puede cargar el csv')
        return
    qc_before = QualityCheck(df)
    print('Quality score Before cleaning:',qc_before.quality_score_weight())
    
    # limpieza
    df = normalize_text(df)
    df = remove_nulls(df)
    df = remove_customer_duplicates(df)
    # fin de limpieza
    
    # Inicio de trazabilidad
    # Trazabilidad de limpieza
    saved_dataset(df,'cleaned',"cleaned_churn.csv")
    
    # Feature engineering creacion
    df = create_features(df)
    # trazabilidad de feature engineering
    saved_dataset(df,'feature_engineering','fe_churn.csv')
    
    # trazabilidad del preprocessing
    df = encode_features(df)
    saved_dataset(df,'encoded','encoded_churn.csv')
    print("Feature y Encoding aplicados correctamente")
    # Fin de trazabilidad
    
    
    # Evaluando la limpieza
    qc_after_cleaning = QualityCheck(df)
    report = qc_after_cleaning.quality_report()
    score = qc_after_cleaning.quality_score_weight()
    
    print('Quality report After cleaning:',report)
    print('Quality score After cleaning:',score) 
    
    report_details = qc_after_cleaning.quality_report_details()
    print('Quality report details:',report_details)
    # Fin de evaluación
    
    # decisión de carga, en funcion de MIN_QUALITY_SCORE
    if score >= 50:
        print('Datos cargados, iniciando inserción en db')
        subir_a_postgres(df, "cliente")
        print('Pipeline finalizado correctamente')
    else:
        print(f'Dataset con mala calidad ({score}), no se inserta en la BD.')

if __name__ == "__main__":
    main()