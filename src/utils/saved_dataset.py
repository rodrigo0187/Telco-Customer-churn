import pandas as pd
from pathlib import Path
from datetime import datetime

def saved_dataset(df : pd.DataFrame, stage : str, filename : str, versioning: bool = False):
    """Guarda del DataFrame en formato csv dentro de la ruta correpondiente a su etapa.
    Crea automáticamente los directorios necesarios si no existen. Si el versionamiento 
    está activo, antepone una marca de tiempo con el formato 'DDMMAAAA_HHMMSS' al 
    nombre del archivo para evitar sobreescrituras.

    Args:
        df (pd.DataFrame): El DataFrame que se desea almacenar en disco.
        stage (str): Nombre de la etapa de preparación (ej: 'raw', 'cleaned', 'features'), 
            la cual se utilizará como subcarpeta dentro de 'data/processed/'.
        filename (str): Nombre final que tendrá el archivo CSV (incluyendo extensión, ej: 'churn.csv').
        versioning (bool, optional): Indica si se debe aplicar control de versiones 
            añadiendo un timestamp al inicio del archivo. Por defecto es False.

    Returns:
        None
    """
    
    base_path = Path('data/processed') /stage
    base_path.mkdir(parents=True, exist_ok=True)
    
    if versioning:
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        filename = f'{timestamp}_{filename}'
        
    full_path = base_path / filename
    df.to_csv(full_path,index=False)
        
    print(f'[save] »» {stage} -> {full_path}')
        