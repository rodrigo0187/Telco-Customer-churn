import pandas as pd

def impute_handle_numeric(df:pd.dataFrame)-> pd.dataFrame:
    """Analiza por columna valores numéricos nulos.

    Args:
        pd (pd.dataFrame): Entrada DataFrame

    Returns:
        pd.dataFrame: Rellena valores numericos por la media.
    """    
    df = df.copy()
    
    nums_col = df.select_dtypes(include=['number']).columns
    
    for col in nums_col:
        median = df[col].median()
        df[col] = df[col].fillna(median)
    
    return df