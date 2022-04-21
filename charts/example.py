from charts.charts import Candle, CandleStickGraph
import yfinance as yf

ticker = "aubank.ns"

df = yf.download(tickers=ticker, progress=False, threads=True, period="1d", interval="1m")
data = [Candle(value['Open'], value['High'], value['Low'], value['Close']) for index, value in df.iterrows()]
print(CandleStickGraph(data, 10).draw())
