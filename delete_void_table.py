#!/usr/bin/python
# coding = utf-8


import sqlite3

if __name__ == '__main__':
    dbname = "stock.db"
    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()

    check_table = 'select name from sqlite_master where type="table"'  # テーブルの存在確認
    for t in cursor.execute(check_table).fetchall():
#        print(*t)
        select = 'select * from {0} limit 1'.format(*t)
        if not cursor.execute(select).fetchone(): # テーブルが空の場合
            delete = 'drop table {0}'.format(*t)
            cursor.execute(delete)
            print(*t)
