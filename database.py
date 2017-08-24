#!/usr/bin/python
# coding = utf-8

import sqlite3
import datetime as dt
import pandas as pd
import pandas.io.sql as psql
import sys


class DB():
    def __init__(self, code):
        self.code = code
        dbname = './database/code_{0}.sqlite3'.format(code)
        self.con = sqlite3.connect(dbname)
        self.cur = self.con.cursor()

    def select(self, table, col='*', start='', end='', raw_sentence=''):
        '''return a pandas Dataframe, retrieving from the database'''

        if raw_sentence:
            sql_select = 'select distinct {col} from {table} {raw}'.format(table=table, col=','.join(col), raw=raw_sentence)
        else:
            if (not start) and (not end): # 範囲選択がされなかった場合、全データ読み込み
                sql_select = 'select distinct {col} from {table} order by date'.format(table=table, col=','.join(col))
            elif start and (not end): # 開始日のみ指定
                sql_select = 'select distinct {col} from {table} where date >= "{s}" order by date'.format(table=table, col=','.join(col), s=start)
            elif (not start) and end: # 終了日のみ指定
                sql_select = 'select distinct {col} from {table} where date <= "{e}" order by date'.format(table=table, col=','.join(col), e=end)
            elif start and end: # 取得開始日と終了日を共に指定
                sql_select = 'select distinct * from {table} where date between "{s}" and "{e}" order by date'.format(table=table, col=','.join(col), s=start, e=end)

        return psql.read_sql(sql_select, self.con)


    def check_table(self, table):
        '''If the table is found, return False. If not so, create a new table and return True.'''

        sql_check = 'select name from sqlite_master where type="table" and name="{table}"'.format(table=table)
        c = self.cur.execute(sql_check)
        if not c.fetchone():
            return True
        else:
            return False


    def create(self, table, data):
        try:
            data.to_sql(table, self.con, if_exists='replace', index=False)
        except:
            print('Failed: Code {0}: cannot write stock datas to the database'.format(self.code))
            sys.exit(-1)


    def insert(self, table, data):
        try:
            data.to_sql(table, self.con, if_exists='append', index=False)
        except:
            print('Failed: Code {0}: cannot write stock datas to the database'.format(self.code))
            sys.exit(-1)


    def drop_table(self, table):
        ''' delete an invalid table'''
        sql_drop_table = 'drop table {table}'.format(table=table)
        self.cur.execute(sql_drop_table)

if __name__ == '__main__':
    pass
