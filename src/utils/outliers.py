import pandas as pd

def outliers(df: pd.DataFrame,exclude_col:list=None)->bool:
    """Analiza si existen valores atípicos en las columnas numéricas usando el método IQR.

    Calcula el Rango Intercuartílico (IQR) entre los cuartiles 0.25 (Q1) y 0.75 (Q3) 
    para establecer los límites estadísticos permitidos:
    - Límite inferior: Q1 - 1.5 * IQR
    - Límite superior: Q3 + 1.5 * IQR
    Cualquier valor fuera de este rango se considera un valor atípico.

    Args:
        df (pd.DataFrame): El DataFrame de entrada con los datos numéricos a evaluar.
        exclude_col (list, optional): Lista con los nombres de las columnas 
            que se deben excluir del análisis de atípicos. Por defecto es None.

    Returns:
        bool: Retorna True si encuentra al menos un valor atípico en cualquiera de 
            las columnas analizadas; False en caso contrario.
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

    