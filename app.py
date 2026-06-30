import streamlit as st
import requests
import os

st.title("Centro de Control: Churn ML Pipeline")

# Endpoint de FastAPI en Render (Usa variable de entorno o localhost localmente)
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.sidebar.header("Operaciones del Sistema")

# Selector de archivos nativo de Streamlit (¡Resuelve el problema de la carpeta vacía!)
archivo_subido = st.sidebar.file_uploader("Sube tu dataset de Churn (.csv)", type=["csv"])

if st.sidebar.button("Ejecutar Pipeline en la API"):
    if archivo_subido is not None:
        with st.spinner("Enviando datos a FastAPI y ejecutando pipeline..."):
            try:
                # Preparar el archivo para enviarlo por HTTP POST
                files = {"file": (archivo_subido.name, archivo_subido.getvalue(), "text/csv")}
                
                # Hacer la petición a FastAPI
                respuesta = requests.post(f"{API_URL}/run-pipeline", files=files)
                
                if respuesta.status_code == 200:
                    st.sidebar.success("" + respuesta.json()["message"])
                    st.rerun()
                else:
                    st.sidebar.error(f"Error de la API: {respuesta.json()['detail']}")
            except Exception as e:
                st.sidebar.error(f"No se pudo conectar con la API: {e}")
    else:
        st.sidebar.warning("Por favor, selecciona un archivo CSV antes de ejecutar.")