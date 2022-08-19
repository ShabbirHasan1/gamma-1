#!/usr/bin/python3

import os
import sqlite3
import time
import logging

from json_handler import get_oi, get_OC_json

class dbHandler:
    def __init__(self):
        self._path = os.getcwd()
        self._db_name = 'multistrike_oi.db'
        if os.name == 'nt':
            os.system('cls')
            file_path = os.getcwd() + '\\' + self._db_name
        else:
            os.system('clear')
            file_path = os.getcwd() + '/' + self._db_name

        self._conn = sqlite3.connect(file_path)
        self._cur = self._conn.cursor()

    def checkDB(self):
        file_list = os.listdir(self._path)
        if self._db_name in file_list:
            logging.info("Database found")
            logging.info("Resetting table data")
            self.reset_table_data()
        else:
            logging.info("Database not found")
            logging.info(f"Creating a new database at: {self._path}")

            command = "create table oi(time, strike1, strike2, strike3, strike4, strike5, strike6)"
            self._cur.execute(command)

            returned = self._cur.execute("select * from oi")

            logging.info("Database refreshed")
            for item in returned:
                logging.info(item)

    def populate_db(self, index_name, expiry, contract1, contract2, contract3, contract4, contract5, contract6):
        self._cur.execute("insert into oi values (?, ?, ?, ?, ?, ?, ?)", (time.strftime('%H:%M'), get_oi(expiry, contract1), get_oi(expiry, contract2), get_oi(expiry, contract3), get_oi(expiry, contract4), get_oi(expiry, contract5), get_oi(expiry, contract6)))
        time.sleep(1)

        self._conn.commit()
        returned = self._cur.execute("select * from oi")

        for item in returned:
            logging.info(item)

        self._conn.close()

        get_OC_json(index_name)

    def fetch_data(self):
        returned = self._cur.execute("select * from oi")
        time_data, strike1_oi, strike2_oi, strike3_oi, strike4_oi, strike5_oi, strike6_oi = [], [], [], [], [], [], []

        for item in returned:
            time_data.append(item[0])
            strike1_oi.append(item[1])
            strike2_oi.append(item[2])
            strike3_oi.append(item[3])
            strike4_oi.append(item[4])
            strike5_oi.append(item[5])
            strike6_oi.append(item[6])
        
        return time_data, strike1_oi, strike2_oi, strike3_oi, strike4_oi, strike5_oi, strike6_oi

    def reset_table_data(self):
        self._cur.execute("delete from oi")
        self._conn.commit()

