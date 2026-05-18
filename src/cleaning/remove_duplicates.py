import pandas as pd

def remove_customer_duplicates(df:pd.DataFrame)-> pd.DataFrame:
    """Elimina clientes basándose en customerid

    Args:
        df (_type_): DataFrame churn

    Returns:
        _type_: Retorna un unico registro de cliente por customerid.
    """    
    before = len(df)
    df = df.drop_duplicates(subset = ['customerid'])
    after = len(df)
    print(f'Duplicados eliminados: {before - after}')
    return df