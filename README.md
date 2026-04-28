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

##  Estructura del proyecto

```bash
telco-customer-churn/
├── db/
├── root/
│   └── docs/
├── src/
│   ├── cleaning/
│   ├── data/
│   ├── feature_engineering/
│   ├── ingestion/
│   ├── model/
│   ├── storage/
│   └── pipeline.py
├── .dockerignore
├── .env
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

##  Arquitectura

Arquitectura tipo **pipeline híbrido modular (batch)**:

- Ingestion
- Cleaning
- Feature Engineering
- Storage
- Model
- API

Permite:
- separación de responsabilidades  
- escalabilidad  
- mantenibilidad  

---

##  Tecnologías

### Lenguaje
- Python 3.x

### Librerías
- pandas
- numpy
- scikit-learn
- seaborn
- psycopg2-binary
- sqlalchemy
- python-dotenv

### Base de datos
- PostgreSQL

### Contenerización
- Docker

### Control de versiones
- Git / GitHub

---

#  Ejecución con Docker (Recomendado)

## Requisitos
- Docker
- Docker Compose

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

Dentro de PostgreSQL:

```sql
SELECT COUNT(*) FROM cliente;
SELECT * FROM cliente LIMIT 10;
```

---

## 5. Detener servicios

```bash
docker-compose down
```

> Para eliminar datos:
```bash
docker-compose down -v
```

---

# Ejecución sin Docker

## Requisitos
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

La tabla `cliente` debería contener aproximadamente **7000 registros**.

---

## Despliegue

- Render: despliegue en la nube mediante URL pública

---

## Flujo del pipeline

### Ingestion
- lectura CSV
- validación
- carga inicial

### Cleaning
- eliminación de nulos
- eliminación de duplicados
- corrección de tipos

### Feature Engineering
- encoding
- scaling
- nuevas variables

### Storage
- almacenamiento en PostgreSQL

### Model
- entrenamiento
- predicción

---

## Archivos importantes

- `.dockerignore` → excluye archivos del contenedor  
- `.env` → variables de entorno (no versionado)  
- `.gitignore` → archivos ignorados por git  
- `Dockerfile` → construcción de imagen  
- `docker-compose.yml` → orquestación  
- `pipeline.py` → orquestador del flujo  
- `requirements.txt` → dependencias  

---

## Documento técnico

https://github.com/rodrigo0187/Telco-Customer-churn/blob/main/root/docs/Documento_Diseno_T%C3%A9cnico.pdf

---

## Autores

- Rodrigo Ignacio Aedo Contreras  
- Benjamín Jesús Figueroa Poblete