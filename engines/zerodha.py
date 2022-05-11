from typing import List, Dict, Tuple
from pandas import DataFrame, Timestamp

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from constants import ZerodhaVariables, ZerodhaURL, ZerodhaXPaths
from exceptions import LoginFailedException, MarketClosedException, EngineNotStartedException
from .meta import dbHandler

class ZerodhaEngine(dbHandler):
    def __init__(self, scrip: str, verbose: bool = False):
        self.__scrip = scrip
        self.__verbose = verbose
        self.__searched: bool = False
        self.__prevBidPrice: float = 0
        self.__prevAskPrice: float = 0
        self.__prevBidQty: int = 0
        self.__prevAskQty: int = 0
        self.__buyLtq: float = 0
        self.__askLtq: float = 0
        self.__sellExecuted: bool = False
        self.__buyExecuted: bool = False

        dbHandler.__init__(self)
    
    def __setup_environment(self) -> None:
        options = Options()
        options.add_argument(ZerodhaVariables.headlessArgument)
        options.add_argument(ZerodhaVariables.windowSize)
        options.add_argument(ZerodhaVariables.userAgent)
        self.__driver = webdriver.Chrome(options=options)
        self.__driver.get(ZerodhaURL.loginURL)
        if self.__verbose:
            print("[+] Chrome setup done.")

    def __login_user(self) -> None:
        try:
            self.__driver.find_element(By.ID, ZerodhaXPaths.userInputID).send_keys(ZerodhaVariables.username)
            self.__driver.find_element(By.ID, ZerodhaXPaths.passInputID).send_keys(ZerodhaVariables.password)
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.loginButton).click()
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.pinInputID)))
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.pinInputID).send_keys(ZerodhaVariables.pin)
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.verifyButton).click()
            if self.__verbose:
                print(f"[+] User {ZerodhaVariables.username} logged in successfully.")
        except Exception as e:
            if self.__verbose:
                self.__driver.get_screenshot_as_file("screenshot_login.png")
                print(e)
            self.__driver.quit()
            raise LoginFailedException
    
    def __search_symbol(self) -> None:
        try:
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.searchInput)))
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.searchInput).send_keys(self.__scrip)
            a = ActionChains(self.__driver)
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.selectSymbol)))
            m = self.__driver.find_element(By.XPATH, ZerodhaXPaths.selectSymbol)
            a.move_to_element(m).perform()
            self.__searched = True
            if self.__verbose:
                print(f"[+] Searching for {self.__scrip}")
        except Exception as e:
            if self.__verbose:
                self.__driver.get_screenshot_as_file("screenshot_search.png")
                print(e)
            self.__driver.quit()
    
    def __handle_search(self, scrip: str = None) -> None:
        try:
            if self.__searched:
                WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.orderBookSearch)))
                self.__driver.find_element(By.XPATH, ZerodhaXPaths.orderBookSearch).send_keys(scrip)
                a = ActionChains(self.__driver)
                WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.orderBookResult)))
                m = self.__driver.find_element(By.XPATH, ZerodhaXPaths.orderBookResult)
                a.move_to_element(m).perform()
                if self.__verbose:
                    print(f"[+] Changing symbol from {self.__scrip} to {scrip}.")
            else:
                self.__search_symbol()
        except Exception as e:
            if self.__verbose:
                self.__driver.get_screenshot_as_file("screenshot_handle.png")
                print(e)
            self.__driver.quit()
    
    def __click_marketDepth(self) -> None:
        try:
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.marketDepthButton).click()
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.viewMoreButton)))
            self.__driver.find_element(By.XPATH, ZerodhaXPaths.viewMoreButton).click()
            WebDriverWait(self.__driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, ZerodhaXPaths.orderBookElement)))
        except Exception as e:
            if self.__verbose:
                self.__driver.get_screenshot_as_file("screenshot_marketDepth.png")
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
            if self.__verbose:
                print(f"[+] Got data.")
            return res
        except Exception as e:
            if self.__verbose:
                self.__driver.get_screenshot_as_file("screenshot_data.png")
                print(e)
            self.__driver.quit()

    def __parse_depth(self, res: List[str]) -> Tuple[Dict, Dict]:
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
        if self.__verbose:
            print(f"[+] Parsed depth data.")
        return bid, ask
    
    def __create_df(self, bid: Dict, ask: Dict) -> Tuple[DataFrame, DataFrame]:
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
                if self.__prevAskQty > bestAskQty:
                    self.__sellExecuted == True
                elif self.__prevBidQty > bestBidQty:
                    self.__buyExecuted = True
                else:
                    askDf['ltq'] = 0
                    bidDf['ltq'] = 0
            
            self.__prevBidPrice = bidDf.Prices.max()
            self.__prevAskPrice = askDf.Prices.min()
            self.__prevBidQty = bestBidQty
            self.__prevAskQty = bestAskQty

        if self.__sellExecuted:
            try:
                askDf['ltq'] = int(self.__ltq.strip(","))
                bidDf['ltq'] = 0
            except:
                raise MarketClosedException
        elif self.__buyExecuted:
            try:
                bidDf['ltq'] = int(self.__ltq.strip(","))
                askDf['ltq'] = 0
            except:
                raise MarketClosedException
        else:
            bidDf['ltq'] = 0
            askDf['ltq'] = 0

        bidDf['Timestamp'] = Timestamp.now()
        askDf['Timestamp'] = Timestamp.now()

        if self.__verbose:
            print(f"Created bid & ask dataframes.")

        return bidDf, askDf

    def __get_cmp(self) -> str:
        try:
            if self.__verbose:
                print(f"Got LTP: {self.__ltp}")
            return self.__ltp
        except Exception as e:
            if self.__verbose:
                print(e)
            raise EngineNotStartedException

    def __engineHandler(self, scrip: str = None) -> None:
        if self.__searched:
            self.__handle_search(scrip)
        else:
            self.__setup_environment()
            self.__login_user()
            self.__search_symbol()
            self.__click_marketDepth()
        res: List[str] = self.__get_data()
        self.__bid, self.__ask = self.__parse_depth(res)
    
    def getCMP(self, scrip: str = None) -> str:
        """Returns the current market price for a scrip.

        Args:
            scrip (str, optional): Used when changing the symbol. Defaults to None

        Returns:
            str: CMP of the scrip, is in str. As it might contain characters like "," which can throw an exception while converting to int.
        """
        if scrip is not None:
            self.__engineHandler(scrip)
            return self.__get_cmp()
        else:
            self.__engineHandler()
            return self.__get_cmp()

    def getData(self, scrip: str = None) -> Tuple[DataFrame, DataFrame]:
        """Returns two dataframes for for bids and asks table.

        Args:
            scrip (str, optional): Used when changing the symbol. Defaults to None.

        Returns:
            Tuple[DataFrame, DataFrame]: Returns a tuple of two dataframes i.e. bid and ask.
        """
        if scrip is not None:
            self.__engineHandler(scrip)
            return self.__create_df(self.__bid, self.__ask)
        else:
            self.__engineHandler()
            return self.__create_df(self.__bid, self.__ask)
        