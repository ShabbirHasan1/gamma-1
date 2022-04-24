'''
This one just to understand the structure of the df during ordermap.
'''

# from pandas import DataFrame

# data1 = {"price": [128.00, 128.05, 128.10], "qty": [1200, 970, 800]}
# df1 = DataFrame(data1)

# print(df1.price.min())
# index = df1[df1['price'] == df1.price.min()].index.values
# print(df1.loc[index, 'qty'].values[0])


# import requests
# import pandas as pd
# import time
# df = pd.DataFrame()
# for i in range(20):
#     df = pd.concat([df, pd.json_normalize(requests.get("https://api.cryptowat.ch/markets/kraken/btcusd/orderbook").json()["result"]).assign(timestamp=pd.to_datetime("now"))])
#     time.sleep(1)

# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# d = df.loc[:, ["timestamp", "asks"]].explode("asks").assign(
#     price=lambda d: d["asks"].apply(lambda a: a[0]),
#     size=lambda d: d["asks"].apply(lambda a: a[1]),
# )

# fig, ax = plt.subplots()
# sns.heatmap(data=d, vmin=30, vmax=70)
# plt.show()

#px.scatter(d, x="timestamp", y="size", color="price")
#fig = go.Figure(go.Heatmap(x=d["timestamp"], y=d["size"], z=d["price"]))
#fig.show()

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

data = np.random.rand(6, 5)
'''
Ok so what's happening here is it is creating a 2-D array.

data[0][0] --> square at 1st row and 1st column
data[5][5] -> square at 4th row and 4th column

So the first axis in our case should be the time, and it will continue to go up and y axis is the price and the hue is dependent
on the qty.

So our array should look something like this

[
    [P1T1, P1T2...],
    [P2T1, P2T2...],
    [P3T1, P3T2...],
    [P4T1, P4T2...],
    [P5T1, P5T2...],
    [P6T1, P6T2...]
]

'''
print(data)
map = sns.heatmap(data, yticklabels=False)
plt.show()