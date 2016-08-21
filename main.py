#!/usr/bin/python3.5
# coding = utf-8


### import formal library ###
import jsm
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas
import matplotlib.pyplot as plt

### import my library ###
from analysis import Analysis


def get_Histrical_Prices(code, start, end):
    return jsm.Quotes().get_historical_prices(code, jsm.DAILY, start_date = start, end_date = end)


def generate_MA_Graph(diff_list, ma_days):
    for i, d in enumerate(ma_days):
        plt.plot(diff_list[i], linewidth=2.5, linestyle='-', label='{0}MA'.format(d))
    plt.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':
    END_DATE = dt.date.today()
    START_DATE = END_DATE - relativedelta(months=24)
    CODE = 8591

#    today_price = jsm.Quotes().get_price(CODE)
#    print(today_price)
    hist_prices = get_Histrical_Prices(code = CODE, start=START_DATE, end=END_DATE)


    ma_days  = (25, 50, 75)
    diff_list = []
    for i in ma_days:
        ana = Analysis(h_prices=hist_prices, ndays=i)
        diff_list.append(ana.Dist_of_Diff_form_MA())

    generate_MA_Graph(diff_list, ma_days)

    ts = ana.seasonal_decompose(5)
    ts.plot()
    #plt.plot(ts.observed)
    #plt.plot(ts.trend)
    #plt.plot(ts.seasonal)
    #plt.plot(ts.resid)
    plt.show()

#    price, ma, diff = ana.calc_Diff_from_MA()
#    print('25days:  price: ' + str(price) + ' ma: ' + str(ma) + ' diff: ' + str(diff))
