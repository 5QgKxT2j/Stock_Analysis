#!/usr/bin/python
# coding = utf-8

from pandasjsm import pandasjsm
import datetime
import pandas as pd

#codes = {3810, 8704,3758, 6181, 8925, 3793, 4728, 3667, 6619}

with open('./brandlist.txt') as bl:
    codes = bl.readlines()

pj = pandasjsm()
#index_code = 998405
index_code = 998407
topix = pj.get_historical_prices(index_code, start_date = datetime.date(2016,1,1))
topix = topix.diff(1)
topix = topix.shift(1)


for code in codes:
    try:
        df = pj.get_historical_prices(code.rstrip('\n'), start_date = datetime.date(2016,1,1))
        df = df.diff(1)
        df = pd.concat([topix['adj_close'], df['adj_close']], axis=1)
        with open('./topix_result.txt', 'a') as tr:
            print(code.rstrip('\n'), df.corr().ix[1, 0], file=tr)
    except Exception as e:
        print(e)
