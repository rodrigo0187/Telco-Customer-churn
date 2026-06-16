import pandas as pd

def normalize_text(df:pd.DataFrame)-> pd.DataFrame:
    """Normaliza columnas de tipo texto

    Args:
        df (_type_): pd.DataFrame entrada

    Returns:
        _type_: Retorna las categoricas unificadas, controlando espacios y minusculas.
        
    """    
    df = df.copy()
    
    column_categoricas = df.select_dtypes(include=['object','category']).columns
    
    for col in column_categoricas:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].str.replace(r'[^a-z0-9\s]','',regex=True)
        
    return df