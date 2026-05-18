import pandas as pd
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin


class Winsorizer(BaseEstimator,TransformerMixin):
    def __init__(self, limits: tuple= (0.05 ,0.05),exclude_cols: list= None):
        """Define límites cuantiles para la winsorización.

        Args:
            limits (tuple, optional): Límites inferior y superior (0.05 ,0.05).
            exclude_cold(list,Optional): Excluye columnas de la winsorización
        """
        if exclude_cols is None:
            self.exclude_cols= []
        else:
            self.exclude_cols = exclude_cols
       
        self.limits = limits
    
    def fit(self,X, y=None ):
        """_summary_

        Args:
            X (_type_): _description_
            y (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """ 
        if isinstance(X, pd.DataFrame):
            self.columns_ = X.columns
        else:
            self.columns_ = np.arange(X.shape[1])
        
        # 
        self.bounds_ = {}
        cols_nums = self.columns_
        for col in cols_nums:
            col_data = X[col]
            lower = col_data.quantile(self.limits[0])
            upper = col_data.quantile(1 - self.limits[1])
            
            self.bounds_[col]= (lower,upper)
            pass
            
        
        return self
        

    def transform(self , df:pd.DataFrame) -> pd.DataFrame:
        """Aplica winsorización sobre variables númericas utilizando limites quantile.

        Args:
            df (pd.DataFrame): DataFrame clientes churn

        Returns:
            pd.DataDaFrame: Retorna DataFrame con valores extremos estabilizados.
        """        
        df = df.copy()
        
        # seleccionar variables númericas
        nums_col = df.select_dtypes(include=['number']).columns
        
        # excluir columnas churn , customerid
        nums_col = [
            col for col in nums_col
            if col not in self.exclude_cols
        ]
        # usa quantile de fit
        for col in nums_col:
            lower , upper = self.bounds_[0]
            df[col] = np.clip(df[col],lower,upper)
            
        return df