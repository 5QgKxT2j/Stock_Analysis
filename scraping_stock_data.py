#!/usr/bin/python
# coding = utf-8

import jsm
import pandas as pd
import datetime as dt


### import my library ###
from database import DB

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

