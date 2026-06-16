import pandas as pd

def outliers(df: pd.DataFrame,exclude_col:list=None)->bool:
    """Analiza si existen valores atípicos usando intercuantilico entre el 0.25 y 0.75

    Args:
        df (pd.DataFrame): Entrada DateFrame

    Returns:
        bool: Retorna verdadero o falso si encuentra atípicos.
    """    
    df = df.copy()
    df = df.select_dtypes(include=['number'])
    if exclude_col:
        df = df.drop(columns=exclude_col,errors='ignore')
    # IQR
    q1= df.quantile(0.25)
    q3= df.quantile(0.75)
    IQR = q3 - q1
    lower_bound = q1 - 1.5 * IQR
    upper_bound = q3 + 1.5 * IQR
    
    return ((df < lower_bound)|(df > upper_bound)).any().any()

    