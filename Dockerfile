FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema operativo para PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo (incluye las carpetas de código y datos de GitHub)
COPY . .

# Exponer el puerto de Streamlit
EXPOSE 10000

# Comando de arranque por defecto para Render
CMD ["streamlit", "run", "app.py", "--server.port", "10000", "--server.address", "0.0.0.0"]