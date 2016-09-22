#!/usr/bin/python
# coding = utf-8

import pandas as pd

### import my library ###
from analysis import Analysis


class simple_model1():

    def __init__(self, stock_data, ma_days=[25]):
        self.stock_data = stock_data.set_index('date')

        for ma_day in ma_days:
            ana = Analysis(df_prices=self.stock_data, ndays=ma_day)
            diff = ana.Dist_of_Diff_form_MA()

            self.stock_data = pd.concat([self.stock_data, diff], axis=1)


    def fit(self, diff_th=-0.10, inc_th=1.1, dline=20, ma_day=25, skip=0):

        res = []
        correct, wrong = 0, 0
        col = 'diff_{day}ma'.format(day=ma_day)

        for i in range(skip, len(self.stock_data)-1):
            if self.stock_data.ix[i, col] <= diff_th:
                if self.stock_data.ix[i, 'close'] * inc_th < max(self.stock_data.ix[i:i+dline, 'close']):
                    correct += 1
                    inc = max(self.stock_data.ix[i:i+dline, 'close']) / self.stock_data.ix[i, 'close']
                    res.append((self.stock_data.ix[i].name, inc))
                else:
                    wrong += 1

#        print('The number of samples:', len(self.stock_data))
#        print('correct rate: {0} (correct: {1} wrong:{2})'.format(correct/(correct+wrong), correct, wrong))
        return correct/(correct+wrong), correct, wrong

    def predict(self):
        pass

    def show(self):
        print(self.stock_data)

