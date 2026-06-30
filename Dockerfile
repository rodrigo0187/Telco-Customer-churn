FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias Python
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Exponer el puerto en el contenedor
EXPOSE 10000

# Comando por defecto al levantar el contenedor
CMD ["streamlit", "run", "app.py", "--server.port", "10000", "--server.address", "0.0.0.0"]