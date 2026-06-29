import pandas as pd
import logging

logger = logging.getLogger(__name__)

def remove_duplicates_customers(df: pd.DataFrame, id_col: str = 'customerid') -> pd.DataFrame:
    """Consolida registros duplicados basados en el ID del cliente mediante agregación.

    Garantiza un ID único para la base de datos fusionando filas duplicadas de la 
    siguiente manera:
    - Variables numéricas: Se calcula la media (`mean`) de los registros duplicados.
    - Variables categóricas/objetos: Se conserva el primer registro encontrado (`first`).

    Args:
        df (pd.DataFrame): DataFrame original que contiene los datos de churn.
        id_col (str, optional): Nombre de la columna identificadora del cliente. 
            Por defecto es 'customerid'.

    Raises:
        ValueError: Si la columna identificadora especificada en `id_col` no 
            existe en el DataFrame.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con filas consolidadas e IDs únicos, 
            manteniendo el orden de las columnas originales.
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