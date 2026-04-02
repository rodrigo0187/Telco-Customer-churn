# Telco Customer Churn

## Descripción
El sistema permite predecir la probabilidad de que un cliente abandone el servicio (churn) en una empresa de telecomunicaciones, utilizando técnicas de machine learning a partir de datos históricos de clientes. El sistema ingesta los datos, los procesa, limpia, transforma y analiza la información para generar predicciones que luego pueden ser consumidas a través de una API. Además, el proyecto es reproducible y escalable.

Integra herramientas como GitHub, Codespaces, Docker y Render, garantizando un entorno:

- escalable
- reproducible
- automatizado

## Estructura del proyecto (collapse)
```
/root
├── README.md
├── docs/
├── └── documento_tecnico.pdf
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
- Almacenamiento (Storage)
- Modelo de IA (Model)
- Exposición mediante API

Esto permite la separación de responsabilidades y la escalabilidad del sistema.

---

## Tecnologías y Librerías

### Lenguaje

- Python 3.x

### Machine Learning

- scikit-learn: entrenamiento, evaluación y pipelines

### Librerías
- Las versiones indicadas son referenciales y pueden cambiar con el tiempo; se recomienda validarlas y ajustar según el entorno y las dependencias del proyecto.
  
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

## Ejecución sin instalación

El proyecto puede ejecutarse sin necesidad de instalar dependencias localmente utilizando Docker.  
Todo el entorno (librerías, configuración y aplicación) se encuentra contenido dentro de la imagen.

Una vez levantado el contenedor, la aplicación quedará disponible localmente en:

http://localhost:5000

### 1. Clonar repositorio

```
git clone https://github.com/rodrigo0187/Telco-Customer-churn.git

```

### 2. Construir imagen docker

```
   docker build -t mi-app .

```

### 3. Ejecutar contenedor

```
docker run -p 5000:5000 mi-app

```

---
# Ejecución local con Windows y linux
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

Se utiliza versionado semántico vMAJOR.MINOR.PATCH
ejemplo v.1.0.0

---

### Flujo de Datos (Pipeline)

**Ingestion**

Módulo encargado de la obtención de datos crudos desde archivos .csv mediante procesamiento batch.

lectura de archivos CSV
validación básica de estructura y formato
manejo de errores de lectura
carga inicial de datos a la base de datos

---

**Cleaning**

Módulo encargado de la limpieza y consistencia de los datos.

eliminación de valores nulos
eliminación de duplicados
corrección de tipos de datos

---

**Feature Engineering**

Módulo encargado de transformar los datos en variables útiles para el modelo.

encoding de variables categóricas
normalización / scaling
creación de nuevas variables

---

**Data Storage (PostgreSQL)**

Módulo encargado del almacenamiento de datos.

datos crudos
datos procesados
features

---

**Model**

Módulo encargado del entrenamiento y predicción del modelo de churn.

---

app.py

Punto de entrada de la aplicación que expone el modelo mediante endpoints.

### Estructura del proyecto (expand)

```bash
/root
├── README.md
├── docs/
├── └── documento_tecnico.pdf
src/
│
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
├── storage/
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

[Para más información visita el siguiente enlace](https://github.com/rodrigo0187/Telco-Customer-churn/blob/main/root/docs/Documento_Diseno_técnico.pdf#Para más información visita el siguiente enlace)
---
## Integrantes 
- Rodrigo Ignacio Aedo Contreras
- Benjamín Jesús Figueroa Poblete
