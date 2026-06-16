import pandas as pd

def impute_categoric_nulls(df: pd.DataFrame)-> pd.DataFrame:
    """Analiza valores nulos en el dataset

    Args:
        pd (pd.DataFrame): Entrada dataFrame

    Returns:
        pd.DataFrame: Rellena las variables categóricas nulas por la moda.
    """    
    df = df.copy()
    
    cat_nulls= df.select_dtypes(include=['object'])
    
    for col in cat_nulls:
        moda = df[col].mode()[0]
        df[col] = df[col].fillna(moda)

    return df