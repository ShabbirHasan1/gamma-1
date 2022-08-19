'''
Implementation of Samco Stock note bridge APIs in python.
'''

from typing import Callable, Dict, List
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import json

from constants import SamcoVariable
from exceptions import StocknoteAPIException

class StocknoteAPI:
    def __init__(self):
        self.__userId: str = SamcoVariable.username
        self.__password: str = SamcoVariable.password
        self.__yob: str = SamcoVariable.yob

        self.__samco = StocknoteAPIPythonBridge()

        self.SEGMENT_NSE = self.__samco.EXCHANGE_NSE
        self.SEGMENT_NFO = self.__samco.EXCHANGE_NFO
        self.SEGMENT_BSE = self.__samco.EXCHANGE_BSE
        self.CALL_OPTION = "CE"
        self.PUT_OPTION = "PE"
        self.BUY = self.__samco.TRANSACTION_TYPE_BUY
        self.SELL = self.__samco.TRANSACTION_TYPE_SELL
        self.LIMIT_ORDER = self.__samco.ORDER_TYPE_LIMIT
        self.MARKET_ORDER = "MKT"
        self.STOP_LOSS = "SL"
        self.STOP_LOSS_MKT = "SL-M"
        self.LTP_PRICE_TYPE = "LTP"
        self.ATP_PRICE_TYPE = "ATP"
        self.TYPE_CNC = "CNC"
        self.TYPE_MIS = "MIS"
        self.TYPE_NORMAL = "NRML"
        self.VALIDITY_DAY = "DAY"
        self.VALIDITY_IOC = "IOC"

        self.__isSessionAlive: bool = False

    def __setSession(self) -> None:
        try:
            login = self.__samco.login(body={"userId": self.__userId, 'password': self.__password, 'yob': self.__yob})
            login = json.loads(login)
            if login['status'] == 'Success':
                token = login['sessionToken']
                self.__samco.set_session_token(token)
                self.__isSessionAlive = True
            else:
                raise StocknoteAPIException("Something went wrong in setting the session.")
        except:
            raise StocknoteAPIException("Something went wrong in setting the session.")

    def searchEquityDerivative(self, scrip: str, exchange) -> List:
        """Search symbols from Futures and Options segment.

        Args:
            scrip (str): Contains the scrip name. e.g.: BANKNIFTY23JUN
            exchange: Contains the segments. For F&O use: self.__samco.EXCHANGE_NFO

        Raises:
            SessionAPIException: If something went wrong with finding the results.

        Returns:
            List: Containing dictionaries of results.
            [
                {'exchange': 'NFO', 'tradingSymbol': 'BANKNIFTY23JUN43500PE', 'bodLotQuantity': '25', 'instrument': 'OPTIDX'}, 
                {'exchange': 'NFO', 'tradingSymbol': 'BANKNIFTY23JUN45000PE', 'bodLotQuantity': '25', 'instrument': 'OPTIDX'}, 
                {'exchange': 'NFO', 'tradingSymbol': 'BANKNIFTY23JUN46500PE', 'bodLotQuantity': '25', 'instrument': 'OPTIDX'}
            ]
        """
        if self.__isSessionAlive:
            results = self.__samco.search_equity_derivative(search_symbol_name = scrip, exchange = exchange)
            results = json.loads(results)
            try:
                if results['status'] == 'Success':
                    return results['searchResults']
                else:
                    raise StocknoteAPIException(f"Couldn't find results for: {scrip}")
            except KeyError:
                raise StocknoteAPIException(f"Something went wrong while searching for symbol: {scrip}")
        else:
            raise StocknoteAPIException("Session is not alive")
    
    def getQuote(self, scrip: str, exchange, callback: Callable = None) -> Dict:
        """Get market depth details for a specific equity or nfo scrip.

        Args:
            scrip (str): Contains the scrip name. e.g. HDFCBANK
            exchange (_type_): Contains the segment.
            callback (Callable, optional): Function to call to everytime it returns something. Defaults to None.

        Returns:
            Dict: Containing market depth data.
        """
        if self.__isSessionAlive:
            quote = self.__samco.get_quote(symbol_name = scrip, exchange = exchange)
            quote = json.loads(quote)
            try:
                if quote['status'] == 'Success':
                    return quote if callback is None else callback(quote)
                else:
                    raise StocknoteAPIException(f"Couldn't find result for: {scrip}")
            except KeyError:
                raise StocknoteAPIException(f"Something went wrong while getting quotes for: {scrip}")
        else:
            raise StocknoteAPIException("Session is not alive")
        
    def getOptionChain(self, scrip: str, exchange, expiry: str, strike: str, type: str, callback: Callable = None) -> Dict:
        """Used to search OptionChain for equity, derivatives and commodity scrips based on user provided search symbol and exchange name.

        Args:
            scrip (str): Contains the scrip name
            exchange (_type_): Contains the segment type
            expiry (str): Expiry date in format of: YYYY-MM-DD
            strike (str): Contains the strike price
            type (str): Contains the option type. for e.g.: self.CALL_OPTION
            callback (Callable, optional): Function to call everytime it returns something. Defaults to None.

        Returns:
            Dict: Containing option chain data
        """
        if self.__isSessionAlive:
            results = self.__samco.get_option_chain(
                search_symbol_name = scrip, 
                exchange = exchange, 
                expiry_date = expiry, 
                strike_price = strike, 
                option_type = type)
            results = json.loads(results)
            try:
                if results['status'] == 'Success':
                    return results if callback is None else callback(results)
                else:
                    raise StocknoteAPIException(f"Couldn't find result for: {scrip}")
            except KeyError:
                raise StocknoteAPIException(f"Something went wrong while getting option chain for: {scrip}")
        else:
            raise StocknoteAPIException("Session is not alive")

    def getMargins(self) -> Dict:
        """Used to gets the user cash balances, available margin for trading in equity and commodity segments.

        Raises:
            StocknoteAPIException: If session is not alive

        Returns:
            Dict: Containing the available margins.
        """
        if self.__isSessionAlive:
            margins = self.__samco.get_limits()
            margins = json.loads(margins)
            return margins
        else:
            raise StocknoteAPIException("Session is not alive")
    
    def placeOrder(self, scrip: str, exchange: str, transactionType: str, orderType: str, price: str, quantity: str, priceType: str = "LTP", marketProtection: str = "3%", orderValidity: str = "DAY", amoFlag: str = "NO", productType: str = "MIS", triggerPrice: str = None, disclosedQty: str = "") -> tuple([str, str]):
        """Used to place an equity/derivative order to the exchange i.e the place order request typically registers the order with OMS 
        and when it happens successfully, a success response is returned. 
        
        Successful placement of an order via the function does not imply its successful execution. When an order is successfully placed
        the function returns an OrderNumber in response, and the actual order status can be checked separately using the 
        getOrderStatus() .This is for Placing CNC, MIS and NRML Orders.

        Args:
            scrip (str): Trading Symbol Name of the scrip
            exchange (str): Name of the exchange.Valid exchanges values (BSE/ NSE/ NFO/ MCX/ CDS).If the user does not provide an exchange name, by default considered as NSE.For trading with BSE, NFO, CDS and MCX, exchange is mandatory.
            transactionType (str): Transaction type should be BUY or SELL
            orderType (str): Type of order. It can be one of the following, MKT - Market Order,L- Limit Order,SL - Stop Loss Limit,SL-M - Stop loss market
            price (str): Price at which the order will be placed
            quantity (str): Quantity with which order is being placed
            disclosedQty (str, optional): If provided should be minimum of 10% of actual quantity. Defaults to "".
            priceType (str, optional): Price type required to place an order. Valid price type - LTP/ATP , default is LTP. Applicable for BO orders only. Defaults to "LTP".
            marketProtection (str, optional): Percentage of MarketProtection required for ordertype MKT/SL-M to limit loss due to market price changes against the price with which order is placed. Default value is 3%.
            orderValidity (str, optional): Order validity can be DAY / IOC. Defaults to "DAY".
            amoFlag (str, optional): After Market Order Flag YES/NO. Defaults to "NO".
            productType (str, optional): Product Type of the order. It can be CNC (Cash and Carry)NRML (Normal),MIS (Intraday). Defaults to "MIS".
            triggerPrice (str, optional): The price at which an order should be triggered in case of SL, SL-M. Defaults to None.
        
        Returns:
            tuple(str, str): Returns the order number and order status or execution price in a tuple.
        """
        if self.__isSessionAlive:
            request = self.__samco.place_order(
                body = {
                    "symbolName": scrip,
                    "exchange": exchange,
                    "transactionType": transactionType,
                    "orderType": orderType,
                    "quantity": quantity,
                    "disclosedQuantity": disclosedQty,
                    "price": price,
                    "priceType": priceType,
                    "marketProtection": marketProtection,
                    "orderValidity": orderValidity,
                    "afterMarketOrderFlag": amoFlag,
                    "productType": productType,
                    "triggerPrice": triggerPrice
                }
            )
            request = json.loads(request)
            try:
                if request['status'] == 'Success':
                    if request['rejectionReason'] != "--":
                        raise StocknoteAPIException(f"Order rejected: {request['rejectionReason']}")
                    if request['exchangeOrderStatus'] == 'complete':
                        return ([request['orderNumber'], request['orderDetails']['avgExecutionPrice']])
                    else:
                        return ([request['orderNumber'], request['ex changeOrderStatus']])
                else:
                    raise StocknoteAPIException("Unable to process the order.")
            except KeyError:
                raise StocknoteAPIException("Something went wrong while placing an order.")
        else:
            raise StocknoteAPIException("Session is not alive")

    def run(self):
        self.__setSession()
        res = self.getOptionChain("BANKNIFTY", self.SEGMENT_NSE, "2022-08-25", "40000", self.CALL_OPTION)
        print(res)
        #results = self.placeOrder("HDFCBANK", self.SEGMENT_NSE, self.BUY, self.MARKET_ORDER, "1427.05", "10")
        #print(results)
