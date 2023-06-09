from numpy import *
import tushare as ts
import datetime
import io
import os
import pandas as pd


def get_k(df, k, offset = 0):
    return df['close'][offset : offset + k].mean()

def get_boll(df, k, offset = 0):
    t = df['close'][offset : offset + k]
    m = t.mean()
    s = t.std()
    return m, m + 2 * s, m - 2 * s

if __name__=="__main__":
    l, s = fetch_stock_info()
    print (len(l), s)
