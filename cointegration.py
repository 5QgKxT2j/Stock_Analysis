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
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import subprocess
import talib
import numpy as np

SLEEP_SEC = 2

def predict_based_on_coint(code, cls_code, now):
    pj = pandasjsm()
    target_code = []

    start_date = now - relativedelta(years=1)

    ### ADF unit root test begins
    for c in code:
        df = pj.get_historical_prices(c, start_date = start_date.date())
        # get rid of stocks, which only have low volume.
        if df.tail(1)['volume'][0] < 100000:
            continue

        # make sure that there is a unit root.
        if stattools.adfuller(df['adj_close'], regression='ct')[1] > 0.05:
            target_code.append(c)

        time.sleep(SLEEP_SEC)
    print('class_code={0}: Now target_list is available'.format(cls_code))
    ### ADF unit root test ends

    ### cointegration test begins
    for c1, c2 in list(itertools.combinations(target_code, 2)):
        db = DB(c1)
        df1 = db.select(table='code_{0}_0'.format(c1), start=start_date.strftime("%Y-%m-%d %H:%M:%S"))
        db = DB(c2)
        df2 = db.select(table='code_{0}_0'.format(c2), start=start_date.strftime("%Y-%m-%d %H:%M:%S"))

        if len(df1['adj_close']) != len(df2['adj_close']):
            continue

        coint = stattools.coint(df1['adj_close'], df2['adj_close'], trend='ct')
        if coint[1] < 0.01:
            model = VECM(pd.concat([df1['adj_close'], df2['adj_close']], axis=1),
                             deterministic="ci", coint_rank=1)
            vecm_res = model.fit()
            beta1, beta2 = vecm_res.beta
            coint_series = beta1 * df1['adj_close'] + beta2 * df2['adj_close'] + vecm_res.const_coint[0][0]

            ### make sure that the generated cointegration series do "not" have a unit root.
            if stattools.adfuller(coint_series, regression='ct')[1] < 0.01:
                c1_latest = df1.tail(1).iloc[0]['adj_close']
                c2_latest = df2.tail(1).iloc[0]['adj_close']

                forecast, lower, upper = vecm_res.predict(steps=30, alpha=0.05)
                max_profit = 0
                close_day = 0
                for day, fc in enumerate(forecast):
                    profit = (beta1 * (fc[0] - c1_latest)) + (beta2 * (fc[1] - c2_latest))
                    if profit > max_profit:
                        max_profit = profit
                        close_day = day

                profit_rate = max_profit / ( beta1 * c1_latest - beta2 * c2_latest)
                if profit_rate <= 0.01:
                    continue

                with open('./coint_log/{0}_coint.txt'.format(now.strftime("%Y%m%d_%H%M")), 'a') as log:
                    print('code, coint:', [c1, c2, coint[1]], '\n',
                          forecast, '\n'
                          'Latest Price:', [df1.tail(1).iloc[0]['adj_close'], df2.tail(1).iloc[0]['adj_close']], '\n'
                          'VECM Beta:', beta1, beta2 , '\n'
                          'Expected Profit:', max_profit, profit_rate, '\n'
                          'Close: in', close_day+1, 'steps\n' , file=log)


                # make a graph for a forecast and a cointegration series
                vecm_res.plot_forecast(steps=30, n_last_obs=30)
                plt.savefig("./figure/coint/{0}/forecast_{1}-{2}.png".format(now.strftime("%Y%m%d_%H%M"), c1, c2))
                plt.close()

                bupper, bmiddle, blower = talib.BBANDS(np.array(coint_series, dtype='f8'), timeperiod=25)
                coint_series_res = pd.concat([pd.DataFrame(bupper), coint_series, pd.DataFrame(blower)], axis=1)
                coint_series_res.plot()
                plt.savefig("./figure/coint/{0}/coint_series_{1}-{2}.png".format(now.strftime("%Y%m%d_%H%M"), c1, c2))
                plt.close()


    ### cointegration test ends


if __name__ == '__main__':
    connect = sqlite3.connect('brand.sqlite3')
    cursor = connect.cursor()
    select = 'select * from brand_list where market is "東証1部"'
    brand = pd.io.sql.read_sql(select, connect)
    cls_code = sorted(set(brand['class_code']), key=itemgetter(0))

    now = datetime.datetime.now()
    subprocess.call( ['mkdir', '-p', './figure/coint/{0}'.format(now.strftime("%Y%m%d_%H%M")) ])
    threads = []
    for cc in cls_code:
        th = threading.Thread(target=predict_based_on_coint, name='th', args=(brand[brand['class_code'] == cc]['ccode'], cc, now))
        threads.append(th)
        th.start()


    for t in threads:
        t.join()

