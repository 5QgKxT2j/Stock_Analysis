#!/usr/bin/python
# coding = utf-8

import pandas as pd

### import my library ###
from analysis import Analysis


class simple_model1():

    def __init__(self, stock_data, ma_days=[25]):
        self.stock_data = stock_data.set_index('date')


    def fit(self, diff_th=-0.10, inc_th=1.1, dline=20, ma_day=25, skip=0):

        res = []
        correct, wrong = 0, 0
        col = 'Diff_from_{day}MA'.format(day=ma_day)

        for i in range(skip, len(self.stock_data)-1):
            if self.stock_data.ix[i, col] <= diff_th:
                if self.stock_data.ix[i, 'close'] * inc_th < max(self.stock_data.ix[i:i+dline, 'close']):
                    correct += 1
                    inc = max(self.stock_data.ix[i:i+dline, 'close']) / self.stock_data.ix[i, 'close']
                    res.append((self.stock_data.ix[i].name, inc))
                else:
                    wrong += 1
        try:
            res = correct/(correct+wrong)
            return res, correct, wrong
        except:
            return None


    def predict(self):
        pass


    def show_table(self):
#        print(self.stock_data.iloc[:, 5:])
        print(self.stock_data)


    def show_diff_from_MA(self, ma_day):
        last = len(self.stock_data)-1
        dict = {}
        for d in ma_day:
            col = 'Diff_from_{day}MA'.format(day=d)
            diff = self.stock_data.ix[last, col]
            dict[d] = diff
        return dict
