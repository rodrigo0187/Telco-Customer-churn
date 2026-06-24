import pandas as pd
import os
def test_dimension_de_datos():
    # rutas
    # x variables predictoras caracteristicas de los clientes
    
    ruta_x = 'data/processed/X_test.csv'
    # y variables de respuestas reales si el cliente se queda o se va
    ruta_y ='data/processed/Y_test.csv'
    
    assert os.path.exists(ruta_x), f"No se encontró archivo en la ruta {ruta_x}"
    assert os.path.exists(ruta_y), f"No se encontró archivo en la ruta {ruta_y}"
    
    # carga de datos
    df_x = pd.read_csv(ruta_x)
    df_y = pd.read_csv(ruta_y)
    
    # comprobar que no esten vacios
    assert len(df_x) > 0, "El archivo está vacio"
    assert len(df_y) > 0, "El archivo está vacio"
    
    # comprobar que las filas de las caracteristicas (y) coincidan con las etiquetas de (x) 
    assert len(df_x) == len(df_y), f"Desajuste de tamaño, (X) tiene {len(df_x)} filas e (Y) tiene {len(df_y)} etiquetas."
    