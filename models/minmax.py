from typing import Callable
from pandas import DataFrame, concat
import numpy as np
from scipy.signal import argrelextrema

class MinMax:
    def __init__(self):
        return

    async def __get_min_max(self, df: DataFrame, key: str, window_range: int, getMinima: bool, getMaxima: bool, smoothing: int=None) -> DataFrame:     
        if smoothing is not None:
            smoothed = df[key].rolling(window=smoothing).mean().dropna()
            local_max = argrelextrema(smoothed.values, np.greater)[0]
            local_min = argrelextrema(smoothed.values, np.less)[0]
        else:
            local_max = argrelextrema(df[key].values, np.greater)[0]
            local_min = argrelextrema(df[key].values, np.less)[0]
        
        price_local_max_dt = []
        
        for i in local_max:
            if (i > window_range) and (i < len(df)-window_range):
                price_local_max_dt.append(df.iloc[i-window_range:i+window_range][key].idxmax())
        
        price_local_min_dt = []
        
        for i in local_min:
            if (i > window_range) and (i < len(df)-window_range):
                price_local_min_dt.append(df.iloc[i-window_range:i+window_range][key].idxmin())
        
        maxima = DataFrame(df.loc[price_local_max_dt])
        minima = DataFrame(df.loc[price_local_min_dt])

        max_min = concat([maxima, minima]).sort_index()
        max_min.index.name = 'Datetime'
        max_min = max_min.reset_index()
        max_min = max_min[~max_min.Datetime.duplicated()]

        maxima = maxima.reset_index()
        minima = minima.reset_index()
        try:
            maxima = maxima[~maxima.Datetime.duplicated()]
            minima = minima[~minima.Datetime.duplicated()]
        except AttributeError:
            maxima = maxima[~maxima.Date.duplicated()]
            minima = minima[~minima.Date.duplicated()]

        if getMinima:
            res = minima
        elif getMaxima:
            res = maxima
        else:
            res = max_min

        p = df.reset_index()

        if getMinima or getMaxima:
            try:
                res['interval'] = p[p['Datetime'].isin(res.Datetime)].index.values
            except:
                res['interval'] = p[p['Date'].isin(res.Date)].index.values
            res = res.set_index('interval')['Close']
        else:
            try:
                res['interval'] = p[p['Datetime'].isin(res.Datetime)].index.values
            except:
                res['interval'] = p[p['Date'].isin(res.Datetime)].index.values
            res = res.set_index('interval')['Close']

        return res

    @classmethod
    async def getMinMax(self, df: DataFrame, col_name: str, window_range: int, getMinima: bool=False, getMaxima: bool=False, callback: Callable=None, smoothing: int=None) -> DataFrame:
        """Returns minimas and maximas of a dataframe.

        Args:
            df (pandas.DataFrame): Specify a pandas dataframe
            col_name (str): Column name to take in consideration
            window_range (int): Specify the window range
            getMinima (bool, optional): Just return minimas. Defaults to False.
            getMaxima (bool, optional): Just return maximas. Defaults to False.
            callback (Callable, optional): Callable method to callback. Defaults to None.
            smoothing (int, optional): To add some smoothing to the numbers. Defaults to None.

        Returns:
            pandas.DataFrame: Returns a pandas DataFrame, if callback not mentioned else None.
        """
        data = await self.__get_min_max(self, df, col_name, window_range, getMinima, getMaxima, smoothing)
        return data if callback is None else callback(data)