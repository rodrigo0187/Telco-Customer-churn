import pickle
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.tree import plot_tree

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
    roc_curve
)

def evaluate_model():
    """Evalúa el rendimiento del modelo serializado utilizando datos no vistos.

    Carga las características y etiquetas de prueba guardadas previamente, 
    descongela el pipeline del modelo RandomForest y calcula métricas clave de 
    clasificación (F1-Score, Recall, Precisión, Accuracy y ROC-AUC). Genera 
    reportes detallados en consola y exporta curvas de diagnóstico junto con 
    un análisis de importancia de variables (Feature Importance).

    Args:
        None: Consume los archivos de datos de prueba y el modelo serializado 
            directamente desde las rutas relativas estándar del proyecto 
            ('data/processed/X_test.csv', 'data/processed/y_test.csv' y 'models/modelo_churn.pkl').

    Returns:
        None: No retorna valores en memoria. Como efecto secundario, exporta 
            a la carpeta 'results/' los gráficos 'matriz_confusion.png', 
            'curva_roc.png', 'importancia_variables.png' y el archivo 
            estructurado 'metricas.json'.
    """    
    RESULTS_DIR = "results"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print(" Loading test datasets...")
    X_test = pd.read_csv("data/processed/X_test.csv")
    Y_test = pd.read_csv("data/processed/Y_test.csv").squeeze()
    
    MODEL_PATH = "models/modelo_churn.pkl"
    print(f" Loading model from: {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    
    # 1. Ejecutar inferencia (Predicciones y Probabilidades)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # 2. Cálculo de Métricas Clave
    accuracy = accuracy_score(Y_test, y_pred)
    precision = precision_score(Y_test, y_pred)
    recall = recall_score(Y_test, y_pred)
    f1 = f1_score(Y_test, y_pred)
    roc_auc = roc_auc_score(Y_test, y_prob)
    
    print(" «« CLASIFICACIÓN MÉTRICAS »» ")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")
    
    print(" «« DETALLE REPORTE »» ")
    print(classification_report(Y_test, y_pred, target_names=["Retained", "Churn"]))
    
    # 3. Gráfico de Matriz de Confusión Visual
    cm = confusion_matrix(Y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Retained (0)", "Churn (1)"],
        yticklabels=["Retained (0)", "Churn (1)"]
    )
    plt.title("Matriz de Confusión - Churn", fontsize=14, fontweight="bold")
    plt.xlabel("Predicción del Modelo", fontsize=12, fontweight="bold")
    plt.ylabel("Valor Real (Ground Truth)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "matriz_confusion.png"), dpi=300)
    plt.close()
    
    # 4. Gráfico Curva ROC
    fpr, tpr, _ = roc_curve(Y_test, y_prob)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', label=f"AUC = {roc_auc:.4f}")
    plt.plot([0, 1], [0, 1], color='navy', linestyle="--")
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("Curva ROC - Diagnóstico de Churn", fontsize=14, fontweight="bold")
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(RESULTS_DIR, "curva_roc.png"), dpi=300)
    plt.close()
    
    # 5. Análisis de Importancia de Variables (Feature Importance)
    rf_model = model.named_steps["classifier"]
    feature_names = X_test.columns.tolist()
    importances = rf_model.feature_importances_
    
    importance_data = pd.DataFrame({
        "Variable": feature_names,
        "Importancia": importances
    }).sort_values(by="Importancia", ascending=False)
    
    print("VARIABLES MÁS PREDICTIVAS")
    print(importance_data.head(5).to_string(index=False))
    
    # Gráfico de barras horizontales de importancia
    plt.figure(figsize=(10, 8))
    sns.barplot(data=importance_data.head(15), x="Importancia", y="Variable",hue='Variable',legend=False)
    plt.title("Top 15 Variables que deciden el Churn", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "importancia_variables.png"), dpi=300)
    plt.close()
    
    print("Generación arbol de decisión")
    arbol_individual = rf_model.estimators_[0]
    
    plt.figure(figsize=(20,10))
    plot_tree(
        arbol_individual,
        max_depth=3,
        feature_names=feature_names,
        class_names=["Retaind (0)","Churn (1)"],
        filled=True,
        rounded=True,
        fontsize=10    
    )
    plt.title('Estructura individual del Bosque (Profundidad Maxima 3)')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR,'arbol_decision.png'),dpi=300,bbox_inches='tight')
    plt.close()
    
    
    # 6. Almacenar Métricas en JSON para auditoría futura
    metricas = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "classification_report": classification_report(Y_test, y_pred, output_dict=True)
    }
    with open(os.path.join(RESULTS_DIR, "metricas.json"), "w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=4, ensure_ascii=False)
    print("\n Métricas guardadas exitosamente en results/metricas.json")

if __name__ == "__main__":
    evaluate_model()