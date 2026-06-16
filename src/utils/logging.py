import logging
import os
from datetime import datetime

def get_logger(name):
    """Configura y retorna un objeto Logger unificado para la aplicación.

    Evita la duplicación de handlers si la función es llamada múltiples
    veces con el mismo nombre y define un formato de salida estandarizado
    tanto para la consola como para el flujo de Docker.

    Args:
        name (str): El nombre del módulo o script que genera los logs 
            (por ejemplo, 'train_model' o 'predict_model').

    Returns:
        logging.Logger: Un objeto Logger configurado con nivel INFO y 
            un StreamHandler formateado.
    """    
    logger = logging.getLogger(name)
    if not logger.handlers:
        
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        ruta_logs_dir = 'results/logs'
        os.mkdirs(ruta_logs_dir,exits_ok = True)
        ruta_archivo_log = os.path.join(ruta_logs_dir,'Errores_pipeling.log')
        
        # configuracion del Findhandler (manejador de archivos)
        file_handler = logging.FileHandler(ruta_archivo_log,mode='a',encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        file_handler.setLevel(logging.warning)
        logger.addHandler(file_handler)
        
        logger.setLevel(logging.INFO)
        
    return logger