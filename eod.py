from scipy.signal import argrelextrema
from typing import List
import pandas as pd
import numpy as np
import asyncio
from collections import defaultdict

from exceptions import NoSymbolException
from utils import Prices, Symbols

class EOD:
    def __init__(self, type: str = None, symbol: str = None, fromWatchlist: bool = False):
        self._type: str = type
        self._symbol: str = symbol
        self._fromWatchlist: bool = fromWatchlist
        #self._periods: List = ["1d", "3mo", "1y"]
        #self._interval: List = ["1h", "1d", "5d"]
        self._periods = ["3mo"]
        self._interval = ["1h"]

    def _getSymbols(self) -> List:
        if self._symbol is None and self._type is None and self._fromWatchlist == False:
            raise NoSymbolException
        elif self._fromWatchlist:
            try:
                symbols = open('watchlist')
                return symbols
            except:
                raise NoSymbolException
        elif self._symbol is not None:
            return [self._symbol]
        elif self._type is not None:
            return Symbols(self._type).getSymbols()
        else:
            raise NoSymbolException

    def _getPrice(self, scrip: str, interval: str="1d", period="6mo") -> pd.DataFrame:
        return Prices.getHistory(scrip, interval, period)

    def _cleanData(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df.drop(columns=["Volume", "Dividends", "Stock Splits"], inplace=True)
            df.dropna(inplace=True)
            df = df[~df.index.duplicated()]
            df.replace(0, method='bfill', inplace=True)
            return df
        except:
            pass

    def _getMinMax(self, df:pd.DataFrame, smoothing: int = 3, window_range: int = 3) -> pd.DataFrame:
        smoothed_price = df['Close'].rolling(window=smoothing).mean().dropna()
        local_max = argrelextrema(smoothed_price.values, np.greater)[0]
        local_min = argrelextrema(smoothed_price.values, np.less)[0]

        df_local_max_dt = []
        for i in local_max:
            if (i > window_range) and (i < len(df) - window_range):
                df_local_max_dt.append(df.iloc[i-window_range : i+window_range]['Close'].idxmax())
        
        df_local_min_dt = []
        for i in local_min:
            if (i > window_range) and (i < len(df) - window_range):
                df_local_min_dt.append(df.iloc[i-window_range : i+window_range]['Close'].idxmin())

        maxima = pd.DataFrame(df.loc[df_local_max_dt])
        minima = pd.DataFrame(df.loc[df_local_min_dt])
        min_max = pd.concat([maxima, minima]).sort_index()
        min_max.index.name = "Date"
        min_max = min_max.reset_index()
        min_max = min_max[~min_max.duplicated()]

        d = df.reset_index()
        try:
            min_max['Day_num'] = d[d['Date'].isin(min_max.Date)].index.values
        except:
            min_max['Day_num'] = d[d['index'].isin(min_max.Date)].index.values

        min_max = min_max.set_index('Day_num')['Close']

        return min_max

    def _findPatterns(self, minmaxDf: pd.DataFrame, window_range: int = 5, units: int = 100, threshold: float = 0.02) -> defaultdict:
        """Find patterns from minima and maximas

        Args:
            minmaxDf (pd.DataFrame): Dataframe containing minimas and maximas
            window_range (int, optional): Range in which patterns must form. Defaults to 5.
            units (int, optional): Patterns must play out in these units. Defaults to 100.
            threshold (float, optional): Noise percentage. Defaults to 0.02.

        Returns:
            defaultdict: Contains the patterns.
        """
        patterns = defaultdict(list)

        for i in range(window_range, len(minmaxDf)):
            window = minmaxDf.iloc[i-window_range: i]
            if window.index[-1] - window.index[0] > units:
                continue
            a, b, c, d, e = window.iloc[0: 5]

            # Inverted head and shoulders
            if a < b and c < a and c < e and c < d and e < d and abs(b-d) <= np.mean([b, d]) * threshold:
                patterns['IHS'].append((window.index[0], window.index[-1]))

        return patterns

    
    def _plotChart(self, df: pd.DataFrame, minmaxDf: pd.DataFrame, patterns: defaultdict, stock: str) -> None:
        import matplotlib.pyplot as plt
        df.reset_index()['Close'].plot()
        #plt.scatter(minmaxDf.index, minmaxDf.values, color='orange', alpha=.5)
        for _, end_day_nums in patterns.items():
            for _, tup in enumerate(end_day_nums):
                sd = tup[0]
                ed = tup[1]
                plt.scatter(minmaxDf.loc[sd:ed].index, minmaxDf.loc[sd:ed].values, alpha=.5)
        plt.title(f'Showing {stock}')
        plt.show()
        

    async def run(self):
        symbols = self._getSymbols()
        for sym in symbols:
            for i in range(len(self._periods)):
                prices = await self._getPrice(sym, self._interval[i], self._periods[i])
                df = self._cleanData(prices)
                min_max = self._getMinMax(df)
                patterns = self._findPatterns(min_max, threshold=0.02)
                self._plotChart(df, min_max, patterns, sym)

async def main():
    #symbols: List = get_symbols("AUTO")
    #for sym in symbols:
    #prices = await Prices.getHistory("sbin", "1d", "6mo")
    #print(prices.head())
    eod = await EOD(symbol="SBIN").run()
    print(eod)

asyncio.run(main())