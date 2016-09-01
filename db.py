import sys
import sqlite3
import jsm
import datetime as dt

param = sys.argv

dbname = "stock.db"

connection = sqlite3.connect(dbname)
cursor = connection.cursor()

CODE = int(param[1])
START_DATE = dt.datetime.strptime(param[2], '%Y%m%d')
END_DATE = START_DATE
if len(param) == 4:
    END_DATE = dt.datetime.strptime(param[3], '%Y%m%d')

try:
    h_prices = jsm.Quotes().get_historical_prices(CODE, jsm.DAILY, start_date = START_DATE, end_date = END_DATE)
except:
    print("データ取得失敗")
    h_prices = []


create = "create table if not exists code_" + str(CODE) + "(date datetime unique, open, high, low, close, volume)"
cursor.execute(create)


data = []
for l in h_prices:
    data.append((l.date, l.open, l.high, l.low, l.close, l.volume))

insert = 'insert into code_' + str(CODE) + '(date, open, high, low, close, volume) values (?,?,?,?,?,?)'

cursor.executemany(insert, data)
connection.commit()

select = 'select * from code_' + str(CODE)
for row in cursor.execute(select):
    print(row)
