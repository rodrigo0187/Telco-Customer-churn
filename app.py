import streamlit as st
import requests
import os
from io import BytesIO

## @file app.py
#  @brief Dashboard de Streamlit para el Centro de Control del Pipeline de Churn.
#  @details Interfaz grafica de usuario que permite la carga de datasets en formato CSV,
#           gatilla el re-entrenamiento en el backend y visualiza metricas y graficos en tiempo real.

st.set_page_config(page_title="Churn ML Pipeline", layout="wide")
st.title("Centro de Control: Churn ML Pipeline")

# Endpoint de FastAPI en Render (Usa variable de entorno o localhost localmente)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Inicializar estados de la sesion para mantener la persistencia tras los reruns
if "pipeline_ejecutado" not in st.session_state:
    st.session_state.pipeline_ejecutado = False

# --- BARRA LATERAL ---
st.sidebar.header("Operaciones del Sistema")

# Selector de archivos nativo de Streamlit
archivo_subido = st.sidebar.file_uploader("Sube tu dataset de Churn (.csv)", type=["csv"])

if st.sidebar.button("Ejecutar Pipeline en la API"):
    """
    @brief Gatilla la ejecucion del pipeline al hacer clic en el boton.
    @details Lee el archivo CSV subido por el usuario, lo envia mediante una peticion
             HTTP POST multipart a la API de FastAPI y evalua la respuesta para actualizar
             el estado de la interfaz.
    """
    if archivo_subido is not None:
        with st.sidebar.spinner("Enviando datos a FastAPI y ejecutando pipeline..."):
            try:
                # Preparar el archivo manteniendo su nombre original (con timestamp si lo tiene)
                files = {"file": (archivo_subido.name, archivo_subido.getvalue(), "text/csv")}
                
                # Hacer la peticion POST a FastAPI
                respuesta = requests.post(f"{API_URL}/run-pipeline", files=files)
                
                if respuesta.status_code == 200:
                    st.session_state.pipeline_ejecutado = True
                    st.sidebar.success("Pipeline ejecutado con exito")
                else:
                    error_msg = respuesta.json().get('detail', 'Desconocido')
                    st.sidebar.error(f"Error de la API (Codigo {respuesta.status_code}): {error_msg}")
            except ValueError:
                    st.sidebar.error(f"La API respondio con codigo {respuesta.status_code} pero no envio un JSON.")
                    with st.sidebar.expander('Ver la respuesta del servidor'):
                        st.code(respuesta.text[:500])
                 
            except Exception as e:
                st.sidebar.error(f"No se pudo conectar con la API: {e}")
    else:
        st.sidebar.warning("Por favor, selecciona un archivo CSV antes de ejecutar.")


# --- CUERPO PRINCIPAL DEL DASHBOARD ---
if st.session_state.pipeline_ejecutado or st.checkbox("Mostrar ultimos resultados guardados"):
    """
    @brief Seccion principal de visualizacion de resultados.
    @details Si el pipeline ya se ejercuto o el usuario marca la casilla de verificacion,
             esta seccion realiza peticiones HTTP GET a la API para descargar el archivo
             'metricas.json' y los graficos PNG correspondientes, desplegandolos de forma ordenada.
    """
    st.subheader("Metricas del Modelo y Graficos del Pipeline")
    
    try:
        # 1. Consumir el endpoint de metricas JSON de la API
        res_metrics = requests.get(f"{API_URL}/api/metrics")
        if res_metrics.status_code == 200:
            metricas = res_metrics.json()
            
            # Distribucion en 5 columnas para las metricas globales del JSON
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
                    label="Precision (Precision)", 
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
            st.markdown("### Reporte de Clasificacion Detallado")
            with st.expander("Ver desglose por Clase (0: No Churn / 1: Churn)", expanded=True):
                report = metricas.get('classification_report', {})
                if report:
                    c_clase0, c_clase1 = st.columns(2)
                    
                    with c_clase0:
                        st.markdown("**Clase 0 (Permanencia)**")
                        clase_0 = report.get('0', {})
                        st.write(f"Precision: {clase_0.get('precision', 0)*100:.2f}%")
                        st.write(f"Recall: {clase_0.get('recall', 0)*100:.2f}%")
                        st.write(f"F1-Score: {clase_0.get('f1-score', 0)*100:.2f}%")
                        st.caption(f"Soporte: {int(clase_0.get('support', 0))} registros")
                        
                    with c_clase1:
                        st.markdown("**Clase 1 (Fuga / Churn)**")
                        clase_1 = report.get('1', {})
                        st.write(f"Precision: {clase_1.get('precision', 0)*100:.2f}%")
                        st.write(f"Recall: {clase_1.get('recall', 0)*100:.2f}%")
                        st.write(f"F1-Score: {clase_1.get('f1-score', 0)*100:.2f}%")
                        st.caption(f"Soporte: {int(clase_1.get('support', 0))} registros")
                else:
                    st.warning("No se encontro el desglose por clases en el reporte.")
        else:
            st.warning("No se pudieron cargar las metricas desde la API. Asegurate de haber corrido el pipeline.")
            
        # 2. Consumir el endpoint de imagenes PNG de la API
        st.markdown("---")
        st.subheader("Graficos Estadisticos Generados")
        
        # Segmentacion de graficos en cuadricula organizada para legibilidad en pantallas anchas
        fila1_col1, fila1_col2 = st.columns(2)
        fila2_col1, fila2_col2 = st.columns(2)
        
        # Grafico 1: Matriz de Confusion
        with fila1_col1:
            res_img = requests.get(f"{API_URL}/api/charts/matriz_confusion.png")
            if res_img.status_code == 200:
                st.image(BytesIO(res_img.content), caption="Reporte: matriz_confusion.png", use_container_width=True)
            else:
                st.error("Grafico no encontrado: matriz_confusion.png")

        # Grafico 2: Distribucion de Clases
        with fila1_col2:
            res_img = requests.get(f"{API_URL}/api/charts/distribución_clases.png")
            if res_img.status_code == 200:
                st.image(BytesIO(res_img.content), caption="Reporte: distribución_clases.png", use_container_width=True)
            else:
                st.error("Grafico no encontrado: distribución_clases.png")

        # Grafico 3: Curva ROC
        with fila2_col1:
            res_img = requests.get(f"{API_URL}/api/charts/curva_roc.png")
            if res_img.status_code == 200:
                st.image(BytesIO(res_img.content), caption="Reporte: curva_roc.png", use_container_width=True)
            else:
                st.error("Grafico no encontrado: curva_roc.png")

        # Grafico 4: Importancia de Variables
        with fila2_col2:
            res_img = requests.get(f"{API_URL}/api/charts/importancia_variables.png")
            if res_img.status_code == 200:
                st.image(BytesIO(res_img.content), caption="Reporte: importancia_variables.png", use_container_width=True)
            else:
                st.error("Grafico no encontrado: importancia_variables.png")

        # Grafico 5: Arbol de Decision (Contenedor completo e independiente para legibilidad)
        st.markdown("---")
        st.subheader("Auditoria del Modelo: Arbol de Decision Individual")
        with st.container():
            res_img = requests.get(f"{API_URL}/api/charts/arbol_decision.png")
            if res_img.status_code == 200:
                st.image(BytesIO(res_img.content), caption="Reporte: arbol_decision.png", use_container_width=True)
            else:
                st.error("Grafico no encontrado: arbol_decision.png")
                    
    except Exception as e:
        st.error(f"Error al conectar con la API para extraer los resultados: {e}")
        
else:
    st.info("El sistema esta listo. Sube un dataset en la barra lateral izquierda y ejecuta el pipeline para procesar los datos.")