#!/usr/bin/python
# coding = utf-8

import sqlite3
import jsm
import datetime as dt
import pandas as pd
import pandas.io.sql as psql

class DB():
    def __init__(self, code):
        self.code = code

        dbname = "stock.db"
        self.connection = sqlite3.connect(dbname)
        self.cursor = self.connection.cursor()


    def write(self, start, end):
        try:
            start = dt.datetime.strptime(start, '%Y%m%d')
            end = dt.datetime.strptime(end, '%Y%m%d')
            h_prices = jsm.Quotes().get_historical_prices(self.code, jsm.DAILY, start_date = start, end_date = end)
        except:
            print("データ取得失敗")
            h_prices = []

        create = "create table if not exists code_" + str(self.code) + "(date datetime unique, open, high, low, close, volume)"
        self.cursor.execute(create)


        data = []
        for l in h_prices:
            data.append((l.date, l.open, l.high, l.low, l.close, l.volume))

        insert = 'insert into code_' + str(self.code) + '(date, open, high, low, close, volume) values (?,?,?,?,?,?)'

        self.cursor.executemany(insert, data)
        self.connection.commit()

    def read(self, start='', end=''):
        if not start: # 読み込み範囲の選択がされなかった場合
            select = 'select * from code_{code} order by date'
            select = select.format(code=self.code)
        else:
            d_to_s = '"{Y}-{m}-{d}"'
            s = d_to_s.format(Y=start[:4], m=start[4:6], d=start[6:])
            e = d_to_s.format(Y=end[:4], m=end[4:6], d=end[6:])
            select = 'select * from code_{code} where date between {start} and {end}'
            select = select.format(code=self.code, start=s, end=e)

        df = psql.read_sql(select, self.connection) # pandasのDataFrameの形でデータを取り出す
        return df

if __name__ == '__main__':
    code = sys.argv[1]
    db = DB(code)

    start = '20160801'
    end = '20160831'
    db.write(start, end)
#    res = db.read(start, end)
    res = db.read()
    print(res)

