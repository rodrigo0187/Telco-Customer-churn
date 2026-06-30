from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil
from src.pipeline import main as ejecutar_pipeline
from src.utils.logging_config import get_logger

logger = get_logger('fastapi_backend')

app = FastAPI(
    title="Churn ML Pipeline API",
    description="API para la ingesta de datos y re-entrenamiento del modelo de Churn",
    version="1.0.0"
)

# Asegurar que existan las carpetas en el contenedor de la API
os.makedirs("data/raw", exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "online", "message": "API de Churn ML operativa"}

@app.post("/run-pipeline")
async def run_pipeline_endpoint(file: UploadFile = File(...)):
    """Recibe un archivo CSV, lo guarda en data/raw y ejecuta el pipeline completo."""
    
    # 1. Validar formato del archivo
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser estrictamente un CSV.")
        
    try:
        # 2. Guardar el archivo recibido en la ruta que espera tu pipeline
        ruta_destino = os.path.join("data/raw", "churn_current.csv")
        with open(ruta_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Archivo {file.filename} recibido con éxito y guardado para procesamiento.")
        
        # 3. Ejecutar tu pipeline original (Ingesta -> DB -> ML)
        ejecutar_pipeline()
        
        return {
            "status": "success",
            "message": "Pipeline ejecutado con éxito. Modelo re-entrenado y Base de Datos actualizada."
        }
        
    except Exception as e:
        logger.error(f"Error en el endpoint del pipeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error crítico en el pipeline: {str(e)}")