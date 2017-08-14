#!/usr/bin/python
# coding = utf-8

import warnings
warnings.filterwarnings('ignore', category=FutureWarning, message=r'The pandas.core.datetools')

import pandas as pd
from statsmodels.tsa import stattools
import pprint
from pandasjsm import pandasjsm
import datetime
import copy
import matplotlib.pyplot as plt

wdir = './hist_index/'

code_list = (8704,3758,3810,6181,3793,8925,3667,5704,3688,3185,3935,7577,3542,5817,3788,6084,3264,6239,4772,2397,9421,4728,2656,3672,4585)

pj = pandasjsm()

mprice = []
for market in ['tosho1', 'tosho2', 'mothers', 'jasdac']:
    with open(wdir+ market + '.csv') as f:
        market_price = pd.read_csv(f, parse_dates=[0], names=['date', 'open', 'high', 'low', 'close'], header=None, index_col=0)
        market_price.sort_index(inplace=True)
        market_price = market_price['close'].pct_change()
        market_price.rename(market, inplace=True)
        mprice.append(market_price.dropna())

df = pd.concat([mp for mp in mprice], axis=1)
#print(df.corr())

for i in ['tosho1', 'tosho2', 'mothers', 'jasdac']:
    for j in code_list:

        obj = pj.get_historical_prices(j, start_date = datetime.date(2016,8,1))['adj_close']
        obj.rename(j, inplace=True)
        sub = copy.deepcopy(df[i])

        obj.index = range(len(obj))
        sub.index = range(len(sub))
        for day in range(1, 30):
            sub.index += day
            data = pd.concat([obj, sub], axis=1)
            corr = data.corr()
            sub.index -= day

            if (corr.ix[i, j] > 0.5) or (corr.ix[i, j] < -0.5):
                print('delta', day, '\n', data.corr())

#for code in code_list:
#    df = pj.get_historical_prices(code, start_date = datetime.date(2016,1,1))
#    df = df.pct_change()
#    df.index += datetime.timedelta(days=1)
#    df = pd.concat([market_price['close'], df['adj_close']], axis=1).dropna()
# 
#    cor = df.corr()
#    if cor.ix['adj_close', 'close'] > 0.5:
#        print('###', code, '###')
#        print(cor)

