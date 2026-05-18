# encargado de solo transformar tipos de datos
import pandas as pd

def fix_data_types(df:pd.DataFrame)-> pd.DataFrame:

    """Corrige los tipos de datos incorrectos del dataframe

    Args:
        df (_type_): Entrada DataFrame

    Returns:
        _type_: Retorna el DataFrame con los tipos de datos correcto
    """    
    
    df['totalcharges'] = pd.to_numeric(df['totalcharges'],errors='coerce')
    df['monthlycharges'] = pd.to_numeric(df['monthlycharges'], errors='coerce')
    return df