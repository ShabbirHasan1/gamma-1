from collections import OrderedDict

class FixedDict(OrderedDict):
    def __init__(self, *args, maxlen: int=0, **kwargs):
        self.__maxlen = maxlen
        super().__init__(*args, **kwargs)
    
    def __setitem__(self, key, value) -> None:
        OrderedDict.__setitem__(self, key, value)
        if self.__maxlen > 0:
            if len(self) > self.__maxlen:
                self.popitem(False)