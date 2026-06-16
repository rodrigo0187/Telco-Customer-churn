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
    """Audita el dataset entrante bajo reglas flexibles de negocio.

    Args:
        df (pd.DataFrame): Entrada DataFrame

    Returns:
        bool: True si el dataset es apto para continuar. caso contrario se rechaza.
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
    missing_cols = columnas_espe - columnas_act
    if missing_cols:
        logger.critical(f'Rechazo de archivo: Faltan columnas criticas en el csv: {list(missing_cols)}')
        return False  
    # tasa de nulos > 50%
    total_filas = len(df)
    for col in df.columns:
        nulos_col = df[col].isna().sum() + (df[col]=='').sum() + (df[col]==' ').sum()
        tasa_nulos = (nulos_col/ total_filas) *100
        if tasa_nulos > 50:
            logger.error(f'Alerta de calidad, la columna {col} tiene una tasa de nulos {tasa_nulos:.2f} nulos. mayor al 50%')
    logger.info('Auditoria completada, El data set cumple con los requisitos minimos de estructura.')
    return True
        