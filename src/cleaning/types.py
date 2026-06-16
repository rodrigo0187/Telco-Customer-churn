# encargado de solo transformar tipos de datos
import pandas as pd

def fix_data_types(df:pd.DataFrame)-> pd.DataFrame:

    """Corrige los tipos de datos incorrectos del dataframe

    Args:
        df (_type_): Entrada DataFrame

    Returns:
        _type_: Retorna el DataFrame con los tipos de datos correcto
    """    
    df = df.copy()
    for col in df.columns:
        if df[col].dtype=='object':
            converted = pd.to_numeric(df[col],errors='coerce')    
            if not converted.isna().all():
                df[col] = converted
        if df[col].dtype in['int64','float64']:
            df[col]= df[col].abs()
    return df