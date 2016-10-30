#!/usr/bin/python
# coding = utf-8

import pandas as pd
import sys
import itertools

### import my library ###
from database import DB

class Model():
    def __init__(self, name, code_list):

        if name == 's_model1':

            sm1 = simple_model1()
            for code in code_list:
                db = DB(code) # create a DB object
                data = db.read()
                ldiff_th = [-0.2, -0.1]
                linc_th = [1.1, 1.2]
                ldline = [20, 30]
                lma_day = [25, 50, 75]
                print(sm1.show_diff_from_MA(data, lma_day))
                params = itertools.product(ldiff_th, linc_th, ldline, lma_day)
                for a, b, c, d in params:
                    sm1.fit(data, a, b, c, d)

        elif name == 's_model2':
            pass

        else:
            print('No model found')
            sys.exit(-1)


class simple_model1():

    def __init__(self):
        pass
    def fit(self, stock_data, diff_th=-0.10, inc_th=1.1, dline=20, ma_day=25):

        res = []
        correct, wrong = 0, 0
        col = 'Diff_from_{day}MA'.format(day=ma_day)

        for i in range(len(stock_data)-1):
            if stock_data.ix[i, col] <= diff_th:
                if stock_data.ix[i, 'close'] * inc_th < max(stock_data.ix[i:i+dline, 'close']):
                    correct += 1
                    inc = max(stock_data.ix[i:i+dline, 'close']) / stock_data.ix[i, 'close']
                    res.append((stock_data.ix[i].name, inc))
                else:
                    wrong += 1
        try:
            res = correct/(correct+wrong)
            if (res > 0.6):
                print(res, correct, wrong, diff_th, inc_th, dline, ma_day)
            return None
        except:
            return None

    def show_table(self):
        print(stock_data)


    def show_diff_from_MA(self, data, ma_day):
        last = len(data)-1
        dict = {}
        for d in ma_day:
            col = 'Diff_from_{day}MA'.format(day=d)
            diff = data.ix[last, col]
            dict[d] = diff
        return dict



class Momentum():
    def __init__(self):
        pass
