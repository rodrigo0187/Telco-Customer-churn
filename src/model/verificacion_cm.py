import os
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix
from src.utils.logging import get_logger

logger = get_logger('graficar_matriz_real')

# Definir rutas de los archivos generados por tu pipeline
X_TEST_PATH = 'data/processed/X_test.csv'
Y_TEST_PATH = 'data/processed/Y_test.csv'
MODEL_PATH = 'models/modelo_churn.pkl'

def graficar_matriz_real():
    # Verificar que los archivos existan
    if not all(os.path.exists(p) for p in [X_TEST_PATH, Y_TEST_PATH, MODEL_PATH]):
        logger.error("Asegúrate de haber corrido el docker-compose para generar los archivos.")
        return

    # 2. Cargar los datos de prueba y el modelo entrenado
    X_test = pd.read_csv(X_TEST_PATH)
    Y_test = pd.read_csv(Y_TEST_PATH)
    
    with open(MODEL_PATH, 'rb') as f:
        pipeline = pickle.load(f)

    # 3. Hacer las predicciones con el modelo descongelado
    y_pred = pipeline.predict(X_test)

    # 4. Calcular la matriz de confusión matemática
    cm = confusion_matrix(Y_test, y_pred)
    
    # 5. Diseñar el gráfico visual (Mapa de Calor)
    plt.figure(figsize=(7, 5))
    sns.heatmap(
        cm, 
        annot=True,          # Muestra los números dentro de los cuadros
        fmt='d',             # Formato de número entero (evita notación científica)
        cmap='Blues',        # Paleta de colores degradados en azul
        xticklabels=['Retained (0)', 'Churn (1)'],
        yticklabels=['Retained (0)', 'Churn (1)']
    )
    
    # Formatear el diseño
    plt.title('Matriz de Confusión Real - Predicción de Churn', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Predicción del Modelo', fontsize=10, labelpad=10)
    plt.ylabel('Realidad del Cliente', fontsize=10, labelpad=10)
    plt.tight_layout()
    
    # Mostrar en pantalla
    logger.info("Matriz de Confusión en pantalla!")
    plt.show()

if __name__ == '__main__':
    graficar_matriz_real()