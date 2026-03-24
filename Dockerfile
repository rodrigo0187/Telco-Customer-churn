# definicion de la imagen base
FROM python:3.14
# establecer el directorio de trabajo dentro del contenedor
WORKDIR /app
# copiar el archivo de requisitos y instalar las dependencias
COPY requirements.txt .
# instalar las dependencias del proyecto
RUN pip install -r requirements.txt
# copiar el resto de los archivos del proyecto al contenedor
COPY . .
# exponer el puerto en el que la aplicación se ejecutará
EXPOSE 5000
# comando para ejecutar la aplicación
CMD ["python", "app.py"]