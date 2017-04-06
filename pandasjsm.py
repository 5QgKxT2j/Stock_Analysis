# jsm取得データをDataFrame形式で呼び出す
# 取得データはキャッシュとしてデータベース(sqlite3)へ格納する

import sqlite3
import datetime as dt
import pandas as pd
import pandas.io.sql as psql
import sys
import jsm

class pandasjsm():
    def __init__(self):
        self.name = "kkk"

    def get_price(self, code):
        return

    def get_historical_prices(self, code, freq, start_date, end_date, all=False):
        print(code)
        return

    def __convert_freq(freq):
        if freq == 'DAILY':
            return jsm.DAILY
        elif freq == 'WEEKLY':
            return jsm.WEEKLY
        elif freq == 'MONTHLY':
            return jsm.WEEKLY
        else:
            raise 'IllegalExpression'

    def get_inance(self, cdode):
        return


if __name__ == '__main__':
    pj = pandasjsm()
    pj.get_historical_prices('9433')

    