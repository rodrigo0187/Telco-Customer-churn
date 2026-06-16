import os
import pickle
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from src.utils.logging import get_logger

logger = get_logger('train_model')


def train_model():    
    """Ejecuta el pipeline de entrenamiento para el modelo de predicción de Churn.

    Carga los datos preprocesados de la empresa, genera un análisis visual 
    de la distribución de las clases, realiza una división estratificada 
    para pruebas y entrena un clasificador RandomForest robusto con pesos 
    balanceados. Finalmente, serializa el modelo entrenado.

    Args:
        None: La función lee los parámetros de las rutas estáticas definidas 
            en su cuerpo ('data/processed/encoded/encoded_churn.csv').

    Returns:
        None: No retorna ningún objeto en memoria. Como efecto secundario, 
            genera y guarda los archivos 'data/processed/X_test.csv', 'data/processed/y_test.csv',
            'results/distribución_clases.png' y 'models/modelo_churn.pkl'.
    """
    DATA_PATH = 'data/processed/encoded/encoded_churn.csv'
    RESULTS_DIR = 'results'
    MODEL_DIR = 'models'
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    logger.info('Cargando datos procesados de churn')
    
    if not os.path.exists(DATA_PATH):
        logger.error(f'No se encontró el dataset en {DATA_PATH}')
        raise FileNotFoundError(f'Archivo requerido ausente: {DATA_PATH}')
    
    data = pd.read_csv(DATA_PATH)
    
    # Separación de target y característica
    target = 'churn'
    X = data.drop(columns=[target, 'customerid'], errors='ignore')
    y = data[target]
    
    # Graficar 
    logger.info('Distribucion de clientes')
    data[target].value_counts().plot(
        kind='pie',
        autopct='%1.1f%%',
        labels=['Se Queda (0)', 'Se Va (1)'],
        colors=['#2ecc71', '#e74c3c'],
        figsize=(6, 6)
    )
    plt.title('Distribución de clientes churn (Churn vs Retención)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'distribución_clases.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # División estratificada (80% entrenamiento y 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=29, stratify=y
    )
    X_test.to_csv('data/processed/X_test.csv', index=False)
    y_test.to_csv('data/processed/y_test.csv', index=False)
    
    # Pipeline y configuración del Bosque aleatorio
    logger.info('Entrenamiento del clasificador de bosque aleatorio')
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=29,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    pipeline = Pipeline([
        ('classifier', model)
    ])
    pipeline.fit(X_train, y_train)
    
    # Guardar el modelo en la ruta model
    MODEL_OUTPUT = os.path.join(MODEL_DIR, 'modelo_churn.pkl')
    with open(MODEL_OUTPUT, 'wb') as f:
        pickle.dump(pipeline, f)
        logger.info(f'Exito! modelo almacenado en {MODEL_OUTPUT}')


if __name__ == '__main__':
    train_model()