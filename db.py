#!/usr/bin/python
# coding = utf-8

import sqlite3
import jsm
import datetime as dt
import pandas as pd
import pandas.io.sql as psql
import sys

class DB():
    def __init__(self, code):
        self.code = code

        dbname = "stock.db"
        self.connection = sqlite3.connect(dbname)
        self.cursor = self.connection.cursor()


    def write(self):
        check_table = 'select name from sqlite_master where type="table" and name="code_{code}"' # テーブルの存在確認
        cur = self.cursor.execute(check_table.format(code=self.code))

        if cur.fetchone(): # tableが存在する場合、最新の日付をreturn
            print('The table exists')
            select = 'select date from code_{code} order by date desc limit 1'.format(code=self.code)
            dtime = dt.datetime.strptime(self.cursor.execute(select).fetchone()[0], '%Y-%m-%d %H:%M:%S')
            return dt.date(dtime.year, dtime.month, dtime.day)

        else: # tableが存在しない場合、全株価取得してDBに書き込みし、文字列allをreturn
            print('The table does not exist')
            try:
                h_prices = jsm.Quotes().get_historical_prices(self.code, jsm.DAILY, all=True)
            except:
                print("データ取得失敗")
                h_prices = []

            create = "create table if not exists code_" + str(self.code) + "(date, open, high, low, close, volume)"
            self.cursor.execute(create)
            data = []
            for l in h_prices:
                data.append((l.date, l.open, l.high, l.low, l.close, l.volume))
            insert = 'insert into code_' + str(self.code) + '(date, open, high, low, close, volume) values (?,?,?,?,?,?)'
            try:
                self.cursor.executemany(insert, data)
                self.connection.commit()
            except:
                print('DB書き込みエラー')
            return 'all'


    def write_additional(self, start, end):
        h_prices = jsm.Quotes().get_historical_prices(self.code, jsm.DAILY, start_date = start, end_date = end)
        data = []
        for l in h_prices:
            data.append((l.date, l.open, l.high, l.low, l.close, l.volume))
        insert = 'insert into code_' + str(self.code) + '(date, open, high, low, close, volume) values (?,?,?,?,?,?)'
        try:
            self.cursor.executemany(insert, data)
            self.connection.commit()
        except:
            print('DB書き込みエラー')


    def read(self, start='', end=''):

        res = self.write() # DBに新規株価データの書き込み
        if not (res == 'all'):
            s = res + dt.timedelta(days=1)
            e = dt.date.today()
            if s < e:
                self.write_additional(s, e)

        if (not start) and (not end): # 読み込み範囲の選択がされなかった場合、全データ読み込み
            select = 'select * from code_{code} order by date'
            select = select.format(code=self.code)

        elif start and (not end): # 取得開始のみ指定
            d_to_s = '"{Y}-{m}-{d}"'
            s = d_to_s.format(Y=start[:4], m=start[4:6], d=start[6:])
            select = 'select * from code_{code} where date >= {start} order by date'
            select = select.format(code=self.code, start=s)

        elif (not start) and end: # 取得終了日のみ指定
            d_to_s = '"{Y}-{m}-{d}"'
            e = d_to_s.format(Y=end[:4], m=end[4:6], d=end[6:])
            select = 'select * from code_{code} where date <= {end} order by date'
            select = select.format(code=self.code, end=e)

        elif start and end: # 取得開始日と終了日を共に指定
            d_to_s = '"{Y}-{m}-{d}"'
            s = d_to_s.format(Y=start[:4], m=start[4:6], d=start[6:])
            e = d_to_s.format(Y=end[:4], m=end[4:6], d=end[6:])
            select = 'select * from code_{code} where date between {start} and {end}'
            select = select.format(code=self.code, start=s, end=e)

        else:
            print('想定外のエラー')

        df = psql.read_sql(select, self.connection) # pandasのDataFrameの形でデータを取り出す
        return df


if __name__ == '__main__':
    code = sys.argv[1]
    db = DB(code)

    start = '20160801'
    end = '20160831'
    res = db.read()
