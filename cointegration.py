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
PROCESS = 4


def get_Unit_Root_Code_List(code, start_date, end_date='', alpha=0.05):
    pj = pandasjsm()
    unit_root_code = []
    for c in code:
        if end_date:
            df = pj.get_historical_prices(c, start_date = start_date.date(), end_date=end_date.date())
        else:
            df = pj.get_historical_prices(c, start_date = start_date.date())
        if stattools.adfuller(df['adj_close'], regression='ct')[1] > alpha:
            unit_root_code.append(c)
        time.sleep(SLEEP_SEC)
    return unit_root_code

def get_Coint_Relation_List(unit_root_code, start_date, end_date='', alpha=0.05):
    coint_series_res = [] # list of (code1, code2, beta1, beta2, coint_const, coint_series)
    for c1, c2 in list(itertools.combinations(unit_root_code, 2)):
        db1 = DB(c1)
        db2 = DB(c2)
        if end_date:
            df1 = db1.select(table='code_{0}_0'.format(c1), start=start_date.strftime("%Y-%m-%d %H:%M:%S"), end=end_date.strftime("%Y-%m-%d %H:%M:%S"))
            df2 = db2.select(table='code_{0}_0'.format(c2), start=start_date.strftime("%Y-%m-%d %H:%M:%S"), end=end_date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            df1 = db1.select(table='code_{0}_0'.format(c1), start=start_date.strftime("%Y-%m-%d %H:%M:%S"))
            df2 = db2.select(table='code_{0}_0'.format(c2), start=start_date.strftime("%Y-%m-%d %H:%M:%S"))

            # skip stock, which don't have enough historical dates.
        if len(df1['adj_close']) != len(df2['adj_close']):
            continue

        coint = stattools.coint(df1['adj_close'], df2['adj_close'], trend='ct')
        if coint[1] < alpha:
            model = VECM(pd.concat([df1['adj_close'], df2['adj_close']], axis=1),
                             deterministic="ci", coint_rank=1)
            vecm_res = model.fit()
            beta1, beta2 = vecm_res.beta
            coint_const = vecm_res.const_coint[0][0]
            coint_series = beta1 * df1['adj_close'] + beta2 * df2['adj_close'] + coint_const
            if stattools.adfuller(coint_series, regression='ct')[1] < alpha:
                coint_series_res.append({'c1':c1, 'c2':c2, 'beta1':beta1, 'beta2':beta2,
                                     'coint_const':coint_const, 'coint_series':coint_series})
    return coint_series_res

def predict_based_on_coint(code, cls_code, now):
    start_date = now - relativedelta(years=1)
    unit_root_code = get_Unit_Root_Code_List(code, start_date)
    print('{0}: Unit Root Test finished.'.format(cls_code))
    coint_series_res = get_Coint_Relation_List(unit_root_code, start_date)
    print('{0}: Cointegration Series available.'.format(cls_code))

    for cs in coint_series_res:
        bupper, bmiddle, blower = talib.BBANDS(np.array(cs['coint_series'], dtype='f8'), timeperiod=25)
        coint_series_res = pd.concat([pd.DataFrame(bupper), cs['coint_series'], pd.DataFrame(blower)], axis=1)
        coint_series_res.plot()
        plt.savefig("./figure/coint/{0}/coint_series_{1}-{2}.png".format(now.strftime("%Y%m%d_%H%M"), cs['c1'], cs['c2']))
        plt.close()

    print('{0}: Prediction based on cointegration ends.'.format(cls_code))


def backtest(code, cls_code, now):
    start_date = now - relativedelta(years=0, days=180)
    backtest_start_date = now - relativedelta(days=30)
    end_date = backtest_start_date - relativedelta(days=1)

    unit_root_code = get_Unit_Root_Code_List(code, start_date, end_date)
    print('{0}: Unit Root Test finished.'.format(cls_code))
    coint_series_res = get_Coint_Relation_List(unit_root_code, start_date, end_date)
    print('{0}: Cointegration Series available.'.format(cls_code))

    for cs in coint_series_res:
        bupper, bmiddle, blower = talib.BBANDS(np.array(cs['coint_series'], dtype='f8'), timeperiod=25)
#        coint_series_res = pd.concat([pd.DataFrame(bupper), cs['coint_series'], pd.DataFrame(blower)], axis=1)
#        coint_series_res.plot()
        db1 = DB(cs['c1'])
        db2 = DB(cs['c2'])
        df1 = db1.select(table='code_{0}_0'.format(cs['c1']), start=backtest_start_date.strftime("%Y-%m-%d %H:%M:%S"))
        df2 = db2.select(table='code_{0}_0'.format(cs['c2']), start=backtest_start_date.strftime("%Y-%m-%d %H:%M:%S"))

        backtest_last = len(coint_series_res)
        coint_series_future = cs['beta1'] * df1['adj_close'] + cs['beta2'] * df2['adj_close'] + cs['coint_const']
        coint_series_res = pd.concat([cs['coint_series'], coint_series_future], axis=0, ignore_index=True)
        coint_series_res = pd.concat([pd.DataFrame(bupper), coint_series_res, pd.DataFrame(blower)], axis=1)
        coint_series_res.plot()

        plt.savefig("./figure/coint/{0}/coint_series_{1}-{2}.png".format(now.strftime("%Y%m%d_%H%M"), cs['c1'], cs['c2']))
        plt.close()



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
#        th = threading.Thread(target=predict_based_on_coint, name='th', args=(brand[brand['class_code'] == cc]['ccode'], cc, now))
        th = threading.Thread(target=backtest, name='th', args=(brand[brand['class_code'] == cc]['ccode'], cc, now))
        threads.append(th)
        th.start()

    for t in threads:
        t.join()



############old code ############
##                forecast, lower, upper = vecm_res.predict(steps=30, alpha=0.05)
##                max_profit = 0
##                close_day = 0
##                for day, fc in enumerate(forecast):
##                    profit = (beta1 * (fc[0] - c1_latest)) + (beta2 * (fc[1] - c2_latest))
##                    if profit > max_profit:
##                        max_profit = profit
##                        close_day = day
##
##                with open('./coint_log/{0}_coint.txt'.format(now.strftime("%Y%m%d_%H%M")), 'a') as log:
##                    print('code, coint:', [c1, c2, coint[1]], '\n',
##                          forecast, '\n'
##                          'Latest Price:', [df1.tail(1).iloc[0]['adj_close'], df2.tail(1).iloc[0]['adj_close']], '\n'
##                          'VECM Beta:', beta1, beta2 , '\n'
##                          'Expected Profit:', max_profit, profit_rate, '\n'
##                          'Close: in', close_day+1, 'steps\n' , file=log)
##
##
##                # make a graph for a forecast and a cointegration series
##                vecm_res.plot_forecast(steps=30, n_last_obs=30)
##                plt.savefig("./figure/coint/{0}/forecast_{1}-{2}.png".format(now.strftime("%Y%m%d_%H%M"), c1, c2))
##                plt.close()
##
##                bupper, bmiddle, blower = talib.BBANDS(np.array(coint_series, dtype='f8'), timeperiod=25)
##                coint_series_res = pd.concat([pd.DataFrame(bupper), coint_series, pd.DataFrame(blower)], axis=1)
##                coint_series_res.plot()
##                plt.savefig("./figure/coint/{0}/coint_series_{1}-{2}.png".format(now.strftime("%Y%m%d_%H%M"), c1, c2))
##                plt.close()
