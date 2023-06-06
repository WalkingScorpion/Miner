from numpy import *
import tushare as ts
import datetime


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

def fetch_code_list():
    ts.set_token('d78d8913b060771bebe19279df50a929e5f6fc81a48c179bf02a8c88')
    pro = ts.pro_api()
    d = datetime.timedelta(days=60)
    e = datetime.datetime.now()
    s = e - d
    df = ts.pro_bar(ts_code="000002.SZ", adj='qfq', start_date=s.strftime("%Y%m%d"), end_date=e.strftime("%Y%m%d"), offset=0, limit=30)
    trade_date = df['trade_date'][29]
    r = pro.daily(trade_date=trade_date)
    l = ','.join(r['ts_code'])
    return l

if __name__=="__main__":
    fetch_code_list()
