#!/usr/bin/python
# coding = utf-8

import pandas as pd

class Analysis:
    def __init__(self, h_prices):
        _d_data = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
        for l in h_prices:
            _d_data['date'].append(l.date)
            _d_data['open'].append(l.open)
            _d_data['high'].append(l.high)
            _d_data['low'].append(l.low)
            _d_data['close'].append(l.close)
            _d_data['volume'].append(l.volume)
        self.df_prices = pd.DataFrame(_d_data)
#        print(self.df_prices)

    def calc_MA(self, ndays=25):
#        print(self.df_prices['close'].rolling(center=False, window=ndays).mean())
        return self.df_prices.ix[:,'close'].rolling(center=False, window=ndays).mean()

    def calc_EM(self):
        pass

    def calc_Diff_from_MA(self, ndays=25):
        _latest_ma = self.calc_MA(ndays).ix[ndays-1]
        _latest_price = self.df_prices.ix[0, 'close']
        diff_rate = (_latest_price - _latest_ma) / _latest_ma
        return _latest_price, _latest_ma, diff_rate


if __name__ == '__main__':
    pass

