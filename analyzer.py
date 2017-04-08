#!/usr/bin/python
# coding = utf-8


### import my library ###
from pandasjsm import pandasjsm as pj


class analyser(object):
    '''分析データ入力と結果出力のインタフェース
    '''
    def __init__(self):
        pass
    
    @classmethod
    def momentum(cls, df):
        '''モメンタムから分析
        '''
        pass
    
    @classmethod
    def ma_deviation(cls, df):
        '''移動平均乖離率から分析
        '''
        pass

    @classmethod
    def garch(cls, df):
        '''garchモデル推定から分析
        '''

'''
class class_jsm():
    def __init__(self):
        pass

    def insert_Stock_Data(self, db, code, loop=False):

        if db.check_table(table='stock_data'):
            try:
                jsm_data = jsm.Quotes().get_historical_prices(code, jsm.DAILY, all=True)
            except:
                return False
        else:
            try:
                raw = 'order by date desc limit 1'
                dtime = db.select(table='stock_data', col=('date',), raw_sentence=raw)
            except:
                if loop:
                    return False
                # The table exists, but no data is inserted (maybe caused by a force process kill)
                db.drop_table(table='stock_data')
                return self.insert_Stock_Data(db, code, loop=True)

            dtime = dt.datetime.strptime(dtime['date'][0], '%Y-%m-%d %H:%M:%S')
            latest_day =  dt.date(dtime.year, dtime.month, dtime.day)
            s = latest_day + dt.timedelta(days=1)
            e = dt.date.today()
            if s < e:
                try:
                    jsm_data = jsm.Quotes().get_historical_prices(code, jsm.DAILY, start_date=s, end_date=e)
                except:
                    return False
            else:
                return False

        df_data = self.jsm_to_df(jsm_data)
        db.insert(table='stock_data', data=df_data)
        return True

    def jsm_to_df(self, jsm_data):
        data = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
        for d in jsm_data:
            data['date'].append(d.date)
            data['open'].append(d.open)
            data['high'].append(d.high)
            data['low'].append(d.low)
            data['close'].append(d.close)
            data['volume'].append(d.volume)
        df_data = pd.DataFrame(data)
        df_data = df_data.drop_duplicates(subset='date')
        df_data = df_data.sort_values('date')

        return df_data


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

    def _create_DF(self, h_prices):
        data = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
        for l in h_prices:
            data['date'].append(l.date)
            data['open'].append(l.open)
            data['high'].append(l.high)
            data['low'].append(l.low)
            data['close'].append(l.close)
            data['volume'].append(l.volume)

        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset='date')
        df = df.sort_values('date')
        df = df.set_index('date')
        return df

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