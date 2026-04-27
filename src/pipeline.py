from src.ingestion.load_csv import cargar_y_limpiar_csv
from src.storage.load_db import subir_a_postgres

def main():
    print('Inicializando pipeline')
    df = cargar_y_limpiar_csv("data/raw/churn.csv")
    
    if df is not None:
        print('Datos cargados, iniciando inserción en db')
        subir_a_postgres(df, "cliente")
        print('Pipeline finalizado correctamente')
    else:
        print('No se pudo cargar el CVS')

if __name__ == "__main__":
    main()