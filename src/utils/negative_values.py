import pandas as pd

def has_negative_values(df:pd.DataFrame,exclude_col:list=None)-> bool:
    """Analiza si existen valores negativos en columna numéricas
    
    Args:
        df (pd.DataFrame): DataFrame Entrada

    Returns:
        bool: Retorna verdadero si existe valores negativos,
        caso contrario False.
    """    
    if exclude_col is None:
        exclude_col = []
    
    col_negative= df.select_dtypes(include=['number'])
    
    col_negative = col_negative.drop(columns= exclude_col,errors='ignore')
    return (col_negative < 0).any().any()