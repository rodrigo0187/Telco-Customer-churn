"""Módulo de Interfaz Gráfica (Dashboard) y Control del Pipeline de Churn.

Esta aplicación de Streamlit actúa como el Centro de Control principal del proyecto,
permitiendo a los usuarios visualizar las métricas de negocio almacenadas en PostgreSQL,
monitorear el rendimiento del modelo de Machine Learning y disparar manualmente la 
ejecución síncrona del pipeline local (Ingesta, Limpieza, Persistencia y Entrenamiento).

Flujo operativo de la interfaz:
    1. Escanea de forma proactiva el directorio local 'data/raw/' en busca de archivos CSV.
    2. Bloquea de forma preventiva ejecuciones vacías si no hay datos disponibles.
    3. Orquesta la ejecución del pipeline importando el módulo principal de manera nativa.
    4. Sincroniza y fuerza la recarga de la interfaz (Hot-Reload) al generar nuevos artefactos visuales.

Uso:
    Streamlit ejecuta este archivo directamente en el puerto expuesto del contenedor Docker
    o plataforma PaaS (Render) mediante el comando:
    $ streamlit run src/app.py --server.port 10000 --server.address 0.0.0.0
"""

import streamlit as st
import os
import glob
from src.pipeline import main as ejecutar_pipeline
from src.utils.logging_config import get_logger

logger = get_logger('streamlit_app')

# Asegurar de forma reactiva que las carpetas existan en el contenedor de Render
os.makedirs("data/raw", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Configuración inicial de la página
st.set_page_config(
    page_title="Churn ML Dashboard",
    layout="wide"
)

# Título Principal limpio
st.title("Centro de Control: Churn ML Pipeline")
st.markdown("---")

# --- BARRA LATERAL DE CONTROL ---
st.sidebar.header("Operaciones del Sistema")
st.sidebar.markdown("Usa los controles de abajo para interactuar con el Pipeline de datos y Modelos de ML.")

# Validación previa de existencia del archivo CSV local para evitar bloqueos/caídas
RUTA_LOCAL_PATTERN = 'data/raw/*.csv'
archivos_disponibles = [
    f for f in glob.glob(RUTA_LOCAL_PATTERN)
    if not os.path.basename(f).startswith('ingesta_')
]

# Botón plano para disparar el flujo
if st.sidebar.button("Ejecutar Pipeline Completo"):
    if not archivos_disponibles:
        st.sidebar.error("Error: No se encontró ningún archivo CSV en 'data/raw/'. Sube los datos al contenedor antes de ejecutar.")
        logger.warning("Intento de ejecución del pipeline abortado: Carpeta 'data/raw/' vacía.")
    else:
        logger.info("Pipeline disparado manualmente desde la interfaz de Streamlit.")
        
        with st.spinner("Procesando flujo completo (Ingesta -> Limpieza -> PostgreSQL -> Entrenamiento ML)..."):
            try:
                # Llamada directa a la orquestación del pipeline
                ejecutar_pipeline()
                st.sidebar.success("Pipeline completado con éxito")
                
                # Forzar a Streamlit a recargar la página para que dibuje las nuevas métricas creadas en results/
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"Error crítico en la ejecución: {e}")
                logger.error(f"Error al ejecutar el pipeline desde Streamlit: {str(e)}", exc_info=True)

# Información del entorno en la barra lateral
st.sidebar.markdown("---")
st.sidebar.info(
    "**Entorno de Operación:**\n\n"
    "El sistema procesa de forma síncrona el archivo CSV más reciente en 'data/raw/', "
    "garantizando estabilidad y evitando bloqueos de red en Render."
)

# --- ÁREA DE VISUALIZACIÓN PRINCIPAL ---
st.subheader("Monitoreo y Resultados del Negocio")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Estado de la Base de Datos")
    st.info(
        "Espacio reservado para consultas usando SQLAlchemy o Pandas para leer la tabla "
        "cliente de PostgreSQL y mostrar KPIs de Churn o el tamaño del dataset."
    )

with col2:
    st.markdown("#### Rendimiento del Modelo de ML")
    
    # Asegurar que mapee el nombre correcto generado por tu predict.py/train_model()
    ruta_grafico = "results/confusion_matrix.png" 
    
    if os.path.exists(ruta_grafico):
        st.image(ruta_grafico, caption="Matriz de Confusión - Último Entrenamiento", use_container_width=True)
    else:
        st.warning(
            "No se encontraron gráficos en 'results/'. "
            "Ejecuta el pipeline completo desde la barra lateral para generar las métricas del modelo por primera vez."
        )