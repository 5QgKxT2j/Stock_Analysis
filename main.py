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
    result = analyzer.momentum(df)
    
    start = result.index[0]
    end = result.index[len(result.index) - 1]
    print('start = {start}, end = {end}'.format(start=start, end=end))

    result.plot(y=['adj_close','asset'])
    plt.savefig('./figure/momentum_{ccode}.png'.format(ccode=args.target))
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

