import pandas as pd

def has_negative_values(df:pd.DataFrame,exclude_col:list=None)-> bool:
    """Analiza si existen valores negativos en las columnas numéricas del DataFrame.

    Filtra el conjunto de datos para evaluar únicamente las variables numéricas,
    permitiendo omitir columnas específicas que puedan contener valores negativos
    por razones de negocio o diseño (como identificadores numéricos).

    Args:
        df (pd.DataFrame): El DataFrame de entrada que se desea inspeccionar.
        exclude_col (list, optional): Lista con los nombres de las columnas 
            que se deben excluir del análisis. Por defecto es None.

    Returns:
        bool: Retorna True si encuentra al menos un valor menor a cero (< 0) 
            en las columnas analizadas; False en caso contrario.
    """
    if exclude_col is None:
        exclude_col = []
    
    col_negative= df.select_dtypes(include=['number'])
    
    col_negative = col_negative.drop(columns= exclude_col,errors='ignore')
    return (col_negative < 0).any().any()