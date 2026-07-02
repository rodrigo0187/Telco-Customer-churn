import sys
from sqlalchemy import create_engine, text

print("INICIANDO SCRIPT DE DIAGNÓSTICO")

# Pegar directamente AQUÍ tu URL externa de Render
URL_EXTERNA = "postgresql://dbchurn_user:xxt234xFdJXIWSjPb0mDTd9hP6eekBjn@dpg-d91ne80js32c739nlrc0-a.oregon-postgres.render.com/dbchurn"

if URL_EXTERNA == "TU_URL_EXTERNA_DE_RENDER_AQUÍ":
    print("ERROR: Olvidaste pegar tu URL real de Render dentro del código.")
    sys.exit()

if URL_EXTERNA.startswith("postgres://"):
    URL_EXTERNA = URL_EXTERNA.replace("postgres://", "postgresql://", 1)

try:
    print("1. Intentando configurar el motor (engine)...")
    engine = create_engine(URL_EXTERNA, connect_args={'connect_timeout': 3})
    print("Motor configurado de forma exitosa.")

    print("2. Intentando abrir conexion fisica (Maximo 3 segundos)...")
    with engine.connect() as conn:
        print("Conexion fisica establecida con el servidor.")
        
        print("3. Ejecutando consulta de prueba...")
        res = conn.execute(text("SELECT version();")).fetchone()
        print("Respuesta del servidor PostgreSQL:")
        print(res[0])
        
except Exception as e:
    print("EL PROCESO FALLO DIRECTAMENTE CON EL SIGUIENTE ERROR:")
    print(e)
print("SCRIPT FINALIZADO")