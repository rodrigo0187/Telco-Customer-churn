#------------------------
#Entrenamiento del modelo
#------------------------
import pandas as pd
import os
import matplotlib.pyplot as plt


#---CREAR CARPETA "results"---
RESULTS_DIR= "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

#---CARGAR DATOS---
data = pd.read_csv(data/backup/raw/churn_20260609_191546.csv)

#--Variable Objetivo--
churn= "Yes"

X= data.drop(columns=[churn])
Y= data[churn]

#---REVISA LA DISTRIBUCIÓN DE L A VARIABLE OBJETIVO---

#--Crear un gráfico de torta--
data[churn].value_counts().plot(kind='pie', autopct='%1.1f%%',
                                labels=['No renuncia', 'Sí renuncia'],
                                figsize=(6, 6))
plt.title("Distribución de variable objetivo", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(
    os.path.join(RESULTS_DIR, "distribucion_clases.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()



