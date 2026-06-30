import pandas as pd
import numpy as np
# Importamos las funciones de los otros archivos del mismo directorio
from src.feature_engineering.create_features import create_features
from src.feature_engineering.handle_nulls_post_fe import handle_nulls_post_fe
pd.set_option('future.no_silent_downcasting',True)

def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Orquesta la preparación final y codifica las variables categóricas a numéricas.

    Ejecuta el pipeline secuencial de ingeniería de características (`create_features`) 
    y limpieza de nulos final (`handle_nulls_post_fe`). Posteriormente, transforma 
    las variables cualitativas mediante dos técnicas:
    1. Mapeo Binario Personalizado: Convierte respuestas 'yes'/'no' a 1/0, asimilando 
       los valores 'desconocido' o servicios no contratados al caso base (0).
    2. Codificación One-Hot: Aplica `pd.get_dummies` de forma automática a las variables 
       multiclase restantes (ej. contratos, métodos de pago), eliminando la primera 
       categoría (`drop_first=True`) para evitar redundancia y asegurar compatibilidad 
       con modelos lineales y basados en árboles.

    Args:
        df (pd.DataFrame): El DataFrame con los datos crudos o parcialmente limpios.

    Returns:
        pd.DataFrame: Copia del DataFrame completamente matematizado (con columnas 
            enteras o flotantes), listo para ser separado en matrices X e y para el 
            entrenamiento del modelo. Excluye 'customerid' del encoding.
    """

    df = df.copy()
    
    # REGLA DE ORDEN: Primero ejecutamos las dos funciones previas
    df = create_features(df)
    df = handle_nulls_post_fe(df)
    
    # 1. Binarios estándar (Usamos .replace en minúsculas por la capa de limpieza)
    binary_cols = ['partner', 'dependents', 'phoneservice', 'paperlessbilling', 'churn']
    for col in binary_cols:
        if col in df.columns:
            # Protegemos "desconocido" asignándolo por defecto a 0
            df[col] = df[col].replace({'yes': 1, 'no': 0, 'desconocido': 0,np.nan:0}).astype(int)
            
    # 2. Categóricas especiales multiclases
    special_cols = ['multiplelines', 'onlinesecurity', 'onlinebackup', 'deviceprotection',
                    'techsupport', 'streamingtv', 'streamingmovies']
    for col in special_cols:
        if col in df.columns:
            df[col] = df[col].replace({
                'no internet service': 'no', 
                'no phone service': 'no',
                'desconocido': 'no'  # El nulo limpio se asimila a la mayoría ('no')
            })
            df[col] = df[col].replace({'yes': 1, 'no': 0}).astype(int)
            
    # 3. One-hot automático para las multiclases restantes (ej. contract, paymentmethod)
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.to_list()
    
    exclude_cols = ['customerid']
    categorical_cols = [col for col in categorical_cols if col not in exclude_cols]
    
    # CORRECCIÓN CRÍTICA: dtype=int garantiza salidas de 0 y 1 en lugar de True/False
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True, dtype=int)
        
    # Validaciones o restricciones
    remaining_cat = [c for c in df.select_dtypes(include="object").columns if c != 'customerid']
    if len(remaining_cat) > 0:
        print(f'!Restricción: quedan columnas categóricas sin encoding: {remaining_cat}')
    
    # Excluimos customerid de la revisión de nulos para evitar falsos positivos
    df_check = df.drop(columns=['customerid'], errors='ignore')
    if df_check.isna().sum().sum() > 0:
        print('!Restricción: quedan valores nulos sin encoding')
    
    return df