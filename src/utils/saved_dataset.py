from pathlib import Path
from datetime import datetime

def saved_dataset(df,stage : str, filename : str, versioning: bool = False):
    base_path = Path('data/processed') /stage
    base_path.mkdir(parents=True, exist_ok=True)
    
    if versioning:
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        filename = f'{timestamp}_{filename}'
        
    full_path = base_path / filename
    df.to_csv(full_path,index=False)
        
    print(f'[save] »» {stage} -> {full_path}')
        