from numpy import *
import tushare as ts
import datetime
import io
import time
import os
import pandas as pd

def new_trace_df():
    rdf = pd.DataFrame(columns=['ts_code','buy_date', 'buy', 'tags', 'vol', 'sell_date', 'sell', 'profile', 'potd', 'pond'])
    return rdf

def get_k(df, k, offset = 0):
    return df['close'][offset : offset + k].mean()

def get_boll(df, k, offset = 0):
    t = df['close'][offset : offset + k]
    m = t.mean()
    s = t.std()
    return m, m + 2 * s, m - 2 * s

def get_trade_second(ts):
    t = datetime.datetime.strptime(ts, '%H:%M:%S')
    s0 = datetime.datetime.strptime("09:30:00", '%H:%M:%S')
    e0 = datetime.datetime.strptime("11:30:00", '%H:%M:%S')
    s1 = datetime.datetime.strptime("13:00:00", '%H:%M:%S')
    e1 = datetime.datetime.strptime("15:00:00", '%H:%M:%S')
    d = datetime.timedelta(minutes=90)
    if t > e1:
        t = e1
    if e0 < t < s1:
        t = e0
    if t < s0:
        t = s0
    g = t - s0
    if t > s1:
        g -= d
    return int(g.total_seconds())

def get_volume_ratio(df, window = 5):
    tsl = str(df['trade_date'][0]).split()
    if len(tsl) > 1:
      ts = tsl[1]
      evol = df['vol'][0] / get_trade_second(ts)
      i = 0
      s = 0
      while (i < window):
          s += df['vol'][i + 1]
          i += 1
      mvol = s / window / 14400
      return evol / mvol
    else:
        return df['vol'][0] / window / 14400

if __name__=="__main__":
    print(get_trade_second("09:20:30"), 0)
    print(get_trade_second("09:30:30"), 30)
    print(get_trade_second("11:29:00"), 7140)
    print(get_trade_second("11:31:00"), 7200)
    print(get_trade_second("12:59:00"), 7200)
    print(get_trade_second("13:01:00"), 7260)
    print(get_trade_second("14:59:00"), 14340)
    print(get_trade_second("15:31:00"), 14400)
