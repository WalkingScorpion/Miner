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

def extract(df, code):
    r = df[df['ts_code'] == code].reset_index(drop=True)
    return r

def extract_from_dflist(dfl, code):
    l = []
    for df in dfl:
        r = df[df['ts_code'] == code]
        l.append(r)
    r = pd.concat(l).reset_index(drop=True)
    return r

def fetch_stock_info_by_tradedate(dir_path, td):
    pro = ts.pro_api()
    f = dir_path + "/" + td + ".json"
    if os.access(f, os.F_OK):
        r = pd.read_json(f)
        if r.shape[0] > 0:
            return r
    r = pro.daily(trade_date=td, adj='qfq')
    if r.shape[0] > 0:
        r.to_json(dir_path + "/" + td + ".json")
    return r

def fetch_stock_info(dir_path="data/stock/", days=29, offset=0):
    o = datetime.timedelta(days=offset)
    d = datetime.timedelta(days=1)
    e = datetime.datetime.now() - o
    i = 0
    l = []
    sl = []
    while (i < days):
        td = e.strftime("%Y%m%d")
        e = e - d
        r = fetch_stock_info_by_tradedate(dir_path, td)
        if r.shape[0] <= 0:
            continue
        l.append(r)
        code_set = set()
        for c in r['ts_code']:
            code_set.add(c)
        sl.append(code_set)
        i = i + 1
    rs = set()
    for cs in sl:
        if len(rs) == 0:
            rs = cs
        else:
            rs.intersection_update(cs)
    return l, ','.join(rs)

if __name__=="__main__":
    l, s = fetch_stock_info()
    print (len(l), s)
