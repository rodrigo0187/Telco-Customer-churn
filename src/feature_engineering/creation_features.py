import pandas as pd

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Creación de variables categoricas para modelo de machine learning.

    Args:
        df (pd.DataFrame): Entrada del dataframe churn.

    Returns:
        pd.DataFrame: Agrega nuevas variables categoricas al dataframe.
    """    
    df = df.copy()

    # varible nueva valor económico
    df["charges_ratio"] = df["totalcharges"] / (df["tenure"] + 1)

    # variable nueva antigüedad
    df["is_new_customer"] = (df["tenure"] < 6).astype(int)

    # variable nueva número de servicios
    #  variables categoricas
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

    df["num_services"] = df[service_cols].apply(
        lambda row: sum(val == "Yes" for val in row), axis=1
    )

    # variable nueva pago
    df["is_auto_payment"] = df["paymentmethod"].isin(
        ["Bank transfer (automatic)", "Credit card (automatic)"]
    ).astype(int)

    df["is_risky_payment"] = (df["paymentmethod"] == "Electronic check").astype(int)

    # variable nueva contrato
    df["is_month_to_month"] = (df["contract"] == "Month-to-month").astype(int)

    # variable nueva interacción
    df["new_monthly_combo"] = (
        (df["is_new_customer"] == 1) & (df["is_month_to_month"] == 1)
    ).astype(int)

    return df