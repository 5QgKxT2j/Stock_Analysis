#!/usr/bin/python
# coding = utf-8

import warnings
warnings.filterwarnings('ignore', category=FutureWarning, message=r'The pandas.core.datetools')
warnings.filterwarnings('ignore', category=UserWarning, message=r'No parser')

from pandasjsm import pandasjsm
from analyzer import analyzer
from statsmodels.tsa.vector_ar.vecm import VECM
from statsmodels.tsa import stattools
import datetime
import pprint
import itertools
import pandas as pd
import threading
import sys
import sqlite3
from operator import itemgetter
import time
from database import DB

SLEEP_SEC = 10

def predict_based_on_coint(code, cls_code):
    pj = pandasjsm()
    target_code = []
    for c in code:
        df = pj.get_historical_prices(c, start_date = datetime.date(2016,1,1))
        # get rid of stocks, which only have low volume.
        if df.tail(1)['volume'][0] < 100000:
            continue

        # make sure that there is a unit root.
        if stattools.adfuller(df['adj_close'], regression='ct')[1] > 0.05:
            target_code.append(c)

        time.sleep(SLEEP_SEC)

    print('class_code={0}: Now target_list is available'.format(cls_code))

    for c1, c2 in list(itertools.combinations(target_code, 2)):
        db = DB(c1)
        df1 = db.select(table='code_{0}_0'.format(c1), start='2016-01-01 00:00:00')
        db = DB(c2)
        df2 = db.select(table='code_{0}_0'.format(c2), start='2016-01-01 00:00:00')

        if len(df1['adj_close']) != len(df2['adj_close']):
            continue
        coint = stattools.coint(df1['adj_close'], df2['adj_close'], trend='ct')

#        if coint[1] < 0.05:
        if coint[1] < 0.30:

            model = VECM(pd.concat([df1['adj_close'], df2['adj_close']], axis=1),
                             deterministic="ci", seasons=4, coint_rank=1)
            vecm_res = model.fit()

            c1_latest = df1.tail(1).iloc[0]['adj_close']
            c2_latest = df2.tail(1).iloc[0]['adj_close']
            if (vecm_res.predict(steps=1)[0][0] - c1_latest) - (vecm_res.predict(steps=1)[0][1] - c2_latest) > 0:
                max_profit = 0
                close_day = 0
                for day, predict in enumerate(vecm_res.predict(steps=5)):
                    profit = (vecm_res.beta[0] * (predict[0] - c1_latest)) + (vecm_res.beta[1] * (predict[1] - c2_latest))
                    if profit > max_profit:
                        max_profit = profit
                        close_day = day

                with open('/tmp/coint.txt', 'a') as log:
                    print('code, coint:', [c1, c2, coint[1]], '\n',
                           vecm_res.predict(steps=5), '\n'
                          'Latest Price:', [df1.tail(1).iloc[0]['adj_close'], df2.tail(1).iloc[0]['adj_close']], '\n'
                          'VECM Beta:', vecm_res.beta[0], vecm_res.beta[1] , '\n'
                          'Expected Profit:', max_profit, '\n'
                          'Close: in', close_day+1, 'days\n' , file=log)


connect = sqlite3.connect('brand.sqlite3')
cursor = connect.cursor()
select = 'select * from brand_list where market is "東証1部"'
brand = pd.io.sql.read_sql(select, connect)
cls_code = sorted(set(brand['class_code']), key=itemgetter(0))

threads = []
for cc in cls_code:
    th = threading.Thread(target=predict_based_on_coint, name='th', args=(brand[brand['class_code'] == cc]['ccode'], cc))
    threads.append(th)
    th.start()
    time.sleep(SLEEP_SEC)

for t in threads:
    t.join()

