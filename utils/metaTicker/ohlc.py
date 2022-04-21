'''
Currently we are getting tick by tick data, we need to figure out a way to convert it into ohlc data based on the 
users interval.

df = df.assign(Timestamp = pd.to_datetime(df['Timestamp'],unit='s')).set_index('Timestamp')
df.resample('10min')['Price'].ohlc()

So what we have is, we create a df, with just price and timestamp and make timestamp the index then we create it the index.

Currently the toughest part is real time. Data will be coming in real time.

Ok so what we do is, we take data and put it in some kinda list then every second we create ohlc data from it by comparing the
last one, and at last we need a scheduler for every let say 15 say which closes the candle and starts a new one.

So now we would have one if else statement where if it's first time then simply put ohlc as price and if not, then compare and
replace the values to create one.

Hmm seems simple, now we somehow have to put that list of dictionary in a variable and also pop it once done.

A little change to the plan, instrad of doing this I created a class which is called every 15 or so seconds and handle the tick

Next we need to be able to handle user intervals, hmm that's kinda tricky since we also have to change the background scheduler.

First we need to figure how user should enter the interval, we have minutes, seconds and hours, I assume we can do string split.
but we can't have empty seperator. Instead we can use map, then convert to list. And if we have s - seconds, m - minutes, h - hours
'''


import time
import sys
import pandas as pd
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .defaults import INTERVAL

class handleOHLC:
    def __init__(self, interval):

        self._interval = interval
        self.handle_intervals()

        self._flag = True
        self._frontier = pd.Timestamp.now().floor(INTERVAL).to_pydatetime()
        self._cols = ['startTime', 'time', 'open', 'high', 'low', 'close', 'volume']
        self._data = pd.DataFrame(columns=self._cols)
        self._startScheduler()

    async def _process_tick(self) -> pd.DataFrame:
        _date_time = datetime.fromtimestamp(self._tick['timestamp']/1000)
        if self._flag == True and _date_time >= self._frontier:
            _start_time = pd.Timestamp.now().to_pydatetime()
            _time = time.time() * 1000
            _open = self._tick['price']
            _close = self._tick['price']
            _high = self._tick['price']
            _low = self._tick['price']
            _volume = self._tick['dayVolume']

            _row = {
                'startTime': _start_time,
                'time': _time,
                'open': _open,
                'high': _high,
                'low': _low,
                'close': _close,
                'volume': _volume
            }
            self._data = self._data.append(_row, True)
            self._flag = False
        else:
            if self._tick['price'] >= self._data['high'].iloc[-1]:
                self._data['high'].iloc[-1] = self._tick['price']
            elif self._tick['price'] <= self._data['low'].iloc[-1]:
                self._data['low'].iloc[-1] = self._tick['price']
            
            self._data['close'].iloc[-1] = self._tick['price']
            self._data['volume'].iloc[-1] += self._tick['dayVolume']

            return self._data

    def handle_intervals(self):
        intervals = list(map(str, self._interval))
        int_type = intervals[-1]
        self.timeinterval = int(intervals[0])

        self.second = False
        self.minute = False
        self.hour = False

        if int_type == 's':
            self.second = True
        elif int_type == 'm':
            self.minute = True
        elif int_type == 'h':
            self.hour = True


    async def create_tick(self, tick) -> pd.DataFrame:
        self._tick = tick
        try:
            data = await self._process_tick()
            time.sleep(0.001)
            return data
        except KeyboardInterrupt:
            self._scheduler.remove_job('onClose')
            self._scheduler.shutdown()

    def _on_close(self):
        self._flag = True
        self._frontier = pd.Timestamp.now().floor(INTERVAL).to_pydatetime()
    
    def _startScheduler(self):
        self._scheduler = BackgroundScheduler()
        self._scheduler.configure(timezone='utc')
        if self.second:
            self._scheduler.add_job(self._on_close, trigger='cron', second=self.timeinterval, id='onClose')
        elif self.minute:
            self._scheduler.add_job(self._on_close, trigger='cron', minute=self.timeinterval, id='onClose')
        elif self.hour:
            self._scheduler.add_job(self._on_close, trigger='cron', hour=self.timeinterval, id='onClose')
        else:
            sys.exit()
        self._scheduler.start()