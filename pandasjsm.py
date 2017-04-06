# jsm取得データをDataFrame形式で返す
# 取得データはキャッシュとしてデータベース(sqlite3)へ格納する

import sqlite3
import datetime as dt
import pandas as pd
import pandas.io.sql as psql
import sys
import jsm

# RangeType
DAILY = 0
WEEKLY = 1
MONTHLY = 2

class pandasjsm(jsm.Quotes):
    """株式情報取得"""

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
        p = super().get_historical_prices(ccode, range_type, start_date, end_date, all)
        return p

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
    print("get_price('9433')")
    print(pj.get_price('9433'))
    
    print("get_historical_prices('9433')")
    print(pj.get_historical_prices('9433'))
    