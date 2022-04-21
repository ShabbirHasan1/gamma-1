from helpers import MoneyControlRSS
from parsers import ICICIDirect, KotakSecurities, Samco
from parsers.zerodha import Zerodha
from utils import runAsync, Prices
from models import MinMax, HurstExponent

import json
import asyncio
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def print_message(message):
    print("-"*50)
    print(message)

# def plot_orderbook():
#     #[
#     # ['BID', 'ORDERS', 'QTY', '0.00', '0', '0', '0.00', '0', '0', '0.00', '0', '0', '0.00', 
#     # '0', '0', '0.00', '0', '0', 'Total', '0'], 
#     # ['ASK', 'ORDERS', 'QTY', '2782.10', '58', '976', '0.00', '0', '0', '0.00', '0', '0', '0.00', '0', '0', 
#     # '0.00', '0', '0', 'Total', '976'], 
#     # ['18', '27786195162.21', '10018531', '2773.48']
#     # ]

#     message = [['BID', 'ORDERS', 'QTY', '2781.25', '1', '7', '2781.20', '3', '182', '2781.15', '4', '299', '2781.10', '2', '469', '2781.05', '1', '75', 'Total', '341116'], ['ASK', 'ORDERS', 'QTY', '2781.30', '1', '230', '2781.90', '1', '12', '2782.00', '6', '102', '2782.20', '1', '14', '2782.25', '2', '63', 'Total', '629173'], ['65', '16949060451.96', '6125229', '2767.09']]

#     bid_column: List = message[0][3:18]
#     ask_column: List = message[1][3:18]
#     market_info: List = message[2]

#     i: int = 0
#     res: Dict = {}
#     market: Dict = {}
#     bid_price: List = []
#     bid_quantity: List = []
#     bid_orders: List = []

#     ask_price: List = []
#     ask_orders: List = []
#     ask_quantity: List = []

#     while i < len(bid_column)-3:
#         bid_price.append(float(bid_column[i]))
#         bid_orders.append(int(bid_column[i+1]))
#         bid_quantity.append(int(bid_column[i+2]))

#         ask_price.append(float(ask_column[i]))
#         ask_orders.append(int(ask_column[i+1]))
#         ask_quantity.append(int(ask_column[i+2]))

#         i+=3

#     res['bidprice'] = bid_price
#     res['bidorders'] = bid_orders
#     res['bidqty'] = bid_quantity
#     res['askprice'] = ask_price
#     res['askorders'] = ask_orders
#     res['askqty'] = ask_quantity

#     market['ltq'] = int(market_info[0])
#     market['volinrs'] = float(market_info[1])
#     market['volinsh'] = int(market_info[2])
#     market['atp'] = float(market_info[3])
        
#     df = pd.DataFrame(res)
    
#     plt.grid(False)
#     plt.axis('on')
#     plt.style.use('dark_background')

#     print(df['bidqty'])

#     plt.show()

def print_df(df):
    try:
        df.drop(["Dividends", "Stock Splits"], axis=1, inplace=True)
    except:
        pass
    print(df.head())

def print_zerodha(bid, ask):
    print(bid, ask)

def write_json(message):
    with open("test.json", "w") as f:
        f.write(json.dumps(message))

async def main():
    #df = await Prices.getHistory("aubank", "1m", "1wk")
    #print(df.head())
    await runAsync.runParallel(
    #     # MoneyControlRSS.getData("TN", "title", print_message), 
    #     # ICICIDirect("TI", print_message).parse(),
    #     # KotakSecurities.run("TC", write_json, False),
    #     # Prices.getHistory("tatamotors", "1d", "1mo"),
    #     # MinMax.getMinMax(df=df, col_name="Close", getMinima=True, window_range=20, callback=print_df, smoothing=14),
    #     # HurstExponent.hurstExponent(df, 100, print_message)
    #     # Samco.get_orderbook("RELIANCE", print_message),
        Zerodha.getOrderBook("RELIANCE", print_zerodha)
    )

asyncio.run(main())

# plot_orderbook()