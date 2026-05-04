def remove_customer_duplicates(df):
    before = len(df)
    df = df.drop_duplicates(subset = ['customerid'])
    after = len(df)
    print(f'Duplicados eliminados: {before - after}')
    return df