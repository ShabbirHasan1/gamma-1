from typing import Callable, Dict, List
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from constants import ZerodhaVariables
from exceptions import LoginFailedException

class Zerodha:
    def __init__(self):
        return
    
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
            self.driver.find_element(By.XPATH, r"/html/body/div[1]/div/div/div[1]/div[2]/div/div/form/div[4]/button").click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'//*[@id="pin"]')))
            self.driver.find_element(By.ID, "pin").send_keys(ZerodhaVariables.pin)
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/form/div[3]/button").click()
        except:
            self.driver.get_screenshot_as_file("screenshot_login.png")
            raise LoginFailedException

    def __parse_depth(self, res: List[str]) -> Dict:
        bid_text = res[0]
        ask_text = res[2]
        total_bid_text = res[1]
        total_ask_text = res[3]
        bid: Dict = {}
        ask: Dict = {}
        i: int = 0
        bidList = bid_text.split('\n')
        askList = ask_text.split('\n')
        for i in range(0, len(bidList)):
            bidTemp: Dict = {}
            askTemp: Dict = {}
            bidData = bidList[i].split(' ')
            bidPrice = float(bidData[0])
            bidOrders = bidData[1]
            bidQty = bidData[2]
            askData = askList[i].split(' ')
            askPrice = float(askData[0])
            askOrders = askData[1]
            askQty = askData[2]
            askTemp['orders'] = int(askOrders)
            askTemp['qty'] = int(askQty)
            bidTemp['orders'] = int(bidOrders)
            bidTemp['qty'] = int(bidQty)
            bid[bidPrice] = bidTemp
            ask[askPrice] = askTemp
        bid['total'] = total_bid_text.split(' ')[1]
        ask['total'] = total_ask_text.split(' ')[1]
        return bid, ask 
    
    async def __search_symbol(self, symbol: str, callback: Callable):
        try:
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[2]/div[1]/div/div[1]/div/div/input')))
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/div/div/input").send_keys(symbol)
            a = ActionChains(self.driver)
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[2]/div[1]/div/div[1]/ul/div/li[1]')))
            m = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/ul/div/li[1]")
            a.move_to_element(m).perform()
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/ul/div/li[1]/span[3]/button[4]").click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[2]')))
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[2]").click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[1]/tbody/tr[8]')))
            while True:
                bid = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[1]/tbody")
                total_bid = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[1]/tfoot")
                ask = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[2]/tbody")
                total_ask = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div[2]/div/div/div[1]/div[1]/table[2]/tfoot")
                res = [bid.text, total_bid.text, ask.text, total_ask.text]
                bid, ask = self.__parse_depth(self, res=res)
                callback(bid, ask)
                time.sleep(2)
        except Exception as e:
            print(e)
            self.driver.quit()


    @classmethod
    async def getOrderBook(self, symbol: str, callback: Callable) -> None:
        """Gets order book from zerodha and returns bids and asks to the callable function.

        Args:
            callback (Callable): Callable method to callback. Expects two params.
        """
        try:
            self.__setup_environment(self)
            self.__login_user(self)
            await self.__search_symbol(self, symbol, callback)
        except Exception as e:
            print(e)
            self.driver.quit()