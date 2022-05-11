# %%
from functools import lru_cache
from typing import Dict, List
from sqlalchemy import create_engine

from constants import DBVariables
from exceptions import NoDataException

#%%
class tickDataHandler:
    def __init__(self):
        self.__engine = create_engine(f"postgresql://postgres:{DBVariables.password}@localhost/tickdata")

