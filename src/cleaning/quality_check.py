import pandas as pd
import numpy as np
# validar si existe (inconsistencia,atipicos,nulos,duplicados)
# contar e imprimir
class QualityCheck:
    # Region qualitycheck
    def __init__(self,data:pd.DataFrame,exclude_inconsistencies:np.array = None):
        self.data =data
        # verificar si se excluyen columnas
        if exclude_inconsistencies is None:
            self.exclude_inconsistencies = []
        else:
            self.exclude_inconsistencies = exclude_inconsistencies
    
    # valores faltantes
    def has_nulls(self) ->bool:
        return self.data.isna().any().any()
    
    # valores duplicados
    def has_duplicates(self) -> bool:
        return self.data.duplicated().any()
    
    # Atipicos Q1, Q3 : IQR
    def outliers(self)-> bool:
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
        numeric_col = self.data.select_dtypes(include=['number'])
        # excluye columna del análisis
        numeric_col = numeric_col.drop(
            columns=self.exclude_inconsistencies,errors="ignore")
        return (numeric_col < 0).any().any()
            
    
    # inconsistencia categoricas
    def has_categorical_inconsitencies(self) -> bool:
        cat_cols = self.data.select_dtypes(include=["object"])
        for col in cat_cols.columns:
            values = cat_cols[col].dropna().astype(str)
            normalize = values.str.strip().str.lower()
            if len(values.unique()) != len(normalize.unique()):
                return True
        return False
    
    # Inconsistencias generales
    def has_inconsistencies(self) -> bool:
        neg = self.has_negative_values()
        cat = self.has_categorical_inconsitencies()
        return neg or cat
    
    # completed report
    def quality_report(self) -> dict:
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
    def null_details(self) -> dict:
        nulls_count = self.data.isna().sum()
        return nulls_count[nulls_count>0].to_dict()
    
    # duplicated details
    def duplicated_details(self) ->dict:
        counts = self.data.duplicated().sum()
        return {"duplicated_rows": int(counts)} if counts > 0 else{}
    
    # atypical details
    def outliers_details(self) ->dict:
        df= self.data.select_dtypes(include=['number'])
        df =df.drop(columns=self.exclude_inconsistencies,errors='ignore')
        
        Q1= df.quantile(25)
        Q3= df.quantile(75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers_count = ((df < lower_bound)| (df > upper_bound)).sum()
        return outliers_count[outliers_count>0].to_dict()
    
    # negative for columns
    def columns_negative_details(self) ->dict:
        df = self.data.select_dtypes(include=['number'])
        df = df.drop(columns=self.exclude_inconsistencies,errors='ignore')
        
        neg_counts = (df<0).sum()
        return neg_counts[neg_counts > 0].to_dict()
    
    # categorical_inconsistencies
    def categoric_inconsistencies_details(self) ->dict:
        cat_cols = self.data.select_dtypes(include=["object"])
        result = {}
        
        for col in cat_cols.columns:
            values = cat_cols[col].dropna().astype(str)
            normalized = values.str.trip().str.lower()
            
            if len(values.unique()) != len(normalized.unique()):
                result[col] = {
                    "original": list(values.unique()),
                    "normalizes": list(normalized.unique())
                }
        return result
    
    # quality report
    def quality_report_details(self)-> dict:
        return{
            "nulls":self.null_details(),
            "duplicated":self.duplicated_details(),
            "outliers":self.outliers_details(),
            "negative":self.columns_negative_details(),
            "categorical_issues":self.categoric_inconsistencies_details()
        }