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

        dbname = "stock.sqlite3"
        self.connection = sqlite3.connect(dbname)
        self.cursor = self.connection.cursor()


    def write(self):
        check_table = 'select name from sqlite_master where type="table" and name="code_{code}"' # テーブルの存在確認
        cur = self.cursor.execute(check_table.format(code=self.code))

        if cur.fetchone(): # tableが存在する場合、差分をDBに書き込み
            print('The table code_{code} exists'.format(code=self.code))
            select = 'select date from code_{code} order by date desc limit 1'.format(code=self.code)
            dtime = dt.datetime.strptime(self.cursor.execute(select).fetchone()[0], '%Y-%m-%d %H:%M:%S')
            latest_day =  dt.date(dtime.year, dtime.month, dtime.day)
            s = latest_day + dt.timedelta(days=1)
            e = dt.date.today()
            if s < e:
                print('get additional jsm datas')
                self.write_additional(s, e)

        else: # tableが存在しない場合、全株価取得してDBに書き込み
            print('The table code_{code} does not exist'.format(code=self.code))
            h_prices = jsm.Quotes().get_historical_prices(self.code, jsm.DAILY, all=True)
            data = []
            for l in h_prices:
                data.append((l.date, l.open, l.high, l.low, l.close, l.volume))
            create = "create table if not exists code_" + str(self.code) + "(date, open, high, low, close, volume)"
            insert = 'insert into code_' + str(self.code) + '(date, open, high, low, close, volume) values (?,?,?,?,?,?)'
            try:
                self.cursor.execute(create)
                self.cursor.executemany(insert, data)
                self.connection.commit()
            except:
                print('DB書き込みエラー')


    def write_additional(self, start, end):
        try:
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

        except:
            print("New datas do not exist")


    def read(self, start='', end=''):

        res = self.write() # DBに新規株価データの書き込み

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
    con = sqlite3.connect('brand.sqlite3')
    cur = con.cursor()
    for ccode in cur.execute('select ccode from brand_list').fetchall():
        db = DB(*ccode)
        db.read()
