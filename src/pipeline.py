from src.ingestion.load_csv import cargar_csv
from src.storage.load_db import subir_a_postgres
from src.cleaning.quality_check import QualityCheck

def main():
    print('Inicializando pipeline')
    df = cargar_csv("data/raw/churn.csv")
    
    if df is not None:
        qc = QualityCheck(df)
        report = qc.quality_report()
        score =qc.quality_score_weight()
        print('Quality report:',report)
        print('Quality score:',score)
      
        report_details = qc.quality_report_details()
        print('Quality report details:',report_details)
        
        if score >= 50:
            print('Datos cargados, iniciando inserción en db')
            subir_a_postgres(df, "cliente")
            print('Pipeline finalizado correctamente')
        else:
            print('Dataset con mala calidad, no se inserta en la BD.')
    else:
        print('No se pudo cargar el CSV')

if __name__ == "__main__":
    main()