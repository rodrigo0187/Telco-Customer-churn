import pandas as pd
from src.utils.logging import get_logger

logger = get_logger('auditar_validar_dataset')


EXPECTED_SCHEMA = {
    "customerid": "object",
    "gender": "object",
    "seniorcitizen": "int64",
    "partner": "object",
    "dependents": "object",
    "tenure": "int64",
    "phoneservice": "object",
    "multiplelines": "object",
    "internetservice": "object",
    "onlinesecurity": "object",
    "onlinebackup": "object",
    "deviceprotection": "object",
    "techsupport": "object",
    "streamingtv": "object",
    "streamingmovies": "object",
    "contract": "object",
    "paperlessbilling": "object",
    "paymentmethod": "object",
    "monthlycharges": "float64",
    "totalcharges": "object",  # columna por defecto tiene
    "churn": "object"
}
def auditar_validar_dataset(df:pd.DataFrame)-> bool:
    """Audita la estructura y el contrato de datos del dataset frente al esquema esperado.

    Esta función actúa como un validador de calidad en el pipeline. Realiza tres 
    acciones críticas basadas en la constante global `EXPECTED_SCHEMA`:
    1. Detecta y remueve columnas sobrantes directamente del DataFrame de entrada 
       (mutación in-place) para proteger la firma del modelo de Machine Learning.
    2. Rechaza el dataset si se detecta la ausencia de columnas obligatorias.
    3. Evalúa la tasa de valores faltantes por columna (incluyendo NaN, strings 
       vacíos y espacios en blanco), emitiendo alertas si superan el límite tolerable.

    Args:
        df (pd.DataFrame): El DataFrame entrante que se va a auditar. 
            NOTA: Este objeto se modifica in-place si se detectan columnas extra.

    Returns:
        bool: Retorna True si el dataset cuenta con todas las columnas requeridas 
            y es apto para continuar en el flujo; False si faltan columnas críticas 
            y debe ser rechazado.
    """
    logger.info('Iniciando auditoria y validación de contrato...')
    # columnas actuales del dataset
    columnas_act= set(df.columns)
    # columnas esperadas
    columnas_espe = set(EXPECTED_SCHEMA.keys())
    
    extra_cols = columnas_act - columnas_espe
    # deteccion de nuevas columnas, estas serán removidas generando un reporte en log
    if extra_cols:
        logger.warning(f'Detección de nuevas columnas {len(extra_cols)} extra.') 
        for col in extra_cols:
            logger.warning(f' -> columna nueva encontrada {col} | tipo :{df[col].dtype}')
        df.drop(columns=list(extra_cols),inplace=True)
        logger.info(' -> columnas removidas del flujo para proteger el Modelo ML.')
            
    # Columnas faltantes critico
    UMBRAL_CRITICO = 20.0
    UMBRAL_WARNING = 5.0
    missing_cols = columnas_espe - columnas_act
    if missing_cols:
        logger.critical(f'Rechazo de archivo: Faltan columnas criticas en el csv: {list(missing_cols)}')
        return False  
    # tasa de nulos > 20%
    MIN_NULOS = 20
    total_filas = len(df)
    for col in df.columns:
        nulos_col = df[col].isna().sum() + (df[col]=='').sum() + (df[col]==' ').sum()
        tasa_nulos = (nulos_col/ total_filas) *100
        if tasa_nulos > MIN_NULOS:
            logger.critical(f'Alerta de calidad, la columna {col} tiene una tasa de nulos {tasa_nulos:.2f} nulos. mayor al 20%')
        elif tasa_nulos > UMBRAL_CRITICO:
            logger.warning(f'Alerta: la columna {col} tiene {tasa_nulos:.2f} de nulos. Supera el óptimo umbral del {UMBRAL_WARNING}%')
    logger.info('Auditoria completada, El data set cumple con los requisitos minimos de estructura.')
    return True