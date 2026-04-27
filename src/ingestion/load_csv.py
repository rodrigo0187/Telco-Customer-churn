import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

ruta_csv = 'data/raw/churn.csv'
def cargar_y_limpiar_csv(ruta_csv, carpeta_backup='copy_churn_csv'):
    try:
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        print(f"CSV cargado: {len(df)} filas detectadas.")

        # Limpieza clave
        df.columns = df.columns.str.strip()
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce')

        # Manejo de nulos
        df = df.dropna(subset=['TotalCharges'])

        # Crear backup folder
        if not os.path.exists(carpeta_backup):
            os.makedirs(carpeta_backup)
            print(f'Carpeta de backup "{carpeta_backup}" lista.')

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
        df.to_sql(nombre_tabla, engine, if_exists='append', index=False)
        print(f"Datos insertados en la tabla: {nombre_tabla}")
    except Exception as e:
        print(f"Error en BD: {e}")


if __name__ == "__main__":
    data = cargar_y_limpiar_csv("data/churn.csv")

    if data is not None:
        subir_a_postgres(data, "cliente")