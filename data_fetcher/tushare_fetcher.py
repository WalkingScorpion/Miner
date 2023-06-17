import tushare as ts
import time
import sys
import os
import datetime
import pandas as pd

class TushareFetcher(object):
    def __init__(self):
        self.dfl = []
        self.code_list = []

    def fetch_stock_info_by_tradedate(self, dir_path, td):
        #ts.set_token('d78d8913b060771bebe19279df50a929e5f6fc81a48c179bf02a8c88')
        ts.set_token('d2ff623db1a7255defc5b597a2b530c9d671505c49e5e49477cc9ccb')
        pro = ts.pro_api()
        f = dir_path + "/" + td + ".csv"
        if os.access(f, os.F_OK):
            r = pd.read_csv(f)
            if r.shape[0] > 0:
                return r
        r = pro.daily(trade_date=td, adj='qfq')
        if r.shape[0] > 0:
            r.to_csv(dir_path + "/" + td + ".csv")
        return r

    def extract_snapshot(self, code):
        l = []
        for df in self.dfl:
            r = df[df.ts_code == code]
            l.append(r)
        r = pd.concat(l).reset_index(drop=True)
        return r

    def fetch_data(self, dir_path="data/stock_info/", days=30, offset=0,
        date = datetime.datetime.now()):
        o = datetime.timedelta(days=offset)
        d = datetime.timedelta(days=1)
        e = date - o
        i = 0
        sl = []
        while (i < days):
            wd = e.weekday()
            td = e.strftime("%Y%m%d")
            e = e - d
            if wd == 5 or wd == 6:
                continue
            r = self.fetch_stock_info_by_tradedate(dir_path, td)
            if r.shape[0] <= 0:
                continue
            self.dfl.append(r)
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
        self.code_list = list(rs)

if __name__=="__main__":
    f = TushareFetcher()
    df = f.fetch_data(date = datetime.datetime.strptime("20230614", "%Y%m%d"))
    print(pd.concat(f.dfl)['trade_date'])
