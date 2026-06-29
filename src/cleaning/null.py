import pandas as pd
import numpy as np
def normalize_nulls(df: pd.DataFrame,null_values=None)-> pd.DataFrame:
    """Identifica e imputa valores faltantes tanto en columnas númericas como categóricas.
    
    El tratamiento se realiza de manera diferenciada por tipo de datos:
    - columnas numéricas: los valores nulos se reemplazan por la mediana de la columna.
    - columnas categóricas/objeto: Los valores nulos se reemplazan por la cadena 
      "desconocido".

    Args:
        df (pd.DataFrame): El DataFrame original con valores faltantes.
        null_values (optional): Parámetro reservado para especificación personalizada 
            de valores a tratar como nulos. Por defecto es None.

    Returns:
        pd.DataFrame: Una copia del DataFrame con todos los valores nulos 
            imputados según su tipo de columna.
    """    
    df = df.copy()
    
    columns_numeric = df.select_dtypes(include=[np.number]).columns
    # tratamiento para numericos mediana
    for col in columns_numeric:
        if df[col].isnull().sum()>0:
            mediana = df[col].median()
            df[col] = df[col].fillna(mediana)
    # tratamiendo automatico para categóricas
    columns_categoric = df.select_dtypes(include=['object','category']).columns
    
    for col in columns_categoric:
        if df[col].isnull().sum()>0:
            df[col] = df[col].fillna("desconocido")
    return df