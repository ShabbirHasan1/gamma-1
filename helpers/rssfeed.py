from re import I
import requests
import xml.etree.ElementTree as ET
import asyncio

from constants import MoneyControlRSSURL
from exceptions import KeyNotFoundException, InvalidDataTypeException

class BaseClass:
    async def __get_request(self, url: str) -> str:
        r = requests.get(url)
        return r.text
    
    async def __parseXML(self, url: str) -> ET.Element:
        xml = await self.__get_request(url)
        return ET.fromstring(xml)

    async def __get_data(self, key: str, url: str, callback):
        element = await self.__parseXML(url)
        for child in element[0].findall('item'):
            callback(child.find(key).text)


    async def get_data(self, url: str, key: str, callback) -> None:
        keys = ['title', 'description', 'pubDate', 'link']
        if key in keys:
            await self.__get_data(key, url, callback)
        else:
            raise KeyNotFoundException(key)

class MoneyControlRSS(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)

    @classmethod
    async def getData(self, dataType: str, key, callback):
        """It gets RSS feed and returns important data from moneycontrol.com RSS feed.

        Available Keys:
            [title]: Title of the article.
            [description]: Description of the article.
            [pubDate]: Publishing date of the article.
            [link]: Link to the article.

        Available DataType:
            [TN] : Top News
            [BD] : Budget News
            [LN] : Latest News
            [PN] : Popular News
            [BN] : Business News
            [PF] : Personal Finance
            [BR] : Brokerage Recommendations
            [BS] : Buzzing Stocks
            [EC] : Economy News
            [MR] : Market Reports
            [AR] : Indian ADRs
            [GM] : Global Markets
            [ME] : Market Edge
            [MO] : Market Outlook
            [TC] : Technicals
            [IPO] : IPO News
            [IN] : Insurance News
            [MF] : Mutual Fund News
            [NN] : NRI News
            [CN] : Commodity News
            [RS] : Results
            [TEC] : Technology News
            [EN] : Entertainment News
            [WN] : World News
            [SN] : Sports News
            [CA] : Current Affairs
            [CUR] : Currency News

        Args:
            dataType (str): Specify RSS section to get data from
            key (_type_): Specify key of the XML
            callback (function): Function to callback everytime it gets data.
        """
        switcher = {
            "TN": MoneyControlRSSURL.TopNews,
            "BD": MoneyControlRSSURL.Budget,
            "LN": MoneyControlRSSURL.LatestNews,
            "PN": MoneyControlRSSURL.PopularNews,
            "BN": MoneyControlRSSURL.BusinessNews,
            "PF": MoneyControlRSSURL.PersonalFinance,
            "BR": MoneyControlRSSURL.BrokersRecommendations,
            "BS": MoneyControlRSSURL.BuzzingStocks,
            "EC": MoneyControlRSSURL.Economy,
            "MR": MoneyControlRSSURL.MarketReports,
            "AR": MoneyControlRSSURL.ADRs,
            "GM": MoneyControlRSSURL.GlobalMarkets,
            "ME": MoneyControlRSSURL.MarketEdge,
            "MO": MoneyControlRSSURL.MarketOutlook,
            "TC": MoneyControlRSSURL.Technicals,
            "IPO": MoneyControlRSSURL.IPONews,
            "IN": MoneyControlRSSURL.InsuranceNews,
            "MF": MoneyControlRSSURL.MutualFundNews,
            "NN": MoneyControlRSSURL.NRINews,
            "CN": MoneyControlRSSURL.CommodityNews,
            "RS": MoneyControlRSSURL.Results,
            "TEC": MoneyControlRSSURL.TechnologyNews,
            "EN": MoneyControlRSSURL.EntertainmentNews,
            "WN": MoneyControlRSSURL.WorldNews,
            "SN": MoneyControlRSSURL.SportsNews,
            "CA": MoneyControlRSSURL.CurrentAffairs,
            "CUR": MoneyControlRSSURL.CurrencyNews
        }
        url = switcher.get(dataType)
        if url is not None:
            await self.get_data(url, key, callback)
        else:
            raise InvalidDataTypeException(dataType)