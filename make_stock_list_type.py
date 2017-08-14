#!/usr/bin/python
# coding = utf-8

import jsm
import sqlite3
import os
from operator import itemgetter

if __name__ == '__main__':

    dbname = "brand.sqlite3"
    try:
        os.remove(dbname)
    except OSError:
        pass
    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()
    create = 'create table if not exists brand_list (class_code, ccode, market, name)'
    cursor.execute(create)

    q = jsm.Quotes()

    class_code = {'0050', '1050', '2050', '3050', '3100', '3150', '3200', '3250', '3300', '3350', '3400', '3450', '3500', '3550', '3600', '3650', '3700', '3750', '3800', '4050', '5050', '5100', '5150', '5200', '5250', '6050', '6100', '7050', '7100', '7150', '7200', '8050', '9050'}

    data = []
    for code in class_code:
        bl = q.get_brand(code)
        for l in bl:
            data.append((code, l.ccode, l.market, l.name))

    data = sorted(data, key=itemgetter(0))
    insert = 'insert into brand_list (class_code, ccode, market, name) values (?,?,?,?)'
    try:
        cursor.executemany(insert, data)
        connection.commit()
        print('DB書き込み完了')
    except:
        print('DB書き込みエラー')

