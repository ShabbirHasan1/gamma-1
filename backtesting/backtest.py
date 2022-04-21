'''
Ok so first I need a symbol on which this backtest should happen, if no symbol mentioned we can use a default one line
^NSEI. Next I need it's price data in user-defined interval, if not mentioned we can use a default one.

Then simply we calculate based on an abstract method which should return buy and sell signal with position size
as optional and based on those signals we can execute those trades with either user-defined trade commisions or nil. And
lastly we spit the returns
'''

from abc import ABCMeta, abstractmethod