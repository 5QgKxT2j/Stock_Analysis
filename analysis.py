#!/usr/bin/python
# coding = utf-8

import pandas as pd

class Analysis:
    def __init__(self, h_prices):
        d_data = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
        for l in h_prices:
            d_data['date'].append(l.date)
            d_data['open'].append(l.open)
            d_data['high'].append(l.high)
            d_data['low'].append(l.low)
            d_data['close'].append(l.close)
            d_data['volume'].append(l.volume)
        self.df_prices = pd.DataFrame(d_data)
#        print(self.df_prices)

    def calc_MA(self, ndays=25):
#        print(self.df_prices['close'].rolling(center=False, window=ndays).mean())
        return self.df_prices.ix[:,'close'].rolling(center=False, window=ndays).mean()

    def calc_EM(self):
        pass

    def calc_Diff_from_MA(self, ndays=25):
        latest_ma = self.calc_MA(ndays).ix[ndays-1]
        latest_price = self.df_prices.ix[0, 'close']
        diff_rate = (latest_price - latest_ma) / latest_ma
        return latest_price, latest_ma, diff_rate


if __name__ == '__main__':
    pass

