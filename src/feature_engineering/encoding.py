import pandas as pd

def encode_features(df:pd.DataFrame)-> pd.DataFrame:
    df = df.copy()
    
    # binarios
    binary_cols = ['partner','dependents','phoneservice','paperlessbilling','churn']
    
    for col in binary_cols:
        if col in df.columns:
            df[col]=df[col].map({'Yes':1,'No':0})
            
    # categoricas especiales multiclases
    special_col = ['multiplelines','onlinesecurity','onlinebackup','deviceprotection',
                   'techsupport','streamintv','streamingmovie']
    
    for col in special_col:
        if col in df.columns:
            df[col] = df[col].replace({'No internet service':'No','No phone service':'No'})
            
    # one-hot
    categorical_col = ['contract','paymentmethod','internetservice']
    df = pd.get_dummies(df,columns=[c for c in categorical_col if c in df.columns],drop_first=True)
    
    # validacion o restriccion
    if df.select_dtypes(include='object').shape[1] > 0:
        print('!Restriccion quedan columna categóricas sin encoding')
    
    if df.isna().sum().sum() > 0:
        print('!Restriccion, quedan valores nulos sin encoding')
    
    return df