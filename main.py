#!/usr/bin/python
# coding = utf-8


### import formal library ###
import jsm
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas

### import my library ###
from analysis import Analysis

def get_Histrical_Prices(code, start, end):
    return jsm.Quotes().get_historical_prices(code, jsm.DAILY, start_date = start, end_date = end)

if __name__ == '__main__':
    END_DATE = dt.date.today()
    START_DATE = END_DATE - relativedelta(months=5)
    CODE = 1417

    hist_prices = get_Histrical_Prices(code = CODE, start=START_DATE, end=END_DATE)
    ana = Analysis(h_prices=hist_prices)
    price, ma, diff = ana.calc_Diff_from_MA(ndays=25)
    print('price: ' + str(price) + ' ma: ' + str(ma) + ' diff: ' + str(diff))

