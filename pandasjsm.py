# jsm取得データをDataFrame形式で返す
# 取得データはキャッシュとしてデータベース(sqlite3)へ格納する

import sqlite3
import datetime
import time
import pandas as pd
import pandas.io.sql as psql
import jsm

class pandasjsm(jsm.Quotes):
    """株式情報取得"""

    # RangeType
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2

    def __init__(self, path='./database/'):
        self.path = path 

    def get_price(self, ccode):
        """現在の株価を取得
        ccode: 証券コード
        """
        p = super().get_price(ccode)
        return p

    def get_historical_prices(self, ccode, range_type=DAILY, start_date=None, end_date=None, all=False):
        """過去の株価情報を取得
        ccode: 証券コード
        range_type: 取得タイプ(RANGE_DAILY, RANGE_WEEKLY, RANGE_MONTHLY)
        start_date: 取得開始日時(default: end_dateから1ヶ月前)
        end_date: 取得終了日時(default: 今日)
        all: Trueなら全データ取得
        """

        # dbアクセス準備
        dbpath = self.path + 'code_{ccode}.sqlite3'.format(ccode=ccode)
        connect = sqlite3.connect(dbpath)
        cursor = connect.cursor()

        # キャッシュデータ範囲検証
        table_name = 'code_{ccode}_{range_type}'.format(ccode=ccode, range_type=range_type)
        print('table_name={table_name}'.format(table_name=table_name))

        start_date_sql = 'select date from {table_name} order by date limit 1'.format(table_name=table_name)
        end_date_sql = 'select date from {table_name} order by date desc limit 1'.format(table_name=table_name)

        try:
            db_start_date = psql.read_sql(start_date_sql, connect).iloc[0, 0]
            db_start_date = datetime.datetime.strptime(db_start_date, '%Y-%m-%d %H:%M:%S')
            db_start_date = datetime.date(db_start_date.year, db_start_date.month, db_start_date.day)
            db_end_date = psql.read_sql(end_date_sql, connect).iloc[0, 0]
            db_end_date = datetime.datetime.strptime(db_end_date, '%Y-%m-%d %H:%M:%S')
            db_end_date = datetime.date(db_end_date.year, db_end_date.month, db_end_date.day)
        except Exception as e:
            print(e)
            db_start_date = None
            db_end_date = None
        
        #print('db_start_date = {db_start_date}'.format(db_start_date = db_start_date))
        #print('db_end_date = {db_end_date}'.format(db_end_date = db_end_date))
        

        # 要求データ範囲検証
        if all:
            jsm_start_date = datetime.date(2000, 1, 1)
            jsm_end_date = datetime.date.today()
        else:
            if not end_date:
                jsm_end_date = datetime.date.today()
            else:
                jsm_end_date = end_date
            if not start_date:
                jsm_start_date = datetime.date.fromtimestamp(time.mktime(jsm_end_date.timetuple()) - 2592000)
            else:
                jsm_start_date = start_date

        # エラー処理？？


        # 必要データ取得 & データベース書き込み
        if not db_start_date and not db_end_date:
            data = super().get_historical_prices(ccode, range_type, jsm_start_date, jsm_end_date)
            self.__insert_pricedata(data, table_name, connect)
        else:
            if jsm_start_date < db_start_date:
                try:
                    data = super().get_historical_prices(ccode, range_type, jsm_start_date, db_start_date - datetime.timedelta(1))
                    self.__insert_pricedata(data, table_name, connect)
                except:
                    data = None
            if jsm_end_date > db_end_date:
                try:
                    #data = super().get_historical_prices(ccode, range_type, db_end_date + datetime.timedelta(1), jsm_end_date)
                    data = super().get_historical_prices(ccode, range_type, db_end_date, jsm_end_date)
                    self.__insert_pricedata(data, table_name, connect)
                except:
                    data = None

        # データベース読み込み
        start = jsm_start_date - datetime.timedelta(1)
        end = jsm_end_date + datetime.timedelta(1)
        read_sql = "select * from {table_name} where date between '{start}' and '{end}'".format(table_name = table_name, start = start.strftime('%Y-%m-%d'), end = end.strftime('%Y-%m-%d'))
        
        df = psql.read_sql(read_sql, connect)
        df = df.set_index('date')
        return df

    def __insert_pricedata(self, data, table_name, connect):
        #create if not exists
        create_sql = 'create table if not exists {table_name}(date unique, open, high, low, close, adj_close)'.format(table_name=table_name)
        connect.execute(create_sql)
        #insert each data
        for dat in data:
            insert_sql = 'insert into {table_name} values (?,?,?,?,?,?)'.format(table_name=table_name)
            record = (dat.date, dat.open, dat.high, dat.low, dat.close, dat._adj_close)
            try:
                connect.execute(insert_sql, record)
            except Exception as e:
                print('insert error: {e}'.format(e=e))
                
        connect.commit()
        return

    def get_finance(self, ccode):
        """財務データを取得
        market_cap        # 時価総額
        shares_issued     # 発行済株式数
        dividend_yield    # 配当利回り
        dividend_one      # 1株配当
        per               # 株価収益率
        pbr               # 純資産倍率
        eps               # 1株利益
        bps               # 1株純資産
        price_min         # 最低購入代金
        round_lot         # 単元株数
        years_high        # 年初来高値
        years_low         # 年初来安値
        """
        f = super().get_finance(ccode)
        return f
        
    def get_brand(self, brand_id=None):
        """業種別銘柄リストを取得
        ccode     # 証券コード
        market    # 市場
        name      # 銘柄名
        info      # 銘柄情報

        brand_id: 業種種類
        '0050': 農林・水産業
        '1050': 鉱業
        '2050': 建設業
        '3050': 食料品
        '3100': 繊維製品
        '3150': パルプ・紙
        '3200': 化学
        '3250': 医薬品
        '3300': 石油・石炭製品
        '3350': ゴム製品
        '3400': ガラス・土石製品
        '3450': 鉄鋼
        '3500': 非鉄金属
        '3550': 金属製品
        '3600': 機械
        '3650': 電気機器
        '3700': 輸送機器
        '3750': 精密機器
        '3800': その他製品
        '4050': 電気・ガス業
        '5050': 陸運業
        '5100': 海運業
        '5150': 空運業
        '5200': 倉庫・運輸関連業
        '5250': 情報・通信
        '6050': 卸売業
        '6100': 小売業
        '7050': 銀行業
        '7100': 証券業
        '7150': 保険業
        '7200': その他金融業
        '8050': 不動産業
        '9050': サービス業
        None: 全業種
        """
        b = super().get_brand(brand_id)
        return b
    
    def search(self, terms):
        """銘柄検索
        terms: キーワード
        """
        s = super().search(terms)
        return s

if __name__ == '__main__':
    pj = pandasjsm()
    #print("get_price('9433')")
    #print(pj.get_price('9433'))

    #print("get_historical_prices('1301')", pj.DAILY, datetime.date(2016,1,4),datetime.date(2016,12,30))
    #print(pj.get_historical_prices('1301', pj.DAILY, datetime.date(2016,1,4), datetime.date(2016,12,30)))
 
    #print("get_finance('9433')")
    #print(pj.get_finance('9433'))   
    
    #print("get_brand('5250')")
    #print(pj.get_brand('5250'))

    pass