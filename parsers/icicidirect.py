from typing import Dict, List


from exceptions import InvalidMethodException, InvalidDataTypeException
from constants import ICICIDirectVariables as ICICIConstants
from .base import BaseClass


class ICICIDirect(BaseClass):
    def __init__(self, methodType: str, callback = None):
        """It parses the equity section of ICICIDirect and returns info that we need.

        Method types:
            [MI] : Market Insight
            [CA] : Corporate Actions
            [NW] : News
            [TI] : Trading Ideas
            [II] : Investing Ideas
            [SP] : Sector Performance

        Args:
            methodType (str): Type of data we want from the website.
            callback (callable, optional): Function to be called everytime it get's data. Defaults to None
        """

        BaseClass.__init__(self)

        methods = [
            ICICIConstants.MarketInsight, 
            ICICIConstants.CorporateActions, 
            ICICIConstants.News, 
            ICICIConstants.TechnicalIdeas, 
            ICICIConstants.InvestingIdeas, 
            ICICIConstants.SectoralPerformance ]

        if methodType in methods:
            self.__type: str = methodType
        else:
            raise InvalidDataTypeException(methodType)
        self.__method = callback
        self.msg = None

    async def __parseSP(self) -> Dict:
        soup = await self.get_soup(self.__type)
        final: Dict = {}
        res: List = []
        pointer: int = 0
        index: int = 0
        name: str = None
        for line in soup.find_all('td'):
            res.append(line)
        while pointer < len(res):
            temp: Dict = {}
            if len(res[pointer].contents) > 1:
                name = str(res[pointer].contents[1].a.contents[0])
                pointer += 1
            elif '<span>' in str(res[pointer].contents[0]):
                temp['name'] = name
                temp['change'] = str(res[pointer].contents[0].contents[0])
                temp['advanced'] = str(res[pointer+1].contents[0].contents[0])
                temp['decline'] = str(res[pointer+2].contents[0].contents[0])
                final = self.handle_message(index, self.__method, temp, final)
                pointer += 3
                index += 1
            else:
                pointer += 1
        self.msg = final

    async def __parseII(self) -> Dict:
        soup = await self.get_soup(self.__type)
        res: List = []
        final: Dict = {}
        pointer: int = 0

        for line in soup.find_all('td'):
            res.append(line.contents)
        
        while pointer < len(res):
            temp: Dict = {}
            
            name = str(res[pointer][0].contents)
            temp['duration'] = str(res[pointer+2][0]).lstrip().rstrip()
            temp['entry'] = str(res[pointer+3][0]).lstrip().rstrip()
            temp['target'] = str(res[pointer+4][0]).lstrip().rstrip()
            temp['sl'] = str(res[pointer+5][0]).lstrip().rstrip()
            try:
                temp['call'] = str(res[pointer+9][1].contents[0]).lstrip().rstrip()
            except IndexError:
                pass
            try:
                temp['link'] = str(res[pointer+10][1].get('href')).replace(' ','').lstrip().rstrip()
            except IndexError:
                pass
            final = await self.handle_message(name[0], self.__method, temp, final)
            pointer += 11

        self.msg = final
    
    async def __parseTI(self) -> Dict:
        soup = await self.get_soup(self.__type)
        final: Dict = {}

        for line in soup.find_all('tr'):
            temp: Dict = {}
            try:
                scrip = str(line.contents[1].a.contents[0]).lstrip().rstrip()
                temp['date'] = str(line.contents[3].contents[0]).lstrip().rstrip()
                temp['duration'] = str(line.contents[5].contents[0]).lstrip().rstrip()
                temp['entry'] = str(line.contents[9].contents[0]).lstrip().rstrip()
                temp['target'] = str(line.contents[11].contents[0]).lstrip().rstrip()
                temp['sl'] = str(line.contents[13].contents[0]).lstrip().rstrip()
                final = await self.handle_message(scrip, self.__method, temp, final)
            except AttributeError:
                pass

        self.msg = final
    
    async def __parseCA(self) -> Dict:
        soup = await self.get_soup(self.__type)
        final: Dict = {}
        key: int = 0

        for line in soup.find_all('div', class_='media-body BodyDetails'):
            temp: Dict = {}
            temp['title'] = str(line.div.contents[3].a.contents[0]).lstrip().rstrip()
            temp['link'] = str(line.div.contents[3].a.get('href')).lstrip().rstrip()
            temp['date'] = str(line.div.label.span.contents[0]).lstrip().rstrip()
            final = await self.handle_message(key, self.__method, temp, final)
            key += 1

        self.msg = final
    
    async def __parseMI(self) -> Dict:
        soup = await self.get_soup(self.__type)
        final: Dict = {}
        key: int = 0

        for line in soup.find_all('div', class_='media-body BodyDetails'):
            temp: Dict = {}
            temp['title'] = str(line.div.contents[1].a.contents[0]).lstrip().rstrip()
            temp['link'] = str(line.div.contents[3].a.get('href')).lstrip().rstrip()
            temp['desc'] = str(line.div.contents[3].a.contents[0]).lstrip().rstrip()
            final = await self.handle_message(key, self.__method, temp, final)
            key += 1

        self.msg = final
    
    async def __parseNW(self) -> Dict:
        soup = await self.get_soup(self.__type)
        final: Dict = {}
        key: int = 0

        for line in soup.find_all('div', class_='media-body BodyDetails'):
            temp: Dict = {}
            temp['date'] = str(line.div.contents[1].span.contents[0]).lstrip().rstrip()
            temp['title'] = str(line.div.contents[3].a.contents[0]).lstrip().rstrip()
            temp['link'] = str(line.div.contents[3].a.get('href')).lstrip().rstrip()
            final = await self.handle_message(key, self.__method, temp, final)
            key += 1
            
        self.msg = final

    async def parse(self):
        if self.__type == ICICIConstants.InvestingIdeas:
            await self.__parseII()
        elif self.__type == ICICIConstants.CorporateActions:
            await self.__parseCA()
        elif self.__type == ICICIConstants.MarketInsight:
            await self.__parseMI()
        elif self.__type == ICICIConstants.News:
            await self.__parseNW()
        elif self.__type == ICICIConstants.TechnicalIdeas:
            await self.__parseTI()
        elif self.__type == ICICIConstants.SectoralPerformance:
            await self.__parseSP()
        else:
            raise InvalidMethodException(self.__type)