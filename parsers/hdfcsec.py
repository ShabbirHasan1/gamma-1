from .base import BaseClass

class HDFCSec(BaseClass):
    def __init__(self, methodType: str, callback: str):
         """It parses the HDFC Secturies and returns info that we need.

        Method types:
            [MI] : Market Insight
            [CA] : Corporate Actions
            [NW] : News
            [TI] : Trading Ideas
            [II] : Investing Ideas
            [SP] : Sector Performance

        Args:
            methodType (str): Type of data we want from the website.
            method (callable, optional): Function to be called everytime it get's data. Defaults to None
        """