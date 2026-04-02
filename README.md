# Telco Customer Churn


## Descripción

El sistema permite predecir la probabilidad de que un cliente abandone el servicio(Churn) en una empresa de telecomunicaciones utilizando técnicas de machine learning, a apartir de datos historicos de clientes. El sistema ingesta los datos, procesa ,limpia ,transforma y analiza la información para generar predicciones que luego pueden ser consumidas a trávez de API.
Ademas, el proyecto es reproducible y escalable.

Integra herramientas como GitHub, Codespaces, Docker y Render, garantizando un entorno:

- escalable
- reproducible
- automatizado
## Estructura del proyecto
```
src/
├── ingestion/
├── cleaning/
├── feature_engineering/
├── storage/
├── model/
└── pipeline.py

```

---

## Arquitectura

Se implementa una arquitectura de tipo pipeline híbrida modular, donde el flujo de datos se organiza de la siguiente forma:

- Ingesta de datos (Ingestion)
- Limpieza de datos (Cleaning)
- Transformación (Feature Engineering)
- Almacenamiento (storage)
- Modelo de IA (Model)
- Exposición mediante API

Esto permite la separación de responsabilidades y la escalabilidad del sistema.

---

## Tecnologías y Librerías

### Lenguaje

- Python 3.x

### Machine Learning

- scikit-learn: entrenamiento, evaluación y pipelines

### Testing

- pytest: pruebas unitarias e integración

### Librerias

- Pandas 3.0.x
- Scikit 1.7.x
- Numpy 2.3.4
- Scipy 1.16.3
- joblib 1.5.2

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

# Ejecución con Docker

### 1. Clonar repositorio

```
git clone https://github.com/rodrigo0187/Telco-Customer-churn.git

```

### 2. construir imagen docker

```
   docker build -t mi-app .

```

### 3. ejecutar contenedor

```
docker run -p 5000:5000 mi-app .

```

---
# Ejecucion local con Windows y linux
```
# crear entorno virtual
python -m venv venv

# activar entorno
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# instalar dependencias
pip install -r requirements.txt

# ejecutar aplicación
python app.py

```
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

```bash
src/
├── Documento_técnico.pdf
|
├── ingestion/
│   └── load_csv.py
│
├── cleaning/
│   ├── fix_data_types.py
│   ├── remove_duplicates.py
│   └── remove_nulls.py
│
├── feature_engineering/
│   ├── encoding.py
│   ├── feature_creation.py
│   └── scaling.py
│
├── storage
│   ├── load_bd.py
│   └── storage_bd.py
│
├── model/
│   ├── train.py
│   ├── predict.py
│   └── evaluate.py
│
│
└── pipeline.py  # Orquestador del flujo de datos
```
---
## Enlace del Documento Técnico
[Para más informacion visita la documentación]('https://docs.google.com/document/d/1sDkir-LdEzf7WIuoey8irOKEiO-2Y4m_5qQb3kaK1L4/edit?usp=sharing')

---
## Integrantes

- Rodrigo Ignacio Aedo Contreras
- Benjamín Jesús Figueroa Poblete
