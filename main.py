#!/usr/bin/python
# coding = utf-8

### import formal library ###
import sys
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

### import my library ###
from analysis import Analysis
from db import DB

def generate_MA_Graph(diff_list, ma_days):
    for i, d in enumerate(ma_days):
        plt.plot(diff_list[i], linewidth=2.5, linestyle='-', label='{0}MA'.format(d))
    plt.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':

    params = sys.argv

    db = DB(params[1])
    db.write(params[2], params[3])

    df = db.read()
    print(df)
    ana = Analysis(df_prices=df, ndays=10)
    print(ana.Dist_of_Diff_form_MA())

#    ma_days  = (25, 50, 75)
#    diff_list = []
#    for i in ma_days:
#        ana = Analysis(df_prices=df_prices, ndays=i)
#        diff_list.append(ana.Dist_of_Diff_form_MA())
#
#    generate_MA_Graph(diff_list, ma_days)
#
#    ts = ana.seasonal_decompose(5)
#    ts.plot()
#    #plt.plot(ts.observed)
#    #plt.plot(ts.trend)
#    #plt.plot(ts.seasonal)
#    #plt.plot(ts.resid)
#    plt.show()

#    price, ma, diff = ana.calc_Diff_from_MA()
#    print('25days:  price: ' + str(price) + ' ma: ' + str(ma) + ' diff: ' + str(diff))
