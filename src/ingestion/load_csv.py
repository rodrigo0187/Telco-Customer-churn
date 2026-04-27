import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def cargar_y_limpiar_csv(ruta_csv, carpeta_backup='copy_churn_csv'):
    try:
        # Verificar existencia del archivo
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

        # Leer CSV
        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        print(f"CSV cargado: {len(df)} filas detectadas.")

        # ==============================
        # 🔹 NORMALIZACIÓN DE COLUMNAS
        # ==============================
        df.columns = df.columns.str.strip().str.lower()

        # Renombrar columnas para coincidir con PostgreSQL
        df = df.rename(columns={
            'customerid': 'customer_id'
        })

        # ==============================
        # 🔹 VALIDACIONES CLAVE
        # ==============================
        df = df.dropna(subset=["customer_id"])
        df = df.drop_duplicates(subset=["customer_id"])

        # ==============================
        # 🔹 CONVERSIÓN DE TIPOS
        # ==============================
        df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
        df['monthlycharges'] = pd.to_numeric(df['monthlycharges'], errors='coerce')

        # Eliminar nulos en columnas críticas
        df = df.dropna(subset=['totalcharges'])

        # ==============================
        # 🔹 BACKUP (opcional)
        # ==============================
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

        print("Conexion exitosa")

        # Insertar datos
        df.to_sql(nombre_tabla, engine, if_exists='append', index=False)

        print(f"Datos insertados en la tabla: {nombre_tabla}")

    except Exception as e:
        print(f"Error al subir a BD en PostgreSQL: {e}")
        raise  # 🔥 importante: no ocultar errores


if __name__ == "__main__":
    # Ruta correcta dentro del contenedor
    data = cargar_y_limpiar_csv("data/raw/churn.csv")

    if data is not None:
        print("Datos cargados, iniciando inserción en db")
        subir_a_postgres(data, "cliente")
        print("Pipeline finalizado correctamente")
    else:
        print("No se pudo cargar el CSV")