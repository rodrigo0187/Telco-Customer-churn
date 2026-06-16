import pandas as pd
import logging

logger = logging.getLogger(__name__)

def remove_duplicates_customers(df: pd.DataFrame, id_col: str = 'customerid') -> pd.DataFrame:
    """
    Consolida registros duplicados basados en el ID del cliente mediante fusión.
    Garantiza un ID único para la BD sin destruir información valiosa.

    Args:
        df (pd.DataFrame): DataFrame original de churn.
        id_col (str): Nombre de la columna identificadora. Por defecto 'customerid'.

    Returns:
        pd.DataFrame: DataFrame tratado con IDs únicos consolidados.
    """
    df = df.copy()
    
    # Validación temprana: Evita que el pipeline se rompa a futuro si cambia el ID
    if id_col not in df.columns:
        logger.warning(f"La columna de identidad '{id_col}' no existe. No se pueden procesar duplicados.")
        raise ValueError(f"Columna de identidad no encontrada en el DataFrame: {id_col}")
    
    # Registramos cuántas filas tenemos antes del tratamiento
    filas_iniciales = len(df)
    
    # Definición dinámica de reglas (Ciega a nombres fijos de columnas)
    reglas = {
        col: 'mean' if df[col].dtype in ['int64', 'float64'] else 'first' 
        for col in df.columns if col != id_col
    }
    
    # 3. Tratamiento por agregación
    df_consolidado = df.groupby(id_col, as_index=False).agg(reglas)
    
    filas_finales = len(df_consolidado)
    duplicados_fusionados = filas_iniciales - filas_finales
    
    logger.info(f"Tratamiento de duplicados completado. Filas iniciales: {filas_iniciales}."
                f"Filas consolidadas: {filas_finales}. Registros duplicados fusionados: {duplicados_fusionados}.")
    
    return df_consolidado