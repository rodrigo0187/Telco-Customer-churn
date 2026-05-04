import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import shutil
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def cargar_csv(ruta_csv, carpeta_backup='data/backup/raw'):
    try:
        
        # Verificar existencia del archivo
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

        # Leer CSV
        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        print(f"CSV cargado: {len(df)} filas detectadas.")
        
        # lower en columnas
        df.columns = df.columns.str.strip().str.lower()
        df = df.rename(columns={
            'customer_id':'customerid'
        })
        # cambiar el tipo de datos en la columna Total_Charges(Object) a float\
        df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
        
        # crear la carpeta backup en caso de que no existiera
        if not os.path.exists(carpeta_backup):
            os.makedirs(carpeta_backup)
            print(f'Carpeta de backup "{carpeta_backup}" lista.')
        # implementacion de buckup con el tiempo de respaldo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo= f'churn_{timestamp}.csv'
        ruta_backup = os.path.join(carpeta_backup,nombre_archivo)
        df.to_csv(ruta_backup,index=False)
        
        return df

    except Exception as e:
        print(f"Error al procesar CSV: {e}")
        return None


def subir_a_postgres(df, nombre_tabla):
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')

    url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    try:
        engine = create_engine(url)

        print("Conexion exitosa")

        # Insertar datos
        df.to_sql(nombre_tabla, engine, if_exists='append', index=False)

        print(f"Datos insertados en la tabla: {nombre_tabla}")

    except Exception as e:
        print(f"Error al subir a BD en PostgreSQL: {e}")
        raise


if __name__ == "__main__":
    # Ruta correcta dentro del contenedor
    try:
        data = cargar_csv("data/raw/churn.csv")

        if data is not None:
            print("Datos cargados, iniciando inserción en db")
            subir_a_postgres(data, "cliente")
            print("Pipeline finalizado correctamente")
            
    except FileNotFoundError as e:
        print(f'Archivo no encontrado: {e}')
        exit(1)
    except Exception as e:
        print(f'Error al generar el Pipeline {e}')
        exit(1)
    