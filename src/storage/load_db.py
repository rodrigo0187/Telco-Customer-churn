import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

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

        df = df.reset_index(drop=True)

        if 'customer_id' in df.columns:
            df = df.drop_duplicates(subset=['customer_id'])

        df.columns = [str(c).strip() for c in df.columns]
# Reemplaza los nombres de las columnas si existen nuevas
        df.to_sql(nombre_tabla, engine, if_exists='replace', index=False)

        print(f"Datos insertados en la tabla: {nombre_tabla}")

    except Exception as e:
        print(f"Error al subir a BD en PostgreSQL: {e}")