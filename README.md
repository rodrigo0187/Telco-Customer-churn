# Telco-Customer-churn

Estructura para la gestión de datos para la IA
Este proyecto tiene como objetivo configurar un entorno para el desarrollo de soluciones en analisis de datos e inteligencia artificial.
La cual se integran herramientas como, GitHub, Codespaces, Docker y render, lo que garantiza un enterno , escalable , reproducible y automatizado.

### Arquitectura

Se integra una arquitectura de tipo pipelin híbrida modular, donde el flujo de trabajo o de datos se manifiesta de la siguiente manera;

- ingesta de datos
- procesamiento de datos
- modelo de la IA
- Exposicion mediante la API

### Esto nos garantiza separar las responsabilidade y la escalabilidad del sistema.

## Tecnologías

- Python
- Docker
- GitHub
- Github Codespace
- render

# Contenerización

Se utiliza docker para empaquetar la aplicación y empaquetar sus dependencias todo en un solo contendor, facilitando su ejecucion en cualquier entorno sin problemas de configuración.

## Ejecución

- Clonar repositorio desde GitHub

1. clonar repositorio
   git clone <URL>

2. construir imagen docker
   docker build -t mi-app .

3. ejecución del contenedor
   docker run -p 5000:5000 mi-app

# Despliegue

La aplicación puede ser desplegada en la nube utilizando render , el acceso debe ser inmediato ya que la URL debe ser pública.

# Estructura de los directorios

## ingestion

Módulo encargada en la obtención de los datos(crudos).
(Entrada de los datos en crudo)

## Processing

Módulo de la limpieza y transformación de los datos.
(Limpieza / transformación / limpieza de los datos)

## Model

Módulo donde se aplica la logica de la inteligencia artificial(IA)
logica de la IA / expone la IA

## app.py

punto de entrada de la aplicación
