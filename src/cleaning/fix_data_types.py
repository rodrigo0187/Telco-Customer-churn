# encargado de solo transformar tipos de datos
import pandas as pd

def fix_data_types(df):
    df['totalcharges'] = pd.to_numeric(df['totalcharges'],errors='coerce')
    df['monthlycharges'] = pd.to_numeric(df['monthlycharges'], errors='coerce')
    return df