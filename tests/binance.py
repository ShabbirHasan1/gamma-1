'''
It was made for testing purpose only, since I develop this project after market hours and some data isn't available after market
hours. So I develop this project using crypto simulated data, as the crypto markets are always open.
'''

from matplotlib.animation import FuncAnimation
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import deque
from typing import Dict, List
import mplcursors

# np.random.seed(32)

# fig, ax = plt.subplots()
# #ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
# bidX = deque(maxlen=60)
# bidY = deque(maxlen=60)
# askX = deque(maxlen=60)
# askY = deque(maxlen=60)
# bidSize = deque(maxlen=60)
# askSize = deque(maxlen=60)
# quantityList: List = []

# from collections import OrderedDict

# class FixedDict(OrderedDict):
#     def __init__(self, *args, maxlen: int=0, **kwargs):
#         self.__maxlen = maxlen
#         super().__init__(*args, **kwargs)
    
#     def __setitem__(self, key, value) -> None:
#         OrderedDict.__setitem__(self, key, value)
#         if self.__maxlen > 0:
#             if len(self) > self.__maxlen:
#                 self.popitem(False)

# hashMap = FixedDict(maxlen=60)

# def getData():
#     r = requests.get("https://api.binance.com/api/v3/depth", params=dict(symbol="ETHBUSD"))
#     results = r.json()

#     rt = requests.get("https://api.binance.com/api/v3/trades", params=dict(symbol="ETHBUSD"))
#     rtres = rt.json()

#     frames = {side: pd.DataFrame(data=results[side], columns=["price", "quantity"], dtype=float) for side in ["bids", "asks"]}
#     frames_list = [frames[side].assign(side=side) for side in frames]
#     data = pd.concat(frames_list, axis="index", ignore_index=True, sort=True)
#     data['timestamp'] = pd.to_datetime('now')
#     return frames, data, rtres

# def animate(i):
#     frames, data, rt = getData()

#     plt.cla()
#     sns.histplot(data=data, x="quantity", y="price", hue="side", ax=ax, kde=True)
#     plt.grid(True)

#     bidY.append(float(frames["bids"].price.max()))
#     askY.append(float(frames["asks"].price.min()))
#     bidX.append(data['timestamp'][0])
#     askX.append(data['timestamp'][0])
#     bidSize.append(float(rt[0]['qty']) * 100)
#     askSize.append(float(rt[3]['qty']) * 100)
    
#     # quantityList = data['quantity'].values
#     # hashMap[data['timestamp'][0]] = list(quantityList)
#     # df = pd.DataFrame(hashMap)
#     # df.index = data['price']

#     plt.cla()
#     #ax.set_ylim([float(frames["bids"].price.min()), float(frames["asks"].price.max())])

#     # sns.heatmap(df, vmin=data['quantity'].min(), vmax=data['quantity'].max(), cbar=False, ax=ax, cmap='GnBu', alpha=0.5)

#     ax2 = plt.twinx()

#     # sns.lineplot(x=list(bidX), y=list(bidY), color='green', linewidth=2, ax=ax2)
#     # sns.lineplot(x=list(askX), y=list(askY), color='red', linewidth=2, ax=ax2)
#     ax2.scatter(list(bidX), list(bidY), s=list(bidSize), color='b', marker='o', alpha=0.8)
#     ax2.scatter(list(askX), list(askY), s=list(askSize), color='r', marker='o', alpha=0.8)
#     # ax2.set_ylim([data['price'].min(), data['price'].max()])
#     #fig.show()

#     mplcursors.cursor.connect("add", lambda x: x.annotation.set_text(f"Bid Size: {bidSize[-1]}\nAsk Size: {askSize[-1]}"))

#     #sns.ecdfplot(x="price", weights="quantity", stat="count", complementary=True, data=frames["bids"], ax=ax1, color='g')
#     #sns.ecdfplot(x="price", weights="quantity", stat="count", data=frames["asks"], ax=ax1, color='r')
#     plt.grid(linestyle='-', linewidth=0.5)
#     plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

# def plot():
#     ani = FuncAnimation(fig=fig, func=animate, frames=220, interval=1000)
#     plt.show()

#plot()

# frames, data, rt = getData()
# print(data.head())
# table = pd.pivot_table(data=data, index=['price'], values=['quantity'])
# if prevTable is None:
#     prevTable = table
# else:
#     table.merge(prevTable, on="price", how="left")
# print(table)
#sns.heatmap(table)
#plt.show()

# for i in range(5):
#     frames, data, rt = getData()
#     quantityList = data['quantity'].values
#     hashMap[data['timestamp'][0]] = list(quantityList)
#     df = pd.DataFrame(hashMap)
#     df.index = data['price']

# sns.heatmap(df)
# plt.show()

# df = pd.DataFrame(
#     [("Alice", 163, 54),
#      ("Bob", 174, 67),
#      ("Charlie", 177, 73),
#      ("Diane", 168, 57)],
#     columns=["name", "height", "weight"])

# df.plot.scatter("height", "weight")
# mplcursors.cursor().connect(
#     "add", lambda sel: sel.annotation.set_text(df["name"][sel.index]))
# plt.show()


fig = plt.figure()
ax = fig.add_axes([0,0,2,2])
fig.show()