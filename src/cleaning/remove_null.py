import pandas as pd

def remove_nulls(df:pd.DataFrame)-> pd.DataFrame:
    """Valida y analiza los valores nulos en la columna TotalCharges.

    Args:
        df (pd.DataFrame): DataFrame churn.

    Returns:
        pd.DataFrame: DataFrame sin registro con nulos inválidos
    """
    mask_null = df['totalcharges'].isna()
    
    # validar los nulls validos y no validos
    valid_nulls = df[(mask_null)&(df['tenure'] == 0)]
    invalid_nulls = df[(mask_null) & (df['tenure'] >0)]
    
    print(f'Nulos validos: {len(valid_nulls)}')
    print(f'Nulos invalidos : {len(invalid_nulls)}')
    
    df = df.drop(invalid_nulls.index)
    return df