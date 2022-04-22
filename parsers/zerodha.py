from typing import Callable, Dict, List
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from constants import ZerodhaVariables
from exceptions import LoginFailedException

class Zerodha:
    def __init__(self, symbol: str):
        self.__symbol = symbol
        plt.rcParams.update({'font.size': 8})
        self.__fig, self.__ax = plt.subplots()
    
    def __setup_environment(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://kite.zerodha.com')

    def __login_user(self):
        try:
            self.driver.find_element(By.ID, "userid").send_keys(ZerodhaVariables.username)
            self.driver.find_element(By.ID, "password").send_keys(ZerodhaVariables.password)
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[4]/button").click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'//*[@id="pin"]')))
            self.driver.find_element(By.ID, "pin").send_keys(ZerodhaVariables.pin)
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/button").click()
        except Exception as e:
            self.driver.get_screenshot_as_file("screenshot_login.png")
            self.driver.quit()
            raise LoginFailedException

    def __create_df(self, bid: Dict, ask: Dict) -> DataFrame:
        bidPrices: List[float] = []
        bidOrders: List[int] = []
        bidQty: List[int] = []
        askPrices: List[float] = []
        askOrders: List[int] = []
        askQty: List[int] = []
        for keys in bid:
            bidPrices.append(keys)
            bidOrders.append(bid[keys]['orders'])
            bidQty.append(bid[keys]['qty'])
        
        for keys in ask:
            askPrices.append(keys)
            askOrders.append(ask[keys]['orders'])
            askQty.append(ask[keys]['qty'])
        
        bidDf = DataFrame({'Prices': bidPrices, 'Orders': bidOrders, 'Qty': bidQty})
        askDf = DataFrame({'Prices': askPrices, 'Orders': askOrders, 'Qty': askQty})

        return bidDf, askDf

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
    
    def __search_symbol(self) -> None:
        try:
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[2]/div[1]/div/div[1]/div/div/input')))
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/div/div/input").send_keys(self.__symbol)
            a = ActionChains(self.driver)
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[2]/div[1]/div/div[1]/ul/div/li[1]')))
            m = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/ul/div/li[1]")
            a.move_to_element(m).perform()
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/ul/div/li[1]/span[3]/button[4]").click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[2]')))
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[2]").click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[1]/tbody/tr[8]')))
        except Exception as e:
            print(e)
            self.driver.quit()
        
    def __get_data(self) -> List[str]:
        try:
            bid = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[1]/tbody")
            total_bid = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[1]/tfoot")
            ask = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[2]/tbody")
            total_ask = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[2]/tfoot")
            res = [bid.text, total_bid.text, ask.text, total_ask.text]
            return res
        except Exception as e:
            print(e)
            self.driver.quit()
    
    def __animate(self, i):
        text = self.__get_data()
        bidD, askD = self.__parse_depth(text)
        bid, ask = self.__create_df(bidD, askD)
        bid, ask = self.__create_df(bidD, askD)
        plt.cla()
        plt.setp(self.__ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        self.__ax.set_title(f"Order book for {self.__symbol}")
        self.__ax.set_xlabel("Prices")
        self.__ax.set_ylabel("Qty")
        sns.ecdfplot(x="Prices", weights="Qty", stat="count", complementary=True, data=bid, ax=self.__ax, color='g')
        sns.ecdfplot(x="Prices", weights="Qty", stat="count", data=ask, ax=self.__ax, color='r')
    
    def __plot_df(self) -> None:
        ani = FuncAnimation(fig=self.__fig, func = self.__animate, frames=220, interval=1000)
        plt.show()

    async def plotOrderBook(self) -> None:
        """Gets order book from zerodha and plots orderbooks in matplotlib.
        """
        try:
            self.__setup_environment()
            self.__login_user()
            self.__search_symbol()
            self.__plot_df()
        except Exception as e:
            print(e)
            self.driver.quit()