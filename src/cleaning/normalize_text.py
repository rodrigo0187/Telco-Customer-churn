import pandas as pd

def normalize_text(df:pd.DataFrame)-> pd.DataFrame:
    """Normaliza y unifica las columnas de tipo texto en el DataFrame.
    
    El proceso aplica las siguientes transformaciones a todas las columnas categoricas y de tipo objeto:
    1. convierte  todos los valores a cadenas de texto(str).
    2. elimina los espacios en blanco al inicio y al final mediante un (strip).
    3. convierte todo el texto de la cadena en minúsculas (lower).
    4. remueve cualquier caracter especial, puntuación o acento, manteniendo unicamente
        caracteres alfanumericos basicos(a-z , 0,9) y espacios.

    Args:
        df (pd.DataFrame): El DataFrame de entrada que se quiere normalizar.

    Returns:
        Una copia del DataFrame con las columnas de texto limpias y estandarizadas.
        Las columnas como tipo 'category' se devuelven como tipo 'object'.
    """    
    df = df.copy()
    
    column_categoricas = df.select_dtypes(include=['object','category']).columns
    
    for col in column_categoricas:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].str.replace(r'[^a-z0-9\s]','',regex=True)
        
    return df