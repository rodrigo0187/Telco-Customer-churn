FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias Python
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Comando por defecto (puede ser sobreescrito por docker-compose)
CMD ["python"]