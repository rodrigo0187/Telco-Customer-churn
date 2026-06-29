import pandas as pd
import numpy as np
from utils.outliers import outliers
from utils.negative_values import has_negative_values
from utils.inconsistencies_cat import categorical_inconsistencies
from utils.categorical_nulls import categorical_nulls

# validar si existe (inconsistencia,atipicos,nulos,duplicados)
# contar e imprimir
class QualityCheck:
    # Region qualitycheck
    def __init__(self,data:pd.DataFrame,exclude_inconsistencies:np.array = None):
        
        """Realizar validaciones de calidad de los datos en un conjunto de datos.

       Incluye validacion para:
       - nulls values
       - duplicados
       - outliers(valores atípicos)
       - valores negativos
       - inconsistencias categóricas
       
       Args: 
            data (pd.DataFrame): El conjunto de datos a validar.
            exclude_inconsistencies (np.array, optional): columnas numericas a excluir
            del análisis de outliers y negativos. Por defecto en None.
        """
        
        self.data =data
        # verificar si se excluyen columnas
        if exclude_inconsistencies is None:
            self.exclude_inconsistencies = []
        else:
            self.exclude_inconsistencies = exclude_inconsistencies
    
    # valores faltantes
    def has_nulls(self) ->bool:
        """Analiza si existe valores nulos en el DataFrame

        Returns:
            bool: Retorna verdadero o falso de la existencia de nulos
        """        
        return self.data.isna().any().any()
    
    # valores duplicados
    def has_duplicates(self) -> bool:
        """Analiza la existencia de valores duplicados en el DataFrame

        Returns:
            bool: Retorna verdadero o falso de la existencia de duplicados
        """        
        return self.data.duplicated().any()
    
    # outliers
    def has_outliers(self):
        """Analiza si existen valores atípicos utilizando IQR en el DataFrame.

        Returns:
            bool : True si existen outliers,
            False caso contrario.
        """        
        return outliers(self.data)
    
    
    # valores negativos 
    def has_negative_values(self):
        """Analiza si existen valores negativos en el DataFrame.

        Returns:
            bool : True si existen valores negativos, caso contrario False.
        """        
        return has_negative_values(self.data)
            
    
    # inconsistencia categoricas
    def has_categorical_inconsitencies(self) -> bool:
        """Analiza inconsistencia de variables categóricas

        Returns:
            bool: Retorna verdadero(True) si existen incosistencias categóricas,
            False caso contrario
        """        
        return categorical_inconsistencies(self.data)
    
    # Inconsistencias generales
    def has_inconsistencies(self) -> bool:
        """Evalua si el DataFrame presenta inconsistencias numéricas (negativos) o categóricos.
        Returns:
            bool: True si detecta al menos una inconsistencia (negativa o categorica)
            False si los datos están limpios de ambas manera de manera general.
        """        
        neg = self.has_negative_values()
        cat = self.has_categorical_inconsitencies()
        return neg or cat
    
    # completed report
    def quality_report(self) -> dict:
        """Genera un reporte final consolidado en formato de indicadores booleanos.
        
        Returns:
            dict : Diccionario cuyas llaves son la prueba de la calidad realizadas
            ('Nulos/faltantes','Outliers',etc) y sus valores indican presencia como TRUE o ausencia False de fallos.
        
        """        
        return {
            "Nulos/faltantes" : bool(self.has_nulls()),
            "Valores_duplicados": bool(self.has_duplicates()),
            "Outliers":bool(self.has_outliers()),
            "Valores_negativos": bool(self.has_negative_values()),
            "Inconsistencias cat": bool(self.has_categorical_inconsitencies()),
            "Inconsistencias gen":bool(self.has_inconsistencies()),
        }
        
    # calcular el score de calidad
    def quality_score_weight(self) ->float:
        """Calcula un puntaje de la calidad de los datos ponderadas aplicando penalización.

        Returns:
            float: Puntaje final de calidad de datos acotado entre 0 y 100.
        """        
        weights ={
            "Nulos/faltantes" : 0.1,
            "Valores_duplicados": 0.2,
            "Outliers": 0.1,
            "Inconsistencias":0.6
        }
        checks = {
           "Nulos/faltantes" : self.has_nulls(),
            "Valores_duplicados": self.has_duplicates(),
            "Outliers": self.has_outliers(),
            "Inconsistencias": self.has_inconsistencies()    
        }
        penalty = 0
        total_weight = sum(weights.values())
        for key in checks:
            if checks[key]:
                penalty +=weights[key]
                
        quality = max(0,(1 - (penalty/total_weight)) * 100)
        return round(quality,2)
    # fin seccion qualitycheck
    
    # region quelitycheck_details
    # indicador de columna en conflicto
    
    # null details
    def null_details(self,id_column='customerid') -> dict:
        """Obtiene los detalles de los nulos por columna incluyendo un análisis de nulos esperados
        según la variable 'tenure'.

        Args:
            id_column (str, optional): Nombre de la columna identificadora 'customerid'

        Raises:
            ValueError: si la columna identificadora ('id_column') no existe en el DataFrame.

        Returns:
            dict: Diccionario por columna con el conteo de nulos, IDs afectados, nulos esperados e inesperados.
        """
             
        if id_column not in self.data.columns:
            raise ValueError(f'Columna {id_column} no existe en el dataFrame')
        result = {}
        for col in self.data.columns:
            mask = self.data[col].isna()
            
            if mask.any():
                subset =self.data.loc[mask]
                
                ids = subset[id_column].to_list()
                if 'tenure' in subset.columns:
                    expected_mask = subset['tenure'] == 0
                    unexpected_mask = subset['tenure'] > 0

                    expected = int(expected_mask.sum())
                    unexpected = int(unexpected_mask.sum())

                    unexpected_ids = subset.loc[unexpected_mask, id_column].tolist() if id_column in subset.columns else []
                else:
                    expected = None
                    unexpected = None
                    unexpected_ids = []

                result[col] = {
                    "count": int(mask.sum()),
                    "proportion": float(mask.mean()),
                    "ids": ids,
                    "expected_nulls": expected,
                    "unexpected_nulls": unexpected,
                    "unexpected_ids": unexpected_ids
            }

        return result
    
    # duplicated details
    def duplicated_details(self) ->dict:
        """Cuenta la cantidad de filas duplicadas encontradas en el DataFrame.

        Returns:
            dict: un diccionario con la llave 'duplicate_rows' y la cantidad total,
            o un diccionario vacio {} si no hay duplicados.
        """        
        counts = self.data.duplicated().sum()
        return {"duplicated_rows": int(counts)} if counts > 0 else{}
    
    # atypical details
    def outliers_details(self) ->dict:
        """Obtiene el conteo de valores atípicos por columna mediante metodo IQR.

        Returns:
            dict: Diccionario donde las llaves son los nombres de las columnas numéricas
            y los valores representan la cantidad de outliers detectados solo incluye
            columnas con conteo > 0.
        """        
        df= self.data.select_dtypes(include=['number'])
        df =df.drop(columns=self.exclude_inconsistencies,errors='ignore')
        
        Q1= df.quantile(0.25)
        Q3= df.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers_count = ((df < lower_bound)| (df > upper_bound)).sum()
        return outliers_count[outliers_count>0].to_dict()
    
    # negative for columns
    def columns_negative_details(self) ->dict:
        """Cuenta la cantidad de negativos encontrados por columna numérica.

        Returns:
            dict: Diccionario donde las llaves son los nombres de las columnas numéricas
            y los valores son la cantidad de negativos hallados (solo incluye columnas con conteo >0).
        """        
        df = self.data.select_dtypes(include=['number'])
        df = df.drop(columns=self.exclude_inconsistencies,errors='ignore')
        
        neg_counts = (df<0).sum()
        return neg_counts[neg_counts > 0].to_dict()
    
    # categorical_inconsistencies
    def categoric_inconsistencies_details(self) ->dict:
        """ Detecta incosistencia de formato (espacios o diferencias de mayúsculas/minúsculas)
        en variables categóricas.

        Returns:
            dict: Diccionario donde las llaves son las columnas afectadas y los valores son
            sub-diccionarios {} conteniendo las listas de los valores original y normalizes.
        """        
        cat_cols = self.data.select_dtypes(include=["object"])
        result = {}
        
        for col in cat_cols.columns:
            values = cat_cols[col].dropna().astype(str)
            normalized = values.str.strip().str.lower()
            
            if len(values.unique()) != len(normalized.unique()):
                result[col] = { 
                    "original": list(values.unique()),
                    "normalizes": list(normalized.unique())
                }
        return result
    
    # quality report
    def quality_report_details(self)-> dict:
        """Genera un reporte detallado y estructurado de la calidad de los datos.

        Returns:
            dict: Diccionario consolidado con los resultados detallados de cada validación.
                Contiene las llaves: 'nulls','categorical nulls', 'duplicated', 'outliers', 'negative' y 
                'categorical_issues'.
        """      
        return{
            "nulls":self.null_details(),
            "categorical_nulls_proportion":self.categorical_nulls(),
            "duplicated":self.duplicated_details(),
            "outliers":self.outliers_details(),
            "negative":self.columns_negative_details(),
            "categorical_issues":self.categoric_inconsistencies_details()
        }