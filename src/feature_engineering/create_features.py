import pandas as pd

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Creación de variables categóricas y de negocio para el modelo."""
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