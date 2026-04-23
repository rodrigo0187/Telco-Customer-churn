# 1. Usar una imagen ligera de Python
FROM python:3.11-slim

# 2. Instalar dependencias del sistema necesarias para Postgres (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Copiar e instalar requisitos
# Aprovechamos el sistema de capas de Docker para no reinstalar todo cada vez
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el contenido del proyecto
COPY . .

# 6. Comando para ejecutar tu script de ingesta específicamente
# Como tu script está en ingestion/load_bd.py:
CMD ["python", "ingestion/load_bd.py"]