# normalizacion  categóricas de tipo object
def normalize_text(df):
    object_cols = df.select_dtypes(include = 'object').columns
    
    for col in object_cols:
        df[col] = df[col].str.strip().str.lower()
    
    return df