#!/usr/bin/python
# coding = utf-8
import time, datetime
import jsm 
from concurrent.futures import ProcessPoolExecutor
from pandasjsm import pandasjsm


def work(ccode):
    print(ccode)
    pj = pandasjsm()
    # df = pj.get_historical_prices(args.target, all=True)
    df = pj.get_historical_prices(ccode, start_date=datetime.date(2016, 1, 1))
    # df = pj.get_historical_prices(ccode)

def main():
    _e = ProcessPoolExecutor(max_workers=8) # 並列数
    """銘柄リストをworkへ投入"""
    q = jsm.Quotes()
    print("銘柄リスト取得開始")
    bl = q.get_brand()
    print("銘柄リスト取得完了")
    for key in bl.keys():
        for l in bl[key]:
            _e.submit(work, l.ccode)


if __name__ == '__main__':
    main()


