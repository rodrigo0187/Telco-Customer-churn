FROM python:3.11-slim

# Evita que Python escriba archivos .pyc en disco y asegura salida de logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Instalar dependencias del sistema esenciales para compilar/correr Postgres si fuesen necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python aprovechando la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Crear directorios clave para asegurar permisos correctos en los montajes de volúmenes
RUN mkdir -p data/raw data/backup/raw results models

EXPOSE 10000

# Comando por defecto (Ideal para Render, Docker Compose lo puede sobrescribir)
CMD ["streamlit", "run", "app.py", "--server.port", "10000", "--server.address", "0.0.0.0"]