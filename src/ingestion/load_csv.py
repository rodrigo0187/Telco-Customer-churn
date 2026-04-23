import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables desde el .env
load_dotenv()

def cargar_y_limpiar_csv(ruta_csv, carpeta_backup='copy_churn_csv'):
    """Lee el CSV y prepara el entorno."""
    try:
        # Verificamos si el archivo existe antes de intentar leerlo
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

        df = pd.read_csv(ruta_csv, low_memory=False, sep=',')
        print(f"CSV cargado: {len(df)} filas detectadas.")
        
        # Crear carpeta de backup si no existe
        if not os.path.exists(carpeta_backup):
            os.makedirs(carpeta_backup)
            print(f'Carpeta de backup "{carpeta_backup}" lista.')
            
        return df

    except Exception as e:
        print(f"Error al procesar CSV: {e}")
        return None

def subir_a_postgres(df, nombre_tabla):
    """Establece conexión y sube el DataFrame."""
    # Extraer credenciales del .env para no dejarlas fijas (hardcoded)
    user = os.getenv('DB_USER', 'admin')
    password = os.getenv('DB_PASS', 'admin')
    host = os.getenv('DB_HOST', 'db')
    port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'churn_db')

    url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    
    try:
        engine = create_engine(url)
        # 'replace' para que cree la tabla la primera vez o la actualice
        df.to_sql(nombre_tabla, engine, if_exists='replace', index=False)
        print(f"¡Datos disponibles en Postgres! Tabla: {nombre_tabla}")
    except Exception as e:
        print(f"Error de conexión/escritura en BD: {e}")

if __name__ == "__main__":
    # IMPORTANTE: En Docker, la ruta suele ser absoluta dentro del contenedor
    # Si en el docker-compose mapeaste ./ingestion:/app/ingestion
    RUTA_ARCHIVO = "ingestion/Churn.csv" 
    
    data = cargar_y_limpiar_csv(RUTA_ARCHIVO)
    
    if data is not None:
        subir_a_postgres(data, "clientes_churn")