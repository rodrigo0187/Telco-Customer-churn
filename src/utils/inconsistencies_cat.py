import pandas as pd

def categorical_inconsistencies(df:pd.DataFrame)-> bool:
    
    df = df.copy()
    
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        values = df[col].dropna().astype(str)
        if values.empty:
            continue
        
        normalize = values.str.strip().str.lower()
        if len(values.unique()) != len(normalize.unique()):
            return True
    return False
    