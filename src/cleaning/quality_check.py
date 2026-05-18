import pandas as pd
import numpy as np
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
    
    # Atipicos Q1, Q3 : IQR
    def outliers(self)-> bool:
        """Analiza valores atípicos(númericas) con metodo rango interquantile de 25% y 75%.

        Returns:
            bool: Retorna verdadero(True) o Falso(False) si existe o no atípicos.
        """        
        df = self.data.select_dtypes(include=['number']).drop(
            columns=self.exclude_inconsistencies,errors="ignore"
        )
        Q1 =df.quantile(0.25)
        Q3  =df.quantile(0.75)
        IQR = Q3 - Q1
            
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return ((df < lower_bound)|(df> upper_bound)).any().any()
        
    
    # valores negativos 
    def has_negative_values(self)-> bool:
        """Analiza valores negativos en el DataFrame

        Returns:
            bool: Retorna verdadero(True) si existe valores atípicos.
            Falso(False) caso contrario
        """        
        numeric_col = self.data.select_dtypes(include=['number'])
        # excluye columna del análisis
        numeric_col = numeric_col.drop(
            columns=self.exclude_inconsistencies,errors="ignore")
        return (numeric_col < 0).any().any()
            
    
    # inconsistencia categoricas
    def has_categorical_inconsitencies(self) -> bool:
        """Analiza inconsistencia de variables categóricas

        Returns:
            bool: Retorna verdadero(True) si existe variables categóricas
            False caso contrario
        """        
        cat_cols = self.data.select_dtypes(include=["object"])
        for col in cat_cols.columns:
            values = cat_cols[col].dropna().astype(str)
            normalize = values.str.strip().str.lower()
            if len(values.unique()) != len(normalize.unique()):
                return True
        return False
    
    # Inconsistencias generales
    def has_inconsistencies(self) -> bool:
        """Evalua inconsistencia númericas y categóricas

        Returns:
            bool: Retorna verdadero si hay valores negativos
            caso contrario no existe valores negativos.
            bool: Retonar verdadero si hay valores incosistentes
            caso contrario no existe valores inconsistentes
        """        
        neg = self.has_negative_values()
        cat = self.has_categorical_inconsitencies()
        return neg or cat
    
    # completed report
    def quality_report(self) -> dict:
        """Genera un reporte final del conjunto de datos analizados

        Returns:
            dict: 
            - nulls values
            - duplicados
            - outliers(valores atípicos)
            - valores negativos
            - inconsistencias categóricas
        """        
        return {
            "Nulos/faltantes" : bool(self.has_nulls()),
            "Valores_duplicados": bool(self.has_duplicates()),
            "Outliers":bool(self.outliers()),
            "Valores_negativos": bool(self.has_negative_values()),
            "Inconsistencias cat": bool(self.has_categorical_inconsitencies()),
            "Inconsistencias gen":bool(self.has_inconsistencies()),
        }
        
    # calcular el score de calidad
    def quality_score_weight(self) ->float:
        """Calcula un puntaje de la calidad de los datos ponderadas aplicando penalización

        Returns:
            float: Puntaje de calidad de datos de 0 y 100
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
            "Outliers": self.outliers(),
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
        """Obtiene los detalles de los nulos por columna

        Args:
            id_column (str, optional): Nombre de la columna identificadora 'customerid'

        Raises:
            ValueError: se generá sí la columna identificadora no existe en el DataFrame

        Returns:
            dict: Diccionario con el conteo de nulos,Id's afectados, nulos esperados e inesperados por columna.
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
                    "ids": ids,
                    "expected_nulls": expected,
                    "unexpected_nulls": unexpected,
                    "unexpected_ids": unexpected_ids
            }

        return result
    
    # duplicated details
    def duplicated_details(self) ->dict:
        """Cuenta la cantidad de duplicados encontrados

        Returns:
            dict: Retorna la cantidad de duplicados
        """        
        counts = self.data.duplicated().sum()
        return {"duplicated_rows": int(counts)} if counts > 0 else{}
    
    # atypical details
    def outliers_details(self) ->dict:
        """Obtiene el conteo de valores atípicos por columna mediante metodo IQR.

        Returns:
            dict: Retorna la cantidad de atípicos por columna.
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
        """Cuenta la cantidad de negativos encontrados

        Returns:
            dict: Retorna la cantidad de negativos por columna identificados como númericos.
        """        
        df = self.data.select_dtypes(include=['number'])
        df = df.drop(columns=self.exclude_inconsistencies,errors='ignore')
        
        neg_counts = (df<0).sum()
        return neg_counts[neg_counts > 0].to_dict()
    
    # categorical_inconsistencies
    def categoric_inconsistencies_details(self) ->dict:
        """ Detecta incosistencia de formatos en variables categóricas.

        Returns:
            dict: columnas categóricas con diferencia entre valores categóricos e incosistente.
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
        """Genera un reporte de la calidad de los datos

        Returns:
            dict: Resultado consolidado de validaciones y análisis inconsistente.
        """        
        return{
            "nulls":self.null_details(),
            "duplicated":self.duplicated_details(),
            "outliers":self.outliers_details(),
            "negative":self.columns_negative_details(),
            "categorical_issues":self.categoric_inconsistencies_details()
        }