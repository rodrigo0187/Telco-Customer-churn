# Cargar variables de entorno
import os
import pandas as pd
from datetime import datetime


def cargar_csv(ruta_csv: str,carpeta_backup: str = 'data/backup/raw') -> pd.DataFrame:
    """
    Carga y normaliza un archivo CSV.

    Args:
        ruta_csv (str): Ruta del archivo CSV.
        carpeta_backup (str, optional): Carpeta de respaldo.

    Returns:
        pd.DataFrame: DataFrame procesado.
    """

    try:

        # validar archivo
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f'No se encontró el archivo: {ruta_csv}')

        # leer csv
        df = pd.read_csv(ruta_csv,low_memory=False,sep=',')

        print(f'CSV cargado: {len(df)} filas.')

        # normalizar columnas
        df.columns = (df.columns.str.strip().str.lower())

        # renombrar columnas
        df = df.rename(columns={'customer_id': 'customerid'})

        # convertir tipos
        df['totalcharges'] = pd.to_numeric(df['totalcharges'],errors='coerce')

        # crear backup
        os.makedirs(carpeta_backup, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        nombre_archivo = f'churn_{timestamp}.csv'

        ruta_backup = os.path.join(carpeta_backup,nombre_archivo)

        df.to_csv(ruta_backup, index=False)

        print(f'Backup generado: {ruta_backup}')

        return df

    except Exception as e:
        print(f'Error al cargar CSV: {e}')
        raise