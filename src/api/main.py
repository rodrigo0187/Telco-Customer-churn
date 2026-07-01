from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
import json
from src.pipeline import main as ejecutar_pipeline
from src.utils.logging_config import get_logger

## @file main.py
#  @brief API de FastAPI para gestionar el Pipeline de Machine Learning de Churn.
#  @details Contiene los endpoints para recibir datasets, ejecutar procesos de entrenamiento y exponer métricas y gráficos.

logger = get_logger('fastapi_backend')

app = FastAPI(
    title="Churn ML Pipeline API",
    description="API para la ingesta de datos y re-entrenamiento del modelo de Churn",
    version="1.0.0"
)

# Carpeta donde tu pipeline almacena los reportes
RESULTS_DIR = "results"

# Asegurar que existan las carpetas en el contenedor de la API
os.makedirs("data/raw", exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


@app.get("/")
def read_root():
    """
    @brief Endpoint de verificación de estado (Health Check).
    
    @details Permite comprobar de manera rápida si el contenedor de la API está
             activo y respondiendo peticiones HTTP.

    @return dict Diccionario con el estado operativo ("online") y un mensaje de bienvenida.
    """
    return {"status": "online", "message": "API de Churn ML operativa"}


@app.post("/run-pipeline")
async def run_pipeline_endpoint(file: UploadFile = File(...)):
    """
    @brief Endpoint para la recepción de datos y ejecución del pipeline.
    
    @details Recibe un archivo en formato CSV cargado por el usuario, lo valida, 
             lo almacena de forma local en el contenedor dentro de 'data/raw' 
             y gatilla secuencialmente todo el pipeline de Machine Learning 
             (Ingesta de datos, base de datos y re-entrenamiento del modelo).

    @param file (UploadFile): Archivo binario enviado a través de un formulario HTTP (Multipart). Debe ser estrictamente extensión .csv.

    @raises HTTPException 400 Si el archivo cargado no posee la extensión '.csv'.
    @raises HTTPException 500 Si ocurre un fallo crítico durante el proceso de guardado o en la ejecución del pipeline interno.

    @return dict Mensaje en formato JSON que confirma el éxito completo del proceso de re-entrenamiento.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser estrictamente un CSV.")
        
    try:
        nombre_archivo = file.filename
        
        ruta_destino = os.path.join("data/raw",nombre_archivo)
        with open(ruta_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Archivo {nombre_archivo} recibido con éxito y guardado para procesamiento.")
        
        ejecutar_pipeline()
        
        return {
            "status": "success",
            "message": "Pipeline ejecutado con éxito. Modelo re-entrenado y Base de Datos actualizada."
        }
        
    except Exception as e:
        logger.error(f"Error en el endpoint del pipeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error crítico en el pipeline: {str(e)}")


@app.get("/api/metrics")
def get_metrics():
    """
    @brief Endpoint para obtener los reportes numéricos del modelo.
    
    @details Accede al directorio de resultados en busca del archivo JSON de métricas 
             generado por el pipeline. Lee el archivo estructurado y lo expone como JSON estructurado.

    @raises HTTPException 404 Si el archivo JSON de métricas no existe en el almacenamiento, 
                           lo cual indica que el pipeline aún no se ha ejecutado exitosamente.
    @raises HTTPException 500 Si ocurre un error inesperado de lectura de archivos o decodificación del JSON.

    @return dict Objeto JSON con los coeficientes del modelo de clasificación (ej: Accuracy, Precision, Recall).
    """
    # REEMPLAZA 'metricas.json' por el nombre EXACTO de tu archivo JSON en results/
    json_path = os.path.join(RESULTS_DIR, "metricas.json") 
    
    if not os.path.exists(json_path):
        logger.warning("Se solicitaron las métricas pero el archivo JSON no existe en results/")
        raise HTTPException(status_code=404, detail="Archivo de métricas no encontrado. Ejecuta el pipeline primero.")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            datos_metricas = json.load(f)
        return datos_metricas
    except Exception as e:
        logger.error(f"Error al leer el archivo de métricas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al leer el reporte de métricas.")


@app.get("/api/charts/{chart_name}")
def get_chart(chart_name: str):
    """
    @brief Endpoint para la transferencia y visualización de gráficos estadísticos.
    
    @details Recupera una imagen específica (ej. matriz de confusión, curva ROC) desde 
             la carpeta interna 'results/' utilizando el nombre provisto en la URL. 
             La función cuenta con un sanitarizador de rutas básico para mitigar ataques 
             de Path Traversal.

    @param chart_name (str): Nombre exacto del archivo de imagen solicitado (incluyendo extensión, ej: 'matriz_confusion.png').

    @raises HTTPException 404 Si el archivo de imagen especificado no se encuentra en el directorio 'results/'.

    @return FileResponse Retorna una respuesta HTTP de tipo archivo binario con el MIME-type 'image/png'.
    """
    # Sanitarizar el nombre para evitar vulnerabilidades de Path Traversal
    safe_name = os.path.basename(chart_name)
    img_path = os.path.join(RESULTS_DIR, safe_name)
    
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail=f"El gráfico '{safe_name}' no existe.")
        
    return FileResponse(img_path, media_type="image/png")