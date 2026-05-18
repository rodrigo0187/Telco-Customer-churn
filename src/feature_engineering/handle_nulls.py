import pandas as pd

def handle_nulls_post_fe(df:pd.DataFrame)-> pd.DataFrame:
    """Imputa valores en totalcharges para clientes nuevos

    Args:
        df (pd.DataFrame): DataFrame churn

    Returns:
        pd.DataFrame: DataFrame con totalcharges imputado y variables derivadas actualizadas.
    """    
    df = df.copy()
    # imputacion basada en reglas de negocio
    df.loc[df['tenure']==0 , 'totalcharges'] = 0
    
    # recalcular charges_ratio
    df['charges_ratio'] = df['totalcharges'] / (df['tenure']+1)
    
    return df
    