#!/usr/bin/python
# coding = utf-8

MA_DAY = [25, 50, 75]

import sqlite3
import jsm
import datetime as dt
import pandas as pd
import pandas.io.sql as psql
import sys


class DB():
    def __init__(self, code):
        self.code = code
        self.tbname = 'code_{0}'.format(code)
        #dbname = './stock.sqlite3'
        dbname = './stock/code_{0}.sqlite3'.format(code)
        self.con = sqlite3.connect(dbname)
        self.cur = self.con.cursor()


    def write(self):

        # テーブルの存在確認をして処理を分岐
        check_table = 'select name from sqlite_master where type="table" and name="{0}"'.format(self.tbname)
        c = self.cur.execute(check_table)
        if c.fetchone(): # tableが存在する場合、差分をDBに書き込み
            print('{0}: The table found'.format(self.tbname))
            select = 'select date from {0} order by date desc limit 1'.format(self.tbname)
#            dtime = dt.datetime.strptime(self.cursor.execute(select).fetchone()[0], '%Y-%m-%d %H:%M:%S')
            dtime = dt.datetime.strptime(self.cur.execute(select).fetchone()[0], '%Y-%m-%d %H:%M:%S')
            latest_day =  dt.date(dtime.year, dtime.month, dtime.day)
            s = latest_day + dt.timedelta(days=1)
            e = dt.date.today()
            if s < e:
                print('{0}: Getting additional datas'.format(self.tbname))
                self._write_additional(s, e)

        else: # tableが存在しない場合、全株価取得してDBに書き込み
            print('{0}: No table found'.format(self.tbname))
            self._write_all()


    def _write_all(self):

        try:
            h_prices = jsm.Quotes().get_historical_prices(self.code, jsm.DAILY, all=True)
        except:
            print('Failed: {0}: Cannot get a stock data from server'.format(self.tbname))

        print('Success: {0}: Finish getting all data'.format(self.tbname))

        df = self._create_DF(h_prices)
        df = self._add_MA_row(df)

        try:
            df.to_sql(self.tbname, self.con, if_exists='replace')
        except:
            print('Failed: {0}: Writing to the Database'.format(self.tbname))
            sys.exit(-1)

        print('Success: {0}: Writing to the Database'.format(self.tbname))


    def _write_additional(self, start, end):

        try:
            h_prices = jsm.Quotes().get_historical_prices(self.code, jsm.DAILY, start_date = start, end_date = end)
        except:
            print('Failed: {0}: Cannot get additonal stock datas from server'.format(self.tbname))
            return None

        print('Success: {0}: Finish getting additional datas'.format(self.tbname))

        df = self._create_DF(h_prices)
        new_data_size = len(df)
        select = 'select distinct {rows} from {table} order by date desc limit {num}'.format(rows='date, open, high, low, close, volume', table=self.tbname, num=(max(MA_DAY)-1))
        data4ma = psql.read_sql(select, self.con)
        data4ma = data4ma.drop_duplicates(subset='date')
        data4ma = data4ma.sort_values('date')
        data4ma = data4ma.set_index('date')
        df = pd.concat([data4ma, df], axis=0)
        df = self._add_MA_row(df)
        df = df.iloc[len(df.index)-new_data_size:]
        try:
            df.to_sql(self.tbname, self.con, if_exists='append')
        except:
            print('Failed: {0}: Writing to the Database'.format(self.tbname))
            sys.exit(-1)

        print('Success: {0}: Writing to the Database'.format(self.tbname))

    def _create_DF(self, h_prices):

        data = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
        for l in h_prices:
            data['date'].append(l.date)
            data['open'].append(l.open)
            data['high'].append(l.high)
            data['low'].append(l.low)
            data['close'].append(l.close)
            data['volume'].append(l.volume)

        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset='date')
        df = df.sort_values('date')
        df = df.set_index('date')
        return df


    def _add_MA_row(self, df):

        ma_list = []
        diff_rate_list = []
        for d in MA_DAY:
            ma = df['close'].rolling(center=False, window=d).mean()
            ma.name = '{0}MA'.format(d)
            diff_rate = (df['close'] - ma) / ma
            diff_rate.name = 'Diff_from_{0}MA'.format(d)
            ma_list.append(ma)
            diff_rate_list.append(diff_rate)

        return pd.concat([df, *ma_list, *diff_rate_list], axis=1)

    def read(self, start='', end=''):

        res = self.write() # DBに新規株価データの書き込み

        if (not start) and (not end): # 読み込み範囲の選択がされなかった場合、全データ読み込み
            select = 'select distinct * from {0} order by date'.format(self.tbname)

        elif start and (not end): # 取得開始のみ指定
            d_to_s = '"{Y}-{m}-{d}"'
            s = d_to_s.format(Y=start[:4], m=start[4:6], d=start[6:])
            select = 'select distinct * from code_{code} where date >= {start} order by date'
            select = select.format(code=self.code, start=s)

        elif (not start) and end: # 取得終了日のみ指定
            d_to_s = '"{Y}-{m}-{d}"'
            e = d_to_s.format(Y=end[:4], m=end[4:6], d=end[6:])
            select = 'select distinct * from code_{code} where date <= {end} order by date'
            select = select.format(code=self.code, end=e)

        elif start and end: # 取得開始日と終了日を共に指定
            d_to_s = '"{Y}-{m}-{d}"'
            s = d_to_s.format(Y=start[:4], m=start[4:6], d=start[6:])
            e = d_to_s.format(Y=end[:4], m=end[4:6], d=end[6:])
            select = 'select distinct * from code_{code} where date between {start} and {end}'
            select = select.format(code=self.code, start=s, end=e)

        else:
            print('想定外のエラー')

        df = psql.read_sql(select, self.con) # pandasのDataFrameの形でデータを取り出す
        return df

if __name__ == '__main__':

    if sys.argv[1] == 'all':
        con = sqlite3.connect('brand.sqlite3')
        cur = con.cursor()
        for ccode in cur.execute('select ccode from brand_list').fetchall():
            db = DB(*ccode)
            db.write()
    else:
        db = DB(sys.argv[1])
        db.write()
#        print(db.read())
