# Modelo predictivo de riesgo de abandono de clientes en servicios de telecomunicaciones

## Descripción

El sistema permite predecir la probabilidad de que un cliente abandone el servicio (churn) en una empresa de telecomunicaciones, utilizando técnicas de machine learning a partir de datos históricos.

El sistema:

- ingesta datos
- procesa
- limpia
- transforma
- genera predicciones

Además, el proyecto es reproducible y escalable.

Integra herramientas como:

- GitHub
- Docker
- Render

---

## Estructura del proyecto

```bash
telco-customer-churn/
├── data/
├── db/
├── documentation/
├── root/
│   └── docs/
├── src/
│   ├── cleaning/
│   ├── data/
│   ├── feature_engineering/
│   ├── ingestion/
│   ├── model/
│   ├── storage/
│   ├── utils/
│   └── pipeline.
│
├── test/
│   └── test_modelo.py
│
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Arquitectura

Arquitectura tipo **pipeline híbrido modular (batch)**:

- Ingestion
- Cleaning
- Feature Engineering
- Storage
- Model

Permite:

- separación de responsabilidades
- escalabilidad  
- mantenibilidad  

---

## Tecnologías

### Lenguaje

- Python 3.x

### Librerías

- Las versiones indicadas son referenciales y pueden cambiar con el tiempo; se recomienda validarlas y ajustar según el entorno y las dependencias del proyecto.

- Scikit 1.4.2 [Scikit](https://scikit-learn.org/stable/install.html)
- Pandas 2.2.2 [Pandas](https://pandas.pydata.org/docs/getting_started/install.html)
- Numpy 2.4.4 [Numpy](https://numpy.org/install/)
- Seaborn 0.13.2 [Seaborn](https://seaborn.pydata.org/installing.html)
- psycopg2-binary 2.9.9 [Psycopg2](https://pypi.org/project/psycopg2-binary/)
- sqlalchemy 2.0.49 [SqlAlchemy](https://pypi.org/project/SQLAlchemy/)
- python-dotenv 1.2.2 [Python-dotenv](https://pypi.org/project/python-dotenv/)

### Base de datos

- PostgreSQL

### Contenerización

- Docker

### Control de versiones

- Git / GitHub / GitHub Actions: automatización de flujos (CI/CD)

---

## Ejecución con Docker (Recomendado)

## Requisitos

- Docker

---

## 1. Clonar repositorio

```bash
git clone https://github.com/rodrigo0187/Telco-Customer-churn.git
cd Telco-Customer-churn
```

---

## 2. Configurar entorno

Crear archivo `.env` en la raíz:

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=churn_db

DB_HOST=db
DB_PORT=5432
```

---

## 3. Ejecutar pipeline

```bash
docker-compose up --build
```

---

## 4. Verificar datos en PostgreSQL

```bash
docker exec -it postgres_churn psql -U admin -d churn_db
```

ver tabla

```bash
\d {nombre_tabla}
```

Dentro de PostgreSQL:

```sql
SELECT COUNT(*) FROM cliente;
SELECT * FROM cliente LIMIT 10;
```

---

## 5. Detener servicios

```bash
docker-compose stop
docker-compose down
```

## 6. Crea nuevamente el contenedor o encender contenedor ya creado

```bash
docker-compose up
docker-compose start
```

## 7. Elimina y detiene contenedor,volúmenes

> Elimina toda la base de datos, tablas, registro y conexion creada

```bash
docker-compose down -v
```

---

## Ejecución sin Docker

## Requisitos sin docker

- Python 3.x
- PostgreSQL

---

## 1. Crear entorno virtual

```bash
python -m venv venv
```

Activar:

```bash
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

---

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Configurar base de datos

```sql
CREATE DATABASE churn_db;
```

```bash
psql -U admin -d churn_db -f db/init.sql
```

---

## 4. Ejecutar pipeline

```bash
python src/pipeline.py
```

---

## Validación

La tabla `cliente` debe contener en crudo **7043 registros** con **21 columnas**

---

## Despliegue

- Render: despliegue en la nube mediante URL pública

---

## Flujo del pipeline

### Ingestion

- load_csv.py, realiza la carga de un archivo CSV tanto local(data/raw) como en la nube(OneDrive).

### Cleaning

- duplicates, consolida registros ducplicados basados en el id, garantizando un id unico.
- normalize_text, normaliza y unifica las columnas de tipo texto en el DataFrame
- null , identifica e imputa valores faltantes
- quality_check (calidad de los datos)
- types(fix_data_types), corrige los tipos de datos incorrectos del DataFrame

### Feature Engineering

- creation_features, Genera variables categóricas, numéricas e interecciones de negocio para el modelo churn.
- encoding, orquesta la preparacion final y códifica las variables categóricas a numéricas.

### Model

predict, evalua el rendimiento del modelo serializado utilizando datos no vistos.
train, ejecuta el pipeline de entramiento para posteriormente generar un análisis visual.
verificacion_cm, Carga el modelo entrenado y los datos de prueba para graficar la Matriz de Confusión.

### Storage

- load_db.py, Genera un motor (engine) de conexión para una base de datos PostgreSQL.

### Utils

- categorical_null,Calcula la proporción de valores nulos especificamente en las columnas categóricas.
- inconsistencies_cat,Detecta de forma temprana si existen inconsistencias de formato en columnas categóricas.
- logging,Configura y retorna un objeto Logger unificado para la aplicación.
- negative_values,Analiza si existen valores negativos en las columnas numéricas del DataFrame.
- outliers,Analiza si existen valores atípicos en las columnas numéricas usando el método IQR.
- saved_dataset,Guarda del DataFrame en formato csv dentro de la ruta correpondiente a su etapa.
- schema_validator,Audita la estructura y el contrato de datos del dataset frente al esquema esperado.

---

## Archivos importantes

- `.dockerignore` → excluye archivos del contenedor  
- `.env` → variables de entorno (no versionado)  
- `.gitignore` → archivos ignorados por git  
- `Dockerfile` → construcción de imagen  
- `docker-compose.yml` → orquestación  
- `pipeline.py` → orquestador del flujo  
- `requirements.txt` → dependencias  
- `render.yaml`-> despliegue

---

## Documento técnico

[Documento Técnico](https://github.com/rodrigo0187/Telco-Customer-churn/blob/main/root/docs/Documento_Diseno_T%C3%A9cnico.pdf)

---

### Estructura del proyecto (expand)

```bash
Telco-customer-churn

├── .github/workflows/
│    └── ci_cd.yaml # Entorno de configuración para la implementación de GitHub Actions
│
├── data/
│   ├── backup/
│   │   ├── raw # backup de churn con timestamp
│   │   └── churn.csv # csv crudo
│   │   
│   │   # Trazabilidad cleaned y feature_engineered se crean archivos csv por etapas de processed
│   ├── processed/
│   │    ├── cleaned/
│   │    │   └── cleaned_churn.csv
│   │    │
│   │    ├── encoded/
│   │    │   └── encoded_churn.csv
│   │    │
│   │    ├── feature_engineering/
│   │    │   └── fe_.csv # pendiente
│   │    │
│   │    └── winsorized/
│   │        └── winsorized_churn.csv
│   │
│   └── raw/
│        └── churn.py
│
├── db/
├── └── init.sql # construccion de la tabla
│
│
├── documentation/
│   └── html/index.html # pagina de documentación Docstring
│
├── models/
├── └── modelo_churn.pkl
│   # se crearán las img con resultados de aprendizajes
├── results/
│    ├── curva_roc.png
│    ├── distribucion_clases.png
│    ├── importancia_variables.png
│    ├── matriz_confusion.png
│    └── metricas.json
│
├── root/
│   └── docs
│   │   ├── Documento_Diseno_Técnico.pdf
│   │   └── diccionario_Metadata.txt
│   │
├── src/
│   │
│   ├── cleaning/
│   │   ├── duplicates.py
│   │   ├── normalize_text.py
│   │   ├── null.py
│   │   ├── quality_check.py
│   │   └── types.py
│   │
│   ├── feature_engineering/
│   │    ├── create_features.py
│   │    ├── encoding.py
│   │    └── handle_nulls_post_fe.py
│   │
│   │
│   ├── ingestion/
│   │   └── load_csv.py
│   │
│   ├── model/
│   │   ├── preprocessing/
│   │   │   ├── impute_categoric_null.py 
│   │   │   ├── impute_numeric_null.py 
│   │   │   ├── scaling.py 
│   │   │   └── winsorizer.py
│   │   │  
│   │   ├── predict.py
│   │   ├── train.py
│   │   └── verificacion_cm
│   │
│   ├── storage/
│   │   └──load_bd.py
│   │   
│   ├── utils/
│   │   ├── inconsistencies_cat.py
│   │   ├── logging.py # registro de logs (como opción futura)
│   │   ├── negative_values.py
│   │   ├── outliers.py
│   │   └── saved_dataset.py # Trazabilidad [persistencia]
│   │
│   └── pipeline.py  # Orquestador del flujo de datos
│
├── test/
│    └── test_modelo.py
│
├── .dockerignore
├── .env
├── .env.example # ejemplo de configuracion de credenciales
├── .gitignore
├── app.py # archivo principal de la aplicación
├── docker-compose.yml # orquestador de los contenedores
├── Dockerfile
├── README.md
├── render.yaml
└── requirements.txt

```

## Autores

- Rodrigo Ignacio Aedo Contreras  
- Benjamín Jesús Figueroa Poblete
