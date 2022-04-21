from functools import cache
from typing import Dict
import requests
from bs4 import BeautifulSoup as bs4
import base64
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

from exceptions import UncallableMethodException
from constants import ICICIDirectURL, KotakSecuritiesURL

class BaseClass:
    @cache
    def __get_link(self, type: str) -> str:
        switcher = {
            "MI" : ICICIDirectURL.MarketInsights,
            "CA" : ICICIDirectURL.CorporateActions,
            "NW" : ICICIDirectURL.TrendingNews,
            "TI" : ICICIDirectURL.TradingIdeas,
            "II" : ICICIDirectURL.InvestingIdeas,
            "SP" : ICICIDirectURL.SectorPerformance
        }
        return switcher.get(type)
    
    @cache
    def __get_html(self, link: str) -> str:
        r = requests.get(link)
        return r.text

    @cache
    def __create_link(self, ctype: str, isFull: str):
        b64_data = base64.b64encode(f"ReportData=900|||{ctype}|0|-1|{isFull}".encode("ascii")).decode("utf-8")
        time = str(datetime.datetime.timestamp(datetime.datetime.now(datetime.timezone.utc)) * 1000).split('.')
        link = KotakSecuritiesURL.reportLink + b64_data + "&_=" + time[0]
        return link

    @cache
    async def get_text(self, ctype: str, showFull: bool):
        isFull = "3" if showFull else "1"
        link = self.__create_link(ctype, isFull)
        return self.__get_html(link)

    @cache
    async def get_soup(self, type: str) -> bs4:
        return bs4(self.__get_html(self.__get_link(type)), 'lxml')

    async def handle_message(self, key, method, msg, output):
        try:
            output: Dict = {}
            output[key] = msg
            return output if method is None else method(output)
        except TypeError:
            raise UncallableMethodException(method)
