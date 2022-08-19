from helpers import MoneyControlRSS
from parsers import ICICIDirect, KotakSecurities, Samco
from parsers import Zerodha
from utils import runAsync, Prices
from models import MinMax, HurstExponent
from engines import PatternEngine
from helpers import StocknoteAPI

import json
import asyncio
import sys

def print_message(message):
    print("-"*50)
    print(message)

def print_df(df):
    try:
        df.drop(["Dividends", "Stock Splits"], axis=1, inplace=True)
    except:
        pass
    print(df.head())

def write_json(message):
    with open("test.json", "w") as f:
        f.write(json.dumps(message))

async def main():
    #df = await Prices.getHistory("aubank", "1m", "1wk")
    #print(df.head())
    #symbol: str = sys.argv[1]
    #PatternEngine().test()
    StocknoteAPI().run()

    await runAsync.runParallel(
    #     # MoneyControlRSS.getData("TN", "title", print_message), 
    #     # ICICIDirect("TI", print_message).parse(),
    #     # KotakSecurities.run("TC", write_json, False),
    #     # Prices.getHistory("tatamotors", "1d", "1mo"),
    #     # MinMax.getMinMax(df=df, col_name="Close", getMinima=True, window_range=20, callback=print_df, smoothing=14),
    #     # HurstExponent.hurstExponent(df, 100, print_message)
    #     # Samco.get_orderbook("RELIANCE", print_message),
    #    Zerodha(symbol.upper()).plotOrderMap()
    )

asyncio.run(main())

# plot_orderbook()
