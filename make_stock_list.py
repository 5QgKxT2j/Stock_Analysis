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
    create = 'create table if not exists brand_list (ccode, market, name)'
    cursor.execute(create)

    q = jsm.Quotes()
    bl = q.get_brand()
    data = []
    for v in bl.values():
        data.append((v.ccode, v.market, v.name))

    data = sorted(data, key=itemgetter(0))
    insert = 'insert into brand_list (ccode, market, name) values (?,?,?)'
    try:
        cursor.executemany(insert, data)
        connection.commit()
        print('DB書き込み完了')
    except:
        print('DB書き込みエラー')

