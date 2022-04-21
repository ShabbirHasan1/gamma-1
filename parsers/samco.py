from typing import Callable, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

from constants import SamcoVariable
from exceptions import LoginFailedException

class Samco:
    def __init__(self):
        return

    def __setup_environment(self) -> None:
        options = Options()
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://web.stocknote.com/login")
        self.driver.maximize_window()
    
    def __login_user(self) -> None:
        try:
            self.driver.find_element_by_id("mat-input-0").send_keys(SamcoVariable.username)
            self.driver.find_element_by_id("mat-input-1").send_keys(SamcoVariable.password)
            self.driver.find_element_by_id("mat-input-2").send_keys(SamcoVariable.yob)
            self.driver.find_element_by_tag_name("button").click()
        except:
            raise LoginFailedException

    def __skip_onboarding(self) -> None:
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_xpath('/html/body/app-root/on-boarding/div/div[2]/div[2]/div[3]/div[2]/button').click()
        self.driver.implicitly_wait(1)
        self.driver.find_element_by_xpath('/html/body/app-root/on-boarding/div/div[2]/div[2]/div[3]/div[2]/button').click()
        self.driver.implicitly_wait(1)
        self.driver.find_element_by_xpath('/html/body/app-root/on-boarding/div/div[2]/div[2]/div[3]/div[2]/button').click()
        self.driver.implicitly_wait(1)
        self.driver.find_element_by_xpath('/html/body/app-root/on-boarding/div/div[2]/div[2]/div[3]/div[2]/button').click()
    
    def __skip_guided_tour(self) -> None:
        WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, r'/html/body/app-root/ngx-guided-tour/div[2]/div/div[2]/div[2]/button[1]')))
        self.driver.find_element_by_xpath('/html/body/app-root/ngx-guided-tour/div[2]/div/div[2]/div[2]/button[1]').click()
    
    def __clicking_search(self) -> None:
        self.driver.find_element_by_class_name("cdk-overlay-backdrop").click()
        WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, r'/html/body/app-root/app-user/div/div/div[1]/wlist/div/form/div[3]/div[2]/button[1]/span[1]/mat-icon')))
        self.driver.find_element(By.XPATH, '/html/body/app-root/app-user/div/div/div[1]/wlist/div/form/div[3]/div[2]/button[1]/span[1]/mat-icon').click()
    
    def __switch_exchange(self) -> None:
        WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, r'/html/body/app-root/ngx-guided-tour/div[2]/div/div[2]/div[2]/button[1]')))
        self.driver.find_element(By.XPATH, '/html/body/app-root/ngx-guided-tour/div[2]/div/div[2]/div[2]/button[1]').click()
        if self.driver.find_element(By.XPATH, "/html/body/app-root/quote/div/div/div/div/div/div[3]/div[1]/div/label[1]").is_enabled():
            self.driver.find_element(By.XPATH, "/html/body/app-root/quote/div/div/div/div/div/div[3]/div[1]/div/label[1]").click()
        else:
            pass

    async def __get_orderbook(self, symbol: str, callback: Callable, sleep: int) -> None:
        try:
            WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, r'/html/body/app-root/app-user/div/div/div[1]/wlist/div/form/wl-search-input/div[1]/input')))
            self.driver.find_element(By.XPATH, '/html/body/app-root/app-user/div/div/div[1]/wlist/div/form/wl-search-input/div[1]/input').send_keys(symbol)

            WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, r'/html/body/app-root/app-user/div/div/div[1]/wlist/div/form/wl-search-input/div[2]/a[1]/div[1]')))
            self.driver.find_element(By.XPATH, '/html/body/app-root/app-user/div/div/div[1]/wlist/div/form/wl-search-input/div[2]/a[1]/div[1]').click()
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[1]/div[2]/div[1]')))
            self.__switch_exchange(self)
            while True:
                WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[1]/div[2]/div[1]')))
                bid_column = self.driver.find_element(By.XPATH, '/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[1]/div[2]/div[1]')
                ask_column = self.driver.find_element(By.XPATH, '/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[1]/div[2]/div[3]')
                WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, r'/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[2]/div[2]/div[2]/market-data-value2/div/div[8]/div/div[2]')))
                ltq = self.driver.find_element(By.XPATH, '/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[2]/div[2]/div[2]/market-data-value2/div/div[8]/div/div[2]')
                volumeinrs = self.driver.find_element(By.XPATH, '/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[2]/div[2]/div[2]/market-data-value2/div/div[6]/div/div[2]')
                volumeinshares = self.driver.find_element(By.XPATH, '/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[2]/div[2]/div[1]/market-data-value/div/div[5]/div/div[2]')
                atp = self.driver.find_element(By.XPATH, '/html/body/app-root/quote/div/div/div/div/quote-screen/div/div[2]/div/div/div/market-depth/div[2]/div[2]/div[1]/market-data-value/div/div[7]/div/div[2]')
                bc = bid_column.text.split('\n')
                ac = ask_column.text.split('\n')
                marketinfo = [ltq.text, volumeinrs.text, volumeinshares.text, atp.text]
                res: List = [bc, ac, marketinfo]
                callback(res)
                time.sleep(sleep)
        except KeyboardInterrupt:
            return

    
    async def __run(self):
        self.__setup_environment(self)
        self.__login_user(self)
        self.__skip_onboarding(self)
        self.__skip_guided_tour(self)
        self.__clicking_search(self)

    @classmethod
    async def get_orderbook(self, scrip: str, callback: Callable, sleep:int = 5):
        """Returns a list of lists containing bid and ask orders with relevant market informations.
        
        [ [BID COLUMN], [ASK COLUMN], [Market Info] ]

        [Market Info] - [Last Traded Volume, Volume (in Rs.), Volume (in Shares), Average Traded Price]

        Args:
            symbol (str): Specify the symbol you want data for.
            callback (Callable): A callable method to call when we get data

        Returns:
            List[List[str]]: Returns a list of lists, it returns to callable method. This method returns None.
        """
        await self.__run(self)
        await self.__get_orderbook(self, scrip, callback, sleep)
