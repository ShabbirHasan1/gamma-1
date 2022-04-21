from functools import lru_cache
from typing import Callable
from pandas import DataFrame
import yfinance

class Prices:
    @classmethod
    @lru_cache
    async def getHistory(self, ticker: str, interval: str, period: str, callback: Callable = None) -> DataFrame:
        """Returns stock price data from Yahoo! finance

        Args:
            ticker (str): Specify ticker symbol.
            interval (str): Specify the interval.
            period (str): Specify the period.
            callback (Callable): Callable method for callbacks. Defaults to None

        Returns:
            pandas.DataFrame: Returns stock prices in pandas dataframe.
        """

        data = yfinance.Ticker(ticker.upper()+'.NS').history(period, interval)
        return data if callback is None else callback(data)
