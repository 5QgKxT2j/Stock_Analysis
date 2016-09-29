#!/usr/bin/python
# coding = utf-8

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

class Analysis:
    def __init__(self, df_prices, ndays):
        self.df_prices = df_prices
        self.ndays = ndays

    def _calc_MA(self):
        df = self.df_prices.set_index('date')
        return self.df_prices.close.rolling(center=False, window=self.ndays).mean()


    def calc_EM(self):
        pass


    def Dist_of_Diff_form_MA(self):
        ma_list = self._calc_MA()
#        df = self.df_prices.set_index('date')
        diff = (self.df_prices.close - ma_list) /  ma_list
        diff = diff.rename('diff_{0}ma'.format(self.ndays))
        return diff


    def seasonal_decompose(self,freq):
        df = self.df_prices.set_index('date')
        return seasonal_decompose(df.close,freq=freq)

if __name__ == '__main__':
    pass
