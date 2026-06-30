import pandas as pd

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Genera variables categóricas, numéricas e interacciones de negocio para el modelo de Churn.

    Calcula y añade los siguientes indicadores estratégicos al DataFrame:
    - `charges_ratio`: Proporción del gasto total respecto a la antigüedad (se suma 1 a 
       `tenure` para mitigar errores por división por cero en clientes nuevos).
    - `is_new_customer`: Indicador binario (1/0) para clientes con antigüedad menor a 6 meses.
    - `num_services`: Conteo total de servicios contratados con respuesta 'yes'.
    - `is_auto_payment`: Indicador binario (1/0) de pago automático (tarjeta o transferencia).
    - `is_risky_payment`: Indicador binario (1/0) para métodos de pago de alto riesgo (cheque electrónico).
    - `is_month_to_month`: Indicador binario (1/0) para contratos mensuales sin permanencia.
    - `new_monthly_combo`: Variable de interacción (1/0) que resalta clientes que son tanto 
       nuevos como bajo contrato mes a mes (perfil de alto riesgo de Churn).

    Args:
        df (pd.DataFrame): El DataFrame de entrada preprocesado que contiene las variables 
            originales del cliente.

    Returns:
        pd.DataFrame: Una copia del DataFrame original enriquecida con las 7 nuevas variables 
            de negocio desarrolladas.
    """
    
    df = df.copy()

    # Variable nueva: valor económico
    df["charges_ratio"] = df["totalcharges"] / (df["tenure"] + 1)

    # Variable nueva: antigüedad
    df["is_new_customer"] = (df["tenure"] < 6).astype(int)

    service_cols = [
        "phoneservice",
        "multiplelines",
        "internetservice",
        "onlinesecurity",
        "onlinebackup",
        "deviceprotection",
        "techsupport",
        "streamingtv",
        "streamingmovies"
    ]

    exist_services = [c for c in service_cols if c in df.columns]
    df["num_services"] = df[exist_services].apply(
        lambda row: sum(str(val).strip().lower() == "yes" for val in row), axis=1
    )

    # Variables nuevas:
    if "paymentmethod" in df.columns:
        df["is_auto_payment"] = df["paymentmethod"].isin(
            ["bank transfer (automatic)", "credit card (automatic)"]
        ).astype(int)
        df["is_risky_payment"] = (df["paymentmethod"] == "electronic check").astype(int)

    # Variable nueva: contrato
    if "contract" in df.columns:
        df["is_month_to_month"] = (df["contract"] == "month-to-month").astype(int)

    # Variable nueva: interacción
    df["new_monthly_combo"] = (
        (df["is_new_customer"] == 1) & (df["is_month_to_month"] == 1)
    ).astype(int)

    return df