import pandas as pd

def categorical_nulls(self)-> dict:
    """Calcula la proporción de valores nulos especificamente en las columnas categóricas.

    Returns:
        dict: LLaves como nombres de columnas 'object','category' que tienen nulos,
        y sus valores como la proporcion (0.0 a 1.0) de registros faltantes.
    """    
    cat_cols = self.data.select_dtypes(include=['object','category'])
    
    null_proportion = cat_cols.isnull().mean()
    return null_proportion[null_proportion>0].to_dict()