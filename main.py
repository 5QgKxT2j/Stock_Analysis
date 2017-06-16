#!/usr/bin/python
# coding = utf-8

### import formal libs ###
import argparse
import pandas as pd

### import my libs ###
from pandasjsm import pandasjsm
from analyzer import analyzer
import matplotlib.pyplot as plt


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    #parser.add_argument('target', help='input stock code or filename with -f')
    parser.add_argument('target', help='input stock code')
    #parser.add_argument('-f', help='specify a filename', action='store_true')
    #parser.add_argument('-d', help='display debug messages', action='store_true')
    #parser.add_argument('-m', help='specify a model name', metavar='model', required=True)

    args = parser.parse_args()

    pj = pandasjsm()
    df = pj.get_historical_prices(args.target, all=True)
    
    analyzer.ma_deviation(df)
    analyzer.ma_deviation(df, window=50)
    analyzer.ma_deviation(df, window=250)
    analyzer.momentum(df)

    fig, [ax1, ax2, ax3] = plt.subplots(3,1,figsize=(10,15))
    df.plot(ax = ax1,y=['adj_close', '25MA', '50MA', '250MA'])
    #ax2 = ax.twinx()
    #df.plot(ax = ax2, y=['momentum'])
    df.plot(ax = ax3, y=['25MA_deviation', '50MA_deviation', '250MA_deviation'])
    plt.savefig('./figure/ma_{ccode}.png'.format(ccode=args.target))
    pass


    '''
    if args.f:
        with open(args.target, 'r') as f:
            code_list = [line.rstrip() for line in f]
    else:
        code_list = [args.target, ]

    if args.d:
        debug_mode = True
        print('Debug mode on')
    else:
        debug_mode = False

    model_name = args.m
    model(model_name, code_list, debug_mode)
    '''

