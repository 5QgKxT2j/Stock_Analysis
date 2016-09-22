#!/usr/bin/python
# coding = utf-8

### import formal library ###
import sys
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from operator import itemgetter

### import my library ###
from analysis import Analysis
from db import DB
import model

def generate_MA_Graph(diff_list, ma_days):
    for i, d in enumerate(ma_days):
        plt.plot(diff_list[i], linewidth=2.5, linestyle='-', label='{0}MA'.format(d))
    plt.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':

    CODE = sys.argv[1]
    db = DB(CODE)
    stock_data = db.read()


    res = []
    l_diff_th = [-0.20, -0.15, -0.10]
    l_inc_th = [1.1, 1.2]
    l_dline = [20, 30]
    l_ma_day = [25, 50, 75]

    m = model.simple_model1(stock_data, ma_days=l_ma_day)
    for diff_th, inc_th, dline, ma_day in itertools.product(l_diff_th, l_inc_th, l_dline, l_ma_day):
#        print('diff_th:', diff_th, 'inc_th:', inc_th, 'dline:', dline, 'ma_day:', ma_day)
        r = m.fit(diff_th=diff_th, inc_th=inc_th, dline=dline, ma_day=ma_day)
        if r[0] > 0.50:
            params = diff_th, inc_th, dline, ma_day
            mes = '{ma_day}日MAから{diff_th}%乖離しているとき、{dline}日以内に株価が{inc_th}倍以上になる確率: {c_rate}(correct: {cor}, wrong: {wr})'.format(ma_day=ma_day, diff_th=diff_th, dline=dline, inc_th=inc_th, c_rate=r[0], cor=r[1], wr=r[2])
            res.append(mes)
    m.show()

    for e in res:
        print(e)
#    ts = ana.seasonal_decompose(5)
#    ts.plot()
#    #plt.plot(ts.observed)
#    #plt.plot(ts.trend)
#    #plt.plot(ts.seasonal)
#    #plt.plot(ts.resid)
#    plt.show()

