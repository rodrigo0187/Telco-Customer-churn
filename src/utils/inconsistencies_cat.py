import pandas as pd

def categorical_inconsistencies(df:pd.DataFrame)-> bool:
    """Detecta de forma temprana si existen inconsistencias de formato en columnas categóricas.

    Inspecciona todas las columnas de tipo objeto/texto y compara la cantidad de 
    valores únicos originales contra su versión normalizada (sin espacios en los 
    extremos y en minúsculas). Si los conteos difieren, significa que existen 
    duplicados implícitos por problemas de escritura (ej: 'Internet' e 'internet ').

    Args:
        df (pd.DataFrame): El DataFrame que contiene las variables categóricas a analizar.

    Returns:
        bool: Retorna True si detecta al menos una inconsistencia de formato en 
            cualquiera de las columnas de texto; False si todas están perfectamente 
            estandarizadas o si no hay columnas de texto.
    """    
    df = df.copy()
    
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        values = df[col].dropna().astype(str)
        if values.empty:
            continue
        
        normalize = values.str.strip().str.lower()
        if len(values.unique()) != len(normalize.unique()):
            return True
    return False
    