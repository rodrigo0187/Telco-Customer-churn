import os
import pandas as pd
from sqlalchemy import create_engine

def cargar_datos(ruta_csv, carpeta_backup='copy_churn_csv'):
    try:
        # 1. Cargar CSV
        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        print("¡Datos cargados en memoria exitosamente!")
        
        # 2. Crear carpeta de backup si no existe
        if not os.path.exists(carpeta_backup):
            os.makedirs(carpeta_backup)
            print(f'¡Carpeta {carpeta_backup} creada!')
            
        return df

    except Exception as e:
        print(f"Error al leer archivo: {e}")
        return None

def subir_a_postgres(df, nombre_tabla):
    # Usamos los valores exactos de tu Docker Compose / .env
    url = f"postgresql://admin:admin@db:5432/churn_db"
    engine = create_engine(url)
    
    try:
        df.to_sql(nombre_tabla, engine, if_exists='replace', index=False)
        print(f"¡Cargado en Postgres en la tabla {nombre_tabla}!")
    except Exception as e:
        print(f"Error al subir a BD: {e}")

# Ejecución
if __name__ == "__main__":
    # OJO: La ruta debe coincidir con donde Docker ve el archivo
    ruta = "ingestion/Churn.csv" 
    data = cargar_datos(ruta)
    
    if data is not None:
        subir_a_postgres(data, "clientes_churn")