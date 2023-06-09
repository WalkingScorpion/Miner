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
        ts.set_token('d78d8913b060771bebe19279df50a929e5f6fc81a48c179bf02a8c88')
        #ts.set_token('d2ff623db1a7255defc5b597a2b530c9d671505c49e5e49477cc9ccb')
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

    def extract_snapshot(self, code):
        l = []
        for df in self.dfl:
            r = df[df['ts_code'] == code]
            l.append(r)
        r = pd.concat(l).reset_index(drop=True)
        return r

    def fetch_data(self, dir_path="data/stock/", days=29, offset=0,
        date=datetime.datetime.now()):
        o = datetime.timedelta(days=offset)
        d = datetime.timedelta(days=1)
        e = date - o
        i = 0
        sl = []
        while (i < days):
            td = e.strftime("%Y%m%d")
            e = e - d
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
    f = TushareFetcher(sys.argv[1])
    df = f.fetch_data()
    print (df)
