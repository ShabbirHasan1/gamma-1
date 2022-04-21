from typing import Callable, Dict, List
import base64

from .base import BaseClass
from constants import KotakSecuritesVariables as KotakConstants
from constants import KotakSecuritiesURL as KotakURLs
from exceptions import InvalidDataTypeException

class KotakSecurities(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)

    def __createPDFLink(self, link: str) -> str:
        baseLink = KotakURLs.basePDFLink
        link = link.encode("ascii")
        encoded = base64.b64encode(link).decode("utf-8")
        return baseLink + encoded

    
    async def __parse(self, callType: str, showFull: bool) -> Dict:
        text = await self.get_text(callType, showFull)
        r = text.split("|")
        i = 0
        data: Dict = {}
        while(i < len(r)-23):
            temp: Dict= {}
            
            symbol = r[i+4]
            segment = r[i+5]
            signal = r[i+6]
            entry = r[i+10]
            target = r[i+12]
            dt = r[i+14]
            status = r[i+15]
            pdf = r[i+24]

            temp['Segment'] = segment
            temp['Signal'] = signal
            temp['Datetime'] = dt
            temp['Entry'] = entry
            temp['Target'] = target
            temp['Status'] = status
            temp['Link'] = self.__createPDFLink(pdf) if len(pdf) > 0 else ''

            data[symbol] = temp

            i += 22

        return data

    @classmethod
    async def run(self, callType: str, callback: Callable, showFull: bool=False) -> None:
        """Returns the calls from Kotak Securities research page

        Args:
            callType (str): Specify the calls type. ["FD" - Fundamental, "TC" - Technical, "DR" - Derivatives]
            callback (Callable): Callable method to callback.
            showFull (bool, optional): Show all the results or just the top calls. Defaults to False.
        """

        allowedTypes: List = ["FD", "TC", "DR"]
        if callType in allowedTypes:

            switcher = {
                "FD": KotakConstants.Fundamentals,
                "TC": KotakConstants.Technicals,
                "DR": KotakConstants.Derivatives
            }
            cType: str = switcher.get(callType)

            data = await self.__parse(callType = cType, showFull = showFull)
            callback(data)
        else:
            raise InvalidDataTypeException(callType)