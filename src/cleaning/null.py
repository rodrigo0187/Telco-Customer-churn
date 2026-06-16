import pandas as pd
import numpy as np
def normalize_nulls(df: pd.DataFrame,null_values=None)-> pd.DataFrame:
    """_summary_ : trata los valores nulos a todo el dataset sin eliminar registros.

    Args:
        df (pd.DataFrame): 

    Returns:
        pd.DataFrame: _description_
    """    
    df = df.copy()
    
    columns_numeric = df.select_dtypes(include=[np.number]).columns
    # tratamiento para numericos mediana
    for col in columns_numeric:
        if df[col].isnull().sum()>0:
            mediana = df[col].median()
            df[col] = df[col].fillna(mediana)
    # tratamiendo automatico pra categóricas
    columns_categoric = df.select_dtypes(include=['object','category']).columns
    
    for col in columns_categoric:
        if df[col].isnull().sum()>0:
            df[col] = df[col].fillna("desconocido")
    return df