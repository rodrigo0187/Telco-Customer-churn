import streamlit as st
import requests
import os
from io import BytesIO

## @file app.py
#  @brief Dashboard de Streamlit para el Centro de Control del Pipeline de Churn.
#  @details Interfaz gráfica de usuario que permite la carga de datasets en formato CSV,
#           gatilla el re-entrenamiento en el backend y visualiza métricas y gráficos en tiempo real.

st.set_page_config(page_title="Churn ML Pipeline", layout="wide")
st.title("Centro de Control: Churn ML Pipeline")

# Endpoint de FastAPI en Render (Usa variable de entorno o localhost localmente)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Inicializar estados de la sesión para mantener la persistencia tras los reruns
if "pipeline_ejecutado" not in st.session_state:
    st.session_state.pipeline_ejecutado = False

# --- BARRA LATERAL ---
st.sidebar.header("Operaciones del Sistema")

# Selector de archivos nativo de Streamlit
archivo_subido = st.sidebar.file_uploader("Sube tu dataset de Churn (.csv)", type=["csv"])

if st.sidebar.button("Ejecutar Pipeline en la API"):
    """
    @brief Gatilla la ejecución del pipeline al hacer clic en el botón.
    @details Lee el archivo CSV subido por el usuario, lo envía mediante una petición
             HTTP POST multipart a la API de FastAPI y evalúa la respuesta para actualizar
             el estado de la interfaz.
    """
    if archivo_subido is not None:
        with st.spinner("Enviando datos a FastAPI y ejecutando pipeline..."):
            try:
                # Preparar el archivo manteniendo su nombre original (con timestamp si lo tiene)
                files = {"file": (archivo_subido.name, archivo_subido.getvalue(), "text/csv")}
                
                # Hacer la petición POST a FastAPI
                respuesta = requests.post(f"{API_URL}/run-pipeline", files=files)
                
                if respuesta.status_code == 200:
                    st.session_state.pipeline_ejecutado = True
                    st.sidebar.success("Pipeline ejecutado con éxito")
                else:
                    error_msg= respuesta.json().get('detail','Desconocido')
                    st.sidebar.error(f"Error de la API (Código {respuesta.status_code}): {error_msg}")
            except ValueError:
                    st.sidebar.error(f"La API respondió con código {respuesta.status_code} pero no envió un JSON.")
                    with st.expander('Ver la respuesta del servidor'):
                        st.code(respuesta.text[:500])
                 
            except Exception as e:
                st.sidebar.error(f"No se pudo conectar con la API: {e}")
    else:
        st.sidebar.warning("Por favor, selecciona un archivo CSV antes de ejecutar.")


# --- CUERPO PRINCIPAL DEL DASHBOARD ---
if st.session_state.pipeline_ejecutado or st.checkbox("Mostrar últimos resultados guardados"):
    """
    @brief Sección principal de visualización de resultados.
    @details Si el pipeline ya se ejecutó o el usuario marca la casilla de verificación,
             esta sección realiza peticiones HTTP GET a la API para descargar el archivo
             'metricas.json' y los gráficos PNG correspondientes, desplegándolos de forma ordenada.
    """
    st.subheader("Métricas del Modelo y Gráficos del Pipeline")
    
    try:
        # 1. Consumir el endpoint de métricas JSON de la API
        res_metrics = requests.get(f"{API_URL}/api/metrics")
        if res_metrics.status_code == 200:
            metricas = res_metrics.json()
            
            # Distribución en 5 columnas para las métricas globales del JSON
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                val_acc = metricas.get('accuracy', 'N/A')
                st.metric(
                    label="Exactitud (Accuracy)", 
                    value=f"{val_acc*100:.2f}%" if isinstance(val_acc, (int, float)) else val_acc
                )
            with col2:
                val_prec = metricas.get('precision', 'N/A')
                st.metric(
                    label="Precisión (Precision)", 
                    value=f"{val_prec*100:.2f}%" if isinstance(val_prec, (int, float)) else val_prec
                )
            with col3:
                val_rec = metricas.get('recall', 'N/A')
                st.metric(
                    label="Sensibilidad (Recall)", 
                    value=f"{val_rec*100:.2f}%" if isinstance(val_rec, (int, float)) else val_rec
                )
            with col4:
                val_f1 = metricas.get('f1_score', 'N/A')
                st.metric(
                    label="F1-Score Global", 
                    value=f"{val_f1*100:.2f}%" if isinstance(val_f1, (int, float)) else val_f1
                )
            with col5:
                val_auc = metricas.get('roc_auc', 'N/A')
                st.metric(
                    label="ROC AUC", 
                    value=f"{val_auc*100:.2f}%" if isinstance(val_auc, (int, float)) else val_auc
                )

            # Desglose del Classification Report estructurado por clases
            st.markdown("### Reporte de Clasificación Detallado")
            with st.expander("Ver desglose por Clase (0: No Churn / 1: Churn)", expanded=True):
                report = metricas.get('classification_report', {})
                if report:
                    c_clase0, c_clase1 = st.columns(2)
                    
                    with c_clase0:
                        st.markdown("**Clase 0 (Permanencia)**")
                        clase_0 = report.get('0', {})
                        st.write(f"Precisión: {clase_0.get('precision', 0)*100:.2f}%")
                        st.write(f"Recall: {clase_0.get('recall', 0)*100:.2f}%")
                        st.write(f"F1-Score: {clase_0.get('f1-score', 0)*100:.2f}%")
                        st.caption(f"Soporte: {int(clase_0.get('support', 0))} registros")
                        
                    with c_clase1:
                        st.markdown("**Clase 1 (Fuga / Churn)**")
                        clase_1 = report.get('1', {})
                        st.write(f"Precisión: {clase_1.get('precision', 0)*100:.2f}%")
                        st.write(f"Recall: {clase_1.get('recall', 0)*100:.2f}%")
                        st.write(f"F1-Score: {clase_1.get('f1-score', 0)*100:.2f}%")
                        st.caption(f"Soporte: {int(clase_1.get('support', 0))} registros")
                else:
                    st.warning("No se encontro el desglose por clases en el reporte.")
        else:
            st.warning("No se pudieron cargar las métricas desde la API. Asegurate de haber corrido el pipeline.")
            
        # 2. Consumir el endpoint de imágenes PNG de la API
        st.markdown("---")
        st.subheader("Gráficos Estadísticos Generados")
        
        # Nombres exactos de tus archivos .png guardados en results/
        lista_graficos = ["matriz_confusion.png", "distribución_clases.png", "curva_roc.png","importancia_variables.png"]
        
        # Desplegar los gráficos dinámicamente en columnas
        cols_graficos = st.columns(len(lista_graficos))
        for i, nombre_grafico in enumerate(lista_graficos):
            with cols_graficos[i]:
                res_img = requests.get(f"{API_URL}/api/charts/{nombre_grafico}")
                if res_img.status_code == 200:
                    st.image(
                        BytesIO(res_img.content), 
                        caption=f"Reporte: {nombre_grafico}", 
                        use_container_width=True
                    )
                else:
                    st.error(f"Gráfico no encontrado: {nombre_grafico}")
                    
    except Exception as e:
        st.error(f"Error al conectar con la API para extraer los resultados: {e}")
        
else:
    st.info("El sistema esta listo. Sube un dataset en la barra lateral izquierda y ejecuta el pipeline para procesar los datos.")