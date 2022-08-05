import csv
import requests
from typing import List, Dict
from os import remove

from constants import NSEScripsURL

class Symbols:
    def __init__(self, type: str):
        """Get symbols for the scrips in an indice or sector.

        Args:
            type (str): Mention the type i.e. the indice or sector

        Returns:
            List: Returns the list containing the symbols.
        """
        self._type = type

    def _downloadCSV(self, link: str):
        resp = requests.get(link)
        self._filename: str = self._type + '.csv'
        open(self._filename, "wb").write(resp.content)

    def _parseCSV(self) -> List:
        symbols: List = []
        with open(self._filename) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            line = 0
            for row in reader:
                if line == 0:
                    line += 1
                else:
                    symbols.append(row[2])
        remove(self._filename)
        return symbols

    def getSymbols(self) -> List:
        symbols: List = []

        switcher: Dict = {
            "AUTO": NSEScripsURL.auto,
            "BANK": NSEScripsURL.bank,
            "FINSERV": NSEScripsURL.finserv,
            "FINSERV50": NSEScripsURL.finserv50,
            "CONSDU": NSEScripsURL.consdu,
            "FMCG": NSEScripsURL.fmcg,
            "HEALTH": NSEScripsURL.health,
            "IT": NSEScripsURL.it,
            "MEDIA": NSEScripsURL.media,
            "METAL": NSEScripsURL.metal,
            "OIL": NSEScripsURL.oil,
            "PHARMA": NSEScripsURL.pharma,
            "PRIVATE": NSEScripsURL.privatebank,
            "PSU": NSEScripsURL.psu,
            "REALTY": NSEScripsURL.realty
        }

        url: str = switcher.get(self._type, "[!] Undefined type")       
        self._downloadCSV(url)
        symbols: List = self._parseCSV()

        return symbols