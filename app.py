# src/app.py
import streamlit as st
import os
from src.pipeline import main as ejecutar_pipeline
from src.utils.logging_config import get_logger

logger = get_logger('streamlit_app')

# Configuracion inicial de la pagina sin caracteres especiales
st.set_page_config(
    page_title="Churn ML Dashboard",
    layout="wide"
)

# Titulo Principal limpio
st.title("Centro de Control: Churn ML Pipeline")
st.markdown("---")

# --- BARRA LATERAL DE CONTROL ---
st.sidebar.header("Operaciones del Sistema")
st.sidebar.markdown("Usa los controles de abajo para interactuar con el Pipeline de datos y Modelos de ML.")

# Boton plano para disparar el flujo
if st.sidebar.button("Ejecutar Pipeline Completo"):
    logger.info("Pipeline disparado manualmente desde la interfaz de Streamlit.")
    
    with st.spinner("Procesando flujo completo (Ingesta -> Limpieza -> PostgreSQL -> Entrenamiento ML)..."):
        try:
            # Llamada directa a tu estructura original
            ejecutar_pipeline()
            st.sidebar.success("Pipeline completado con exito")
            
        except Exception as e:
            st.sidebar.error(f"Error critico en la ejecucion: {e}")
            logger.error(f"Error al ejecutar el pipeline desde Streamlit: {str(e)}", exc_info=True)

# Informacion del entorno en la barra lateral
st.sidebar.markdown("---")
st.sidebar.info(
    "Entorno Local Optimizado\n\n"
    "El sistema procesa de forma síncrona el archivo CSV más reciente en 'data/raw/', "
    "garantizando estabilidad y evitando bloqueos de red en Render."
)

# AREA DE VISUALIZACION PRINCIPAL
st.subheader("Monitoreo y Resultados del Negocio")

col1, col2 = st.columns(2)

with col1:
    st.markdown("Estado de la Base de Datos")
    st.info(
        "Espacio reservado para consultas usando SQLAlchemy o Pandas para leer la tabla "
        "cliente de PostgreSQL y mostrar KPIs de Churn o el tamano del dataset."
    )

with col2:
    st.markdown("Rendimiento del Modelo de ML")
    
    # Ruta típica donde se guardan matrices de confusión o curvas ROC
    ruta_grafico = "results/confusion_matrix.png" # Ajusta al nombre real de tu gráfico
    
    if os.path.exists(ruta_grafico):
        st.image(ruta_grafico, caption="Matriz de Confusión - Último Entrenamiento")
    else:
        st.info(
            "No se encontraron gráficos en 'results/'. "
            "Ejecuta el pipeline completo para generar las métricas del modelo."
        )