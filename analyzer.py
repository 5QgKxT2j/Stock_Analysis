#!/usr/bin/python
# coding = utf-8

### import my library ###
from pandasjsm import pandasjsm
import talib as ta
import pandas as pd
import numpy as np


class analyzer(object):
    '''分析データ入力と結果出力のインタフェース
    '''
    def __init__(self):
        pass
    
    @classmethod
    def momentum(cls, df, column='adj_close', period=250):
        '''モメンタムから分析
        '''

        momentum = ta.MOM(df[column].values.astype(np.float64), period)
        # buy: 1, sell: -1, nutral: 0
        signal = [0 for row in range(momentum.size)]
        for i in range(momentum.size):
            if i > 0:
                if momentum[i-1] < 0 and momentum[i] > 0:
                    signal[i] = 1
                if momentum[i-1] > 0 and momentum[i] < 0:
                    signal[i] = -1

        result = pd.DataFrame(momentum, index=df.index, columns=['momentum'])
        result['signal'] = signal

        result['asset'] = cls.__eval_performance(df, signal)

        return pd.concat([df, result], axis=1)
    
#    @classmethod
#    def random_select(cls, df, plus = 0.1, minus = 0.05):
#        '''ランダムに銘柄を選択し、損切りor利確
#        '''
#        np.random.rand()
#
#        pass

    @classmethod
    def ma_deviation(cls, df,column='adj_close' ,window=25):
        '''移動平均乖離率から分析
        '''
        ma = df[column].rolling(center=False, window=window).mean()
        df['{0}MA'.format(window)] = ma
        df['{0}MA_deviation'.format(window)] = (df[column] - ma) / ma
        return df

    @classmethod
    def garch(cls, df):
        '''garchモデル推定から分析
        '''
        pass

    @classmethod
    def __eval_performance(self, df, signal, budget=10000):
        '''シグナルにあわせた売買でのパフォーマンスを計算
        '''
        size = len(signal)
        cash = [None for i in range(size)]
        position = [None for i in range(size)]
        asset = [None for i in range(size)]
        cash[0] = budget
        position[0] = 0
        for i, (index, row) in enumerate(df.iterrows()):
            if i > 0:
                cash[i] = cash[i-1]
                position[i] = position[i-1]
                if signal[i] == 1:
                    #buy
                    amount = cash[i] // row['adj_close']
                    position[i] += amount
                    cash[i] -= row['adj_close'] * amount
                elif signal[i] == -1:
                    #sell
                    cash[i] += row['adj_close'] * position[i-1]
                    position[i] = 0
            asset[i] = cash[i] + position[i] * row['adj_close']
        
        return asset

if __name__ == '__main__':
    pj = pandasjsm()
    df = pj.get_historical_prices('9433', all=True)
    result = analyzer.momentum(df)
    print(result)
    pass

'''
class Diff_from_MA():

    def __init__():
        df = self._create_DF(h_prices)
        new_data_size = len(df)
        select = 'select distinct {rows} from stock_data order by date desc limit {num}'.format(rows='date, open, high, low, close, volume', num=(max(MA_DAY)-1))
        data4ma = psql.read_sql(select, self.con)
        data4ma = data4ma.drop_duplicates(subset='date')
        data4ma = data4ma.sort_values('date')
        data4ma = data4ma.set_index('date')
        df = pd.concat([data4ma, df], axis=0)
        df = self._add_MA_row(df)
        df = df.iloc[len(df.index)-new_data_size:]

    def _add_MA_row(self, df):

        ma_list = []
        diff_rate_list = []
        for d in MA_DAY:
            ma = df['close'].rolling(center=False, window=d).mean()
            ma.name = '{0}MA'.format(d)
            diff_rate = (df['close'] - ma) / ma
            diff_rate.name = 'Diff_from_{0}MA'.format(d)
            ma_list.append(ma)
            diff_rate_list.append(diff_rate)

        return pd.concat([df, *ma_list, *diff_rate_list], axis=1)

'''