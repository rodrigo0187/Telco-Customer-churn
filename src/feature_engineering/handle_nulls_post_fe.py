import pandas as pd

def handle_nulls_post_fe(df: pd.DataFrame) -> pd.DataFrame:
    """Imputa valores en totalcharges para clientes nuevos y recalcula ratios."""
    df = df.copy()
    
    if 'tenure' in df.columns and 'totalcharges' in df.columns:
        df.loc[df['tenure'] == 0, 'totalcharges'] = 0.0
    
    if 'charges_ratio' in df.columns:
        df['charges_ratio'] = df['totalcharges'] / (df['tenure'] + 1)
    
    return df