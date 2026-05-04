from src.ingestion.load_csv import cargar_csv
from src.storage.load_db import subir_a_postgres
from src.cleaning.quality_check import QualityCheck
from src.cleaning.remove_null import remove_nulls
from src.utils.normalize_text import normalize_text
from src.cleaning.remove_duplicates import remove_customer_duplicates
from feature_engineering.creation_features import create_features
from src.utils.saved_dataset import saved_dataset

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
    # Trazabilidad de limpieza
    saved_dataset(df,'cleaned',"cleaned_churn.csv")
    
    # feature engineering creacion
    df = create_features(df)
    # trazabilidad de feature engineering
    saved_dataset(df,'feature_engineering','fe_churn.csv')
    
    print("feature creadas correctamente")
    
    # evaluando la limpieza
    qc_after = QualityCheck(df)
    report = qc_after.quality_report()
    score = qc_after.quality_score_weight()
    
    print('Quality report After cleaning:',report)
    print('Quality score After cleaning:',score) 
    
    report_details = qc_after.quality_report_details()
    print('Quality report details:',report_details)
    
    # decisión de carga, en funcion de MIN_QUALITY_SCORE
    if score >= 50:
        print('Datos cargados, iniciando inserción en db')
        subir_a_postgres(df, "cliente")
        print('Pipeline finalizado correctamente')
    else:
        print(f'Dataset con mala calidad ({score}), no se inserta en la BD.')

if __name__ == "__main__":
    main()