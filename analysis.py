#!/usr/bin/python
# coding = utf-8

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

class Analysis:
    def __init__(self, df_prices, ndays):
        self.df_prices = df_prices
        self.ndays = ndays

    def calc_MA(self):
        df = self.df_prices.set_index('date')
        return df.close.rolling(center=False, window=self.ndays).mean()


    def calc_EM(self):
        pass


    def Dist_of_Diff_form_MA(self):
        ma_list = self.calc_MA()
        df = self.df_prices.set_index('date')
        diff_rate_list = (df.close - ma_list) /  ma_list
#        print(diff_rate_list)
        return diff_rate_list


    def seasonal_decompose(self,freq):
        df = self.df_prices.set_index('date')
        return seasonal_decompose(df.close,freq=freq)

if __name__ == '__main__':
    pass
