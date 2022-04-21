import base64
import sys
import json
from .logger import writeline
from .ohlc import handleOHLC

import websocket

from .defaults import WEBSOCKET_URL, TICKER_LIST
from .yticker_pb2 import yticker
from utils import runAsync

try:
    import thread
except ImportError:
    import _thread as thread


class metaTicker:
    async def __init__(self, on_ticker = None, ticker_names = TICKER_LIST, on_error = None, on_close = None, enable_socket_trace = False, createOHLC = False, interval='1s'):
        self.symbol_list = dict()
        self.symbol_list["subscribe"] = ticker_names

        self.interval = interval

        websocket.enableTrace(enable_socket_trace)

        self.on_ticker = on_ticker
        self.on_custom_close = on_close
        self.on_custom_error = on_error

        self.createOHLC = createOHLC

        self.yticker = yticker()
        self.ticker_name = ticker_names
        self.ws = websocket.WebSocketApp(WEBSOCKET_URL, on_message=await self.on_message, on_error = await self.on_error, on_close=await self.on_close)
        self.ws.on_open = self.on_open
        
        self.ohlc = handleOHLC(self.interval)
        self.ws.run_forever()

    async def on_message(self, ws, message):
        message_bytes = base64.b64decode(message)
        self.yticker.ParseFromString(message_bytes)
        data = {
            "id": self.yticker.id,
            "exchange": self.yticker.exchange,
            "quoteType": self.yticker.quoteType,
            "price": self.yticker.price,
            "timestamp": self.yticker.time,
            "marketHours": self.yticker.marketHours,
            "changePercent": self.yticker.changePercent,
            "dayVolume": self.yticker.dayVolume,
            "change": self.yticker.change,
            "priceHint": self.yticker.priceHint
        }
        
        try:
            if self.createOHLC:
                data = await self.ohlc.create_tick(data)
                self.on_ticker(data)
            else:
                if self.on_ticker is None:
                    print(json.dumps(data))
                else:
                    self.on_ticker(ws, data)
        except KeyboardInterrupt:
            sys.exit()

    def close_socket(self):
        self.ws.close()

    async def on_error(self, ws, error):
        if self.on_custom_error is None:
            writeline(error)
        else:
            self.on_custom_error(error)

    async def on_close(self, ws):
        if self.on_custom_close is None:
            writeline('### connection closed ###')
        else:
            self.on_custom_close()
    
    async def on_open(self, ws):
        async def run(*args):
            self.ws.send(json.dumps(self.symbol_list))

        runAsync.runParallel(run)