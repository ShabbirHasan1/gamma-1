from typing import Callable
import pandas as pd
import numpy as np

class HurstExponent:
    def __init__(self):
        return

    async def __get_hurst_exponent(self, price, max_lag: int) -> float:
        """Returns the hurst exponent of a given time series."""
        lags = np.arange(2, max_lag+1)
        tau = [np.std(np.subtract(price[lag:], price[:-lag])) for lag in lags]
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]

    @classmethod
    async def hurstExponent(self, time_series: pd.DataFrame, max_lag: int, callback: Callable = None) -> float:
        time_series.drop(['Stock Splits', 'Dividends', 'Volume', 'Open', 'High', 'Low'], axis=1, inplace=True)
        data = await self.__get_hurst_exponent(self, time_series['Close'].dropna().values, max_lag)
        return data if callback is None else callback(data)