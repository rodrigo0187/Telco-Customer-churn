def handle_nulls_post_fe(df):
    df = df.copy()
    # imputar
    df.loc[df['tenure']==0 , 'totalcharges'] = 0
    
    # recalcular charges_ratio
    df['charges_ratio'] = df['totalcharges'] / (df['tenure']+1)
    
    return df
    