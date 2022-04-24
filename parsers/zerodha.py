from typing import Dict, List
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame, to_datetime, concat
from collections import deque
from numpy import log

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from constants import ZerodhaVariables, ZerodhaURL
from constants import ZerodhaXPaths
from exceptions import LoginFailedException, MarketClosedException

class Zerodha:
    def __init__(self, symbol: str):
        self.__symbol = symbol
        
        plt.rcParams.update({'font.size': 8})
        self.__fig, self.__ax = plt.subplots()
        self.__bidX = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__bidY = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__askX = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__askY = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__bidVolume = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__askVolume = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__mergedX = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__mergedY = deque(maxlen=ZerodhaVariables.dequeMaxLen)
        self.__mergedSize = deque(maxlen=ZerodhaVariables.dequeMaxLen)

        self.__prevBidPrice: float = 0
        self.__prevAskPrice: float = 0
        self.__prevBidQty: int = 0
        self.__prevAskQty: int = 0
        self.__sellExecuted: bool = False
        self.__buyExecuted: bool = False

        self.__setup_environment()
    
    def __setup_environment(self):
        options = Options()
        options.add_argument(ZerodhaVariables.headlessArgument)
        options.add_argument(ZerodhaVariables.windowSize)
        options.add_argument(ZerodhaVariables.userAgent)
        self.__driver = webdriver.Chrome(options=options)
        self.__driver.get(ZerodhaURL.loginURL)

        self.__login_user()
        self.__search_symbol()

    def __login_user(self):
        try:
            self.__driver.find_element(By.ID, ZerodhaXPaths.userInputID).send_keys(ZerodhaVariables.username)
            self.__driver.find_element(By.ID, ZerodhaXPaths.passInputID).send_keys(ZerodhaVariables.password)
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.loginButton).click()
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.pinInputID)))
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.pinInputID).send_keys(ZerodhaVariables.pin)
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.verifyButton).click()
        except Exception as e:
            self.__driver.get_screenshot_as_file("screenshot_login.png")
            self.__driver.quit()
            raise LoginFailedException
    
    def __search_symbol(self) -> None:
        try:
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.searchInput)))
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.searchInput).send_keys(self.__symbol)
            a = ActionChains(self.__driver)
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.selectSymbol)))
            m = self.__driver.find_element(By.XPATH, ZerodhaXPaths.selectSymbol)
            a.move_to_element(m).perform()
        except Exception as e:
            print(e)
            self.__driver.quit()

    def __click_marketDepth(self) -> None:
        try:
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.marketDepthButton).click()
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.viewMoreButton)))
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.viewMoreButton).click()
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.orderBookElement)))
        except Exception as e:
            print(e)
            self.__driver.quit()

    def __get_data(self) -> List[str]:
        try:
            bid = self.__driver.find_element(By.XPATH, ZerodhaXPaths.bidsTables)
            total_bid = self.__driver.find_element(By.XPATH, ZerodhaXPaths.totalBid)
            ask = self.__driver.find_element(By.XPATH, ZerodhaXPaths.asksTable)
            total_ask = self.__driver.find_element(By.XPATH, ZerodhaXPaths.totalAsk)
            self.__ltp = self.__driver.find_element(By.XPATH, ZerodhaXPaths.ltp).text
            self.__ltq = self.__driver.find_element(By.XPATH, ZerodhaXPaths.ltq).text
            res = [bid.text, total_bid.text, ask.text, total_ask.text, self.__ltp, self.__ltq]
            return res
        except Exception as e:
            print(e)
            self.__driver.quit()

    def __parse_depth(self, res: List[str]) -> Dict:
        bid_text = res[0]
        ask_text = res[2]
        bid: Dict = {}
        ask: Dict = {}
        i: int = 0
        bidList = bid_text.split('\n')
        askList = ask_text.split('\n')
        for i in range(0, len(bidList)):
            bidTemp: Dict = {}
            askTemp: Dict = {}
            bidData = bidList[i].split(' ')
            bidPrice = bidData[0]
            bidOrders = bidData[1]
            bidQty = bidData[2]
            askData = askList[i].split(' ')
            askPrice = askData[0]
            askOrders = askData[1]
            askQty = askData[2]
            askTemp['orders'] = int(askOrders)
            askTemp['qty'] = int(askQty)
            bidTemp['orders'] = int(bidOrders)
            bidTemp['qty'] = int(bidQty)
            bidTemp['price'] = bidPrice
            bid[bidPrice] = bidTemp
            ask[askPrice] = askTemp
        return bid, ask

    def __create_df(self, bid: Dict, ask: Dict) -> DataFrame:
        bidPrices: List[float] = []
        bidOrders: List[int] = []
        bidQty: List[int] = []
        askPrices: List[float] = []
        askOrders: List[int] = []
        askQty: List[int] = []
        for keys in bid:
            bidPrices.append(float(keys.strip(",")))
            bidOrders.append(bid[keys]['orders'])
            bidQty.append(bid[keys]['qty'])
        
        for keys in ask:
            askPrices.append(float(keys.strip(",")))
            askOrders.append(ask[keys]['orders'])
            askQty.append(ask[keys]['qty'])
        
        bidDf = DataFrame({'Prices': bidPrices, 'Orders': bidOrders, 'Qty': bidQty})
        askDf = DataFrame({'Prices': askPrices, 'Orders': askOrders, 'Qty': askQty})

        bestBidQty = bidDf.loc[bidDf[bidDf['Prices'] == bidDf.Prices.max()].index.values, 'Qty'].values[0]
        bestAskQty = askDf.loc[askDf[askDf['Prices'] == askDf.Prices.min()].index.values, 'Qty'].values[0]

        if self.__prevBidPrice == 0 or self.__prevAskPrice == 0:
            self.__prevBidPrice = bidDf.Prices.max()    
            self.__prevBidQty = bestBidQty 
            self.__prevAskPrice = askDf.Prices.min()
            self.__prevAskQty = bestAskQty
            askDf['ltq'] = 0
            bidDf['ltq'] = 0

        else:
            if self.__prevAskPrice > askDf.Prices.min():
                self.__sellExecuted = True
            elif self.__prevBidPrice < bidDf.Prices.max():
                self.__buyExecuted = True
            else:
                if self.__prevAskQty > askQty:
                    self.__sellExecuted == True
                elif self.__prevBidQty > bidQty:
                    self.__buyExecuted = True
            
            self.__prevBidPrice = bidDf.Prices.max()
            self.__prevAskPrice = askDf.Prices.min()
            self.__prevBidQty = bestBidQty
            self.__prevAskQty = bestAskQty

        if self.__sellExecuted:
            try:
                askDf['ltq'] = int(self.__ltq.strip(","))
            except:
                raise MarketClosedException
        elif self.__buyExecuted:
            try:
                bidDf['ltq'] = int(self.__ltq.strip(","))
            except:
                raise MarketClosedException
        else:
            pass

        bidDf['Timestamp'] = to_datetime('now')
        askDf['Timestamp'] = to_datetime('now')

        return bidDf, askDf
    
    def __animate_depthgraph(self, i):
        text = self.__get_data()
        bidD, askD = self.__parse_depth(text)
        bid, ask = self.__create_df(bidD, askD)
        plt.cla()
        
        plt.setp(self.__ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.grid(linestyle='-', linewidth=0.5)
        self.__ax.set_title(f"Depth graph for {self.__symbol} - {self.__ltp}")
        self.__ax.set_xlabel("Prices")
        self.__ax.set_ylabel("Qty")
        sns.ecdfplot(x="Prices", weights="Qty", stat="count", complementary=True, data=bid, ax=self.__ax, color='g')
        sns.ecdfplot(x="Prices", weights="Qty", stat="count", data=ask, ax=self.__ax, color='r')

    def __animate_ordermap(self, i):
        text = self.__get_data()
        bidD, askD = self.__parse_depth(text)
        bid, ask = self.__create_df(bidD, askD)
        merged = concat([bid, ask], ignore_index=True)
        
        self.__bidX.append(bid['Timestamp'][0])
        self.__bidY.append(bid['Prices'].max())
        self.__askX.append(ask['Timestamp'][0])
        self.__askY.append(ask['Prices'].min())
        self.__mergedX.append(merged['Timestamp'][0])
        self.__mergedY.append(merged['Prices'])
        if self.__buyExecuted:
            self.__bidVolume.append(log(bid['ltq'][0]))
            self.__askVolume.append(0)
        elif self.__sellExecuted:
            self.__askVolume.append(log(ask['ltq'][0]))
            self.__bidVolume.append(0)
        else:
            self.__bidVolume.append(0)
            self.__askVolume.append(0)

        plt.cla()
        plt.setp(self.__ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.grid(linestyle='-', linewidth=0.5)
        
        self.__ax.set_title(f"Order map for {self.__symbol} - {self.__ltp}")
        self.__ax.set_xlabel("Timestamp")
        self.__ax.set_ylabel("Prices")
        self.__ax.set_ylim([bid['Prices'].min(), ask['Prices'].max()])
        self.__ax.plot(list(self.__bidX), list(self.__bidY), color='green')
        self.__ax.plot(list(self.__askX), list(self.__askY), color='red')
        self.__ax.scatter(list(self.__bidX), list(self.__bidY), s=list(self.__bidVolume), color='b', alpha=0.7, marker='.')
        self.__ax.scatter(list(self.__askX), list(self.__askY), s=list(self.__askVolume), color='r', alpha=0.7, marker='.')
        
        # this shouldn't work but i need to see how it seems in real time.
        # and also I do have the alternative if that doesn't work. But I think it might be slow, since it has to create 
        # a whole new dataframe so I also might need to find a solution to that.
        sns.scatterplot(data=merged, x="Timestamp", y="Prices", hue="Qty", alpha=0.5, ax=self.__ax)

    def __plot_ordermap(self):
        ani = FuncAnimation(fig=self.__fig, func=self.__animate_ordermap, frames=220, interval=1000)
        plt.show()

    def __plot_depthgraph(self) -> None:
        ani = FuncAnimation(fig=self.__fig, func = self.__animate_depthgraph, frames=220, interval=1000)
        plt.show()
    
    async def plotDepthGraph(self) -> None:
        """Gets market depth from zerodha and plots depth graph in matplotlib.
        """
        try:
            self.__click_marketDepth()
            self.__plot_depthgraph()
        except Exception as e:
            print(e)
            self.__driver.quit()
    
    async def plotOrderMap(self) -> None:
        """Gets orderbook from Zerodha and plots LBO map in matplotlib.
        """
        try:
            self.__click_marketDepth()
            self.__plot_ordermap()
        except Exception as e:
            print(e)
            self.__driver.quit()
    
    async def placeBuyOrder(self) -> None:
        return

    async def placeSellOrder(self) -> None:
        return

    async def placeGTTOrder(self) -> None:
        return