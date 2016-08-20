#!/usr/bin/python3.5
# coding = utf-8

import pandas as pd

class Analysis:
    def __init__(self, h_prices, ndays):
        d_data = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
        for l in h_prices:
            d_data['date'].append(l.date)
            d_data['open'].append(l.open)
            d_data['high'].append(l.high)
            d_data['low'].append(l.low)
            d_data['close'].append(l.close)
            d_data['volume'].append(l.volume)
        self.df_prices = pd.DataFrame(d_data)
        self.ndays = ndays

    def calc_MA(self):
        return self.df_prices.ix[:,'close'].rolling(center=False, window=self.ndays).mean().dropna().reset_index(drop = True) #Nanを除外して0から再index

    def calc_EM(self):
        pass

    def calc_Diff_from_MA(self):
        latest_ma = self.calc_MA().ix[0]
        latest_price = self.df_prices.ix[0, 'close']
        diff_rate = (latest_price - latest_ma) / latest_ma
        return latest_price, latest_ma, diff_rate

    def Dist_of_Diff_form_MA(self):
        ma_list = self.calc_MA()
        diff_rate_list = (self.df_prices.ix[:, 'close'] - ma_list[:]) /  ma_list[:]
        return diff_rate_list

if __name__ == '__main__':
    pass

