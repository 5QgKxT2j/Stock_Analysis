#!/usr/bin/python
# coding = utf-8

import pandas as pd
import sys
import itertools
from matplotlib import pyplot as plt
import numpy as np
import talib

### import my library ###
from database import DB
from scraping_stock_data import class_jsm
import analyzer as ana

class Model():
    def __init__(self, name, code_list, debug_mode):

        if name == 's_model1':

            jsm_obj = class_jsm()
            for code in code_list:
                db = DB(code, debug_mode) # create a DB object
                jsm_obj.insert_Stock_Data(db=db, code=code) # write jsm datas to the Database

                data = db.select(table='stock_data', start='2010-01-01 00:00:00')
                date = pd.to_datetime(data['date'])
                upper, middle, lower = talib.BBANDS(np.array(data['adj_close'], dtype='f8'))

                plt.subplot(2, 1, 1)
                plt.plot(date, data['adj_close'], linewidth=0.5, label="close")
                plt.plot(date, middle, linewidth=0.5, label="middle")
                plt.plot(date, upper, label="upper", linewidth=0.5)
                plt.plot(date, lower, label="lower", linewidth=0.5)

                plt.legend(loc='upper left')


                plt.subplot(2, 1, 2)
                rsi14 = talib.RSI(np.array(data['adj_close'], dtype='f8'), timeperiod=14)
                plt.plot(date, rsi14, linewidth=0.5, label="rsi14")
                plt.legend(loc='upper left')
                plt.show()


        elif name == 's_model2':
            pass

        elif name == 'momentum':
            pass

        else:

            print('No model found')
            sys.exit(-1)

