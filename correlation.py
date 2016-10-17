from db import DB
import datetime as dt
import sqlite3
import pandas.io.sql as psql
import pandas as pd
import matplotlib.pyplot as plt
import pandas.tseries.offsets as offsets
import sys

if __name__ == '__main__':
    #データ読み込み
    code = sys.argv[1]
    db = DB(code)
    data = db.read()
    
    #indexをdatetime化
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date')
    
    #乖離率と値上げの相関
    columns = ['max_close','diff_from_25MA', 'increase_rate']
    correlation = pd.DataFrame(columns = columns, )

    #tmpdata={'max_close':[], 'diff_from_25MA':[], 'increase_rate':[]}
    for date in data.index:
    #    #print(date)
        max_close = data['close'][date + offsets.Day(1):date + offsets.Day(30)].max()
        diff_from_25MA = data['Diff_from_25MA'][date]
        buy = data.ix[date:][1:2]['open']
        if buy.size > 0:
            buy = buy.values[0]
            increase_rate = max_close/buy
        
            correlation = correlation.append(pd.DataFrame([[max_close,diff_from_25MA,increase_rate]], columns=columns))
    
    ax = correlation[correlation['diff_from_25MA'] < -0.1].plot.scatter(x = 'diff_from_25MA', y = 'increase_rate')
    fig = ax.get_figure()
    fig.savefig('./figure/{}_10%.png'.format(code))
    
    ax = correlation.plot.scatter(x = 'diff_from_25MA', y = 'increase_rate')
    fig = ax.get_figure()
    fig.savefig('./figure/{}.png'.format(code))
    
    print(correlation[correlation['diff_from_25MA'] < -0.1][['diff_from_25MA','increase_rate']].corr().ix[0,1])
