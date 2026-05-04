def remove_nulls(df):
    # identificar los valores posibles de null en la colmna TotalCharges
    
    mask_null = df['totalcharges'].isna()
    
    # validar los nulls validos y no validos
    valid_nulls = df[(mask_null)&(df['tenure'] == 0)]
    invalid_nulls = df[(mask_null) & (df['tenure'] >0)]
    
    print(f'Nulos validos: {len(valid_nulls)}')
    print(f'Nulos invalidos : {len(invalid_nulls)}')
    
    # eliminar solo los invalidos
    df = df.drop(invalid_nulls.index)
    return df