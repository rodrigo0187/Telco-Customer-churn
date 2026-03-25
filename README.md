# Telco Customer Churn

## Descripción

Este proyecto tiene como objetivo configurar un entorno para el desarrollo de soluciones de análisis de datos e inteligencia artificial.

Integra herramientas como GitHub, Codespaces, Docker y Render, garantizando un entorno:

- escalable
- reproducible
- automatizado

---

## Arquitectura

Se implementa una arquitectura de tipo pipeline híbrida modular, donde el flujo de datos se organiza de la siguiente forma:

- Ingesta de datos
- Procesamiento de datos
- Almacenamiento
- Modelo de IA
- Exposición mediante API

Esto permite la separación de responsabilidades y la escalabilidad del sistema.

---

## Tecnologías y Librerías

### Lenguaje

- Python 3.x

### Machine Learning

- scikit-learn: entrenamiento, evaluación y pipelines

### Procesamiento de datos

- pandas
- numpy

### Testing

- pytest: pruebas unitarias e integración

### Contenerización

- Docker: empaquetado de la aplicación

### Control de versiones y CI/CD

- Git: control de versiones
- GitHub: repositorio
- GitHub Actions: automatización de flujos (CI/CD)

### Despliegue

- Render: despliegue automático

### Base de datos

- PostgreSQL: almacenamiento de datos

---

## Ejecución

### 1. Clonar repositorio

</>Bash , Terminal
git clone <URL>

### 2. construir imagen docker

</>Bash , Terminal
docker build -t mi-app .

### 3. ejecutar contenedor

docker run -p 5000:5000 mi-app .

---

### Despliegue

La aplicación puede ser desplegada en la nube utilizando Render.
El acceso se realiza mediante una URL pública.

---

### Versionado

Se utiliza versionado semantico vMAJOR.MINOR.PATCH
ejemplo v.1.0.0

---

### Flujo de Datos (Pipeline)

Ingestion

Módulo encargado de la obtención de datos crudos desde archivos .csv.

carga de datos desde CSV
carga inicial a base de datos

---

Cleaning

Módulo encargado de la limpieza y consistencia de los datos.

eliminación de valores nulos
eliminación de duplicados
corrección de tipos de datos

---

Feature Engineering

Módulo encargado de transformar los datos en variables útiles para el modelo.

encoding de variables categóricas
normalización / scaling
creación de nuevas variables

---

Data Storage (PostgreSQL)

Módulo encargado del almacenamiento de datos.

datos crudos
datos procesados
features

---

Model

Módulo encargado del entrenamiento y predicción del modelo de churn.

Testing

Módulo encargado de validar el correcto funcionamiento del sistema.

app.py

Punto de entrada de la aplicación que expone el modelo mediante endpoints.

src/
├── cleaning/
│ ├── fix_data_types.py
│ ├── remove_duplicates.py
│ └── remove_nulls.py
│
├── feature_engineering/
│ ├── encoding.py
│ ├── feature_creation.py
│ └── scaling.py
│
├── ingestion/
│ └── load_csv.py
│
├── model/
│ ├── train.py
│ ├── predict.py
│ └── evaluate.py
│
├── tests/
│ ├── test_cleaning.py
│ ├── test_features.py
│ ├── test_model.py
│ └── test_pipeline.py
│
└── pipeline.py # Orquestador del flujo de datos
