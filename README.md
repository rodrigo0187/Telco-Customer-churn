# Modelo predictivo de riesgo de abandono de clientes en servicios de telecomunicaciones

## Descripción

El sistema permite predecir la probabilidad de que un cliente abandone el servicio (churn) en una empresa de telecomunicaciones, utilizando técnicas de machine learning a partir de datos históricos de clientes. El sistema ingesta los datos, los procesa, limpia, transforma y analiza la información para generar predicciones que luego pueden ser consumidas a través de una API. Además, el proyecto es reproducible y escalable.

Integra herramientas como GitHub, Codespaces, Docker y Render, garantizando un entorno:

- escalable
- reproducible
- automatizado

## Estructura del proyecto (collapse)

```/root
├── docs/
├── └── documento_tecnico.pdf
src/
├── ingestion/
├── cleaning/
├── feature_engineering/
├── storage/
├── model/
├── .dockerignore
├── .env
├── .gitignore
├── app.py
├── Dockerfile
├── README.md
└── requirements.txt

```

---

## Arquitectura

Se implementa una arquitectura de tipo pipeline híbrida modular, el flujo de datos se organiza por capas funcionales:

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

- Python 3.x    [Python](https://www.python.org/downloads/)

### Machine Learning

- scikit-learn: entrenamiento, evaluación y pipelines

### Librerías  

- Las versiones indicadas son referenciales y pueden cambiar con el tiempo; se recomienda validarlas y ajustar según el entorno y las dependencias del proyecto.
  
- Pandas 3.0.x    [Pandas](https://pandas.pydata.org/docs/getting_started/install.html)
- Scikit 1.7.x    [Scikit](https://scikit-learn.org/stable/install.html)
- Numpy 2.3.4     [Numpy](https://numpy.org/install/)
- Scipy 1.16.3    [Scipy](https://scipy.org/install/)

### Contenerización

- Docker: empaquetado de la aplicación

### Control de versiones y CI/CD

- Git: control de versiones
- GitHub: repositorio
- GitHub Actions: automatización de flujos (CI/CD)

## Despliegue aplicación

- Render: despliegue automático de la aplicación en la nube

### Base de datos

- PostgreSQL: almacenamiento de datos y features

---

## Ejecución con Docker

## Ejecución sin instalación

El proyecto puede ejecutarse sin necesidad de instalar dependencias localmente utilizando Docker.  
Todo el entorno (librerías, configuración y aplicación) se encuentra contenido dentro de la imagen.

Una vez levantado el contenedor, la aplicación quedará disponible localmente en:

<http://localhost:5000>

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

## Ejecución local con Windows y linux

```# crear entorno virtual
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

## Despliegue

1. La aplicación puede ser desplegada en la nube utilizando Render.
2. El acceso se realiza mediante una URL pública.

---

## Versionado

1. Se utiliza versionado semántico vMAJOR.MINOR.PATCH ejemplo v.1.0.0

---

### Flujo de Datos (Pipeline)

## Ingestion

1. Módulo encargado de la obtención de datos crudos desde archivos .csv mediante procesamiento batch.
      1. lectura de archivos CSV
      2. validación básica de estructura y formato
      3. manejo de errores de lectura
      4. carga inicial de datos a la base de datos

---

## Cleaning

1. Módulo encargado de la limpieza y consistencia de los datos.
      1. eliminación de valores nulos
      2. eliminación de duplicados
      3. corrección de tipos de datos

---

## Feature Engineering

1. Módulo encargado de transformar los datos en variables útiles para el modelo.
      1. encoding de variables categóricas
      2. normalización / scaling
      3. creación de nuevas variables

---

## Storage (PostgreSQL)

1. Módulo encargado del almacenamiento de datos.

      1. datos crudos
      2. datos procesados
      3. features

---

## Model

1. Módulo encargado de:
      1. entrenamiento
      2. predicción

---

## Archivos

1. .dockerignore
      - Docker utiliza este archivo, para excluir archivos y carpetas al momento de construir el contenedor

2. .env
      - Archivo de configuracion que almacena las variables de entorno

3. .gitignore
      - Archivo que le indica a git, qué archivos no debe versionar

4. Dockerfile
      - Archivo que indica cómo construir una imagen docker de la aplicación

5. README.md
      - Archivo contiene las descripciónes del sistema, instrucciones de ejecución, arquitectura y tecnologias usadas en el sistema

6. requirements.txt
      - Archivo que contiene las dependencias de python del proyecto

7. app.py
      - Archivo principal de la aplicación

8. pipeline.py
      - Orquestador del flujo de datos, que ejecuta las diferentes etapas del pipeline

### Estructura del proyecto (expand)

```bash
/root
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
├── .dockerignore
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── app.py # archivo principal de la aplicación
├── requirements.txt
└── pipeline.py  # Orquestador del flujo de datos
```

[Visita el Documento Diseño técnico](https://github.com/rodrigo0187/Telco-Customer-churn/blob/main/root/docs/Documento_Diseno_T%C3%A9cnico.pdf)

---

## Autores

- Rodrigo Ignacio Aedo Contreras
- Benjamín Jesús Figueroa Poblete
