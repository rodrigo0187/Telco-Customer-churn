import pandas as pd
from pathlib import Path
from datetime import datetime

def saved_dataset(df : pd.DataFrame, stage : str, filename : str, versioning: bool = False):
    """Guarda el DataFrame en la ruta correspondiente a su etapa de preparacion.

    Args:
        df (pd.DataFrame): Entrada DataFrame
    """    
    base_path = Path('data/processed') /stage
    base_path.mkdir(parents=True, exist_ok=True)
    
    if versioning:
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        filename = f'{timestamp}_{filename}'
        
    full_path = base_path / filename
    df.to_csv(full_path,index=False)
        
    print(f'[save] »» {stage} -> {full_path}')
        