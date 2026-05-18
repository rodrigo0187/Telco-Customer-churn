import pandas as pd

def encode_features(df:pd.DataFrame)-> pd.DataFrame:
    """Codifica variables categóricas para modelos de machine learning.

    Args:
        df (pd.DataFrame): Entrada del dataframe que contiene datos de cliente

    Returns:
        pd.DataFrame: Retorna un dataframe listo para el modelado
    """   
     
    df = df.copy()
    
    # binarios
    binary_cols = ['partner','dependents','phoneservice','paperlessbilling','churn']
    
    for col in binary_cols:
        if col in df.columns:
            df[col]=df[col].map({'Yes':1,'No':0})
            
    # categoricas especiales multiclases
    special_col = ['multiplelines','onlinesecurity','onlinebackup','deviceprotection',
                   'techsupport','streamingtv','streamingmovies']
        
    for col in special_col:
        if col in df.columns:
            df[col] = df[col].replace({'No internet service':'No','No phone service':'No'})
            # mapeo
            df[col] = df[col].map({'Yes':1,'No':0})
    # one-hot automatico
    categorical_cols = df.select_dtypes(include="object").columns.to_list()
    
    # columna no feature
    exclude_cols= ['customerid']
    categorical_cols = [col for col in categorical_cols if col not in exclude_cols]
    df = pd.get_dummies(df,columns=categorical_cols,drop_first=True)
        
    # validacion o restriccion
    remaings_cat =[c for c in df.select_dtypes(include="object").columns if c != 'customerid']
    if len(remaings_cat) > 0:
        print('!Restriccion quedan columna categóricas sin encoding')
    
    if df.isna().sum().sum() > 0:
        print('!Restriccion, quedan valores nulos sin encoding')
    
    return df