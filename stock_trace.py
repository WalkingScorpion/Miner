import sys
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf
from stock_strategy import cat_strategy as cs
from stock_strategy import x_strategy as xs
import tushare as ts

if __name__=="__main__":
    tuf = tuf.TushareFetcher()
    tuf.fetch_data(offset=1)
    df_his = tuf.dfl
    date = sys.argv[1]
    print('---- Begin %s Trace ----' % date)
    with open('data/mock_trade/' + date) as f:
        c = 0
        sm = 0.0
        for line in f:
            line = line.strip()
            info = line.split('|')
            code = info[0].strip()
            trade_time = info[1].strip()
            price = float(info[2].strip())
            rt = rsf.RtSnowballFetcher(code)
            rt.fetch_data()
            h = tuf.extract_snapshot(code)
            r = rt.extract_snapshot(code)
            s = xs.XStrategy(h, r, 1.01)
            ret = s.sell_strategy(trade_time.split()[0], price)
            print('%s  --->  %s' % (line, ret))
            sp = ret.split('|')
            if len(sp) > 2:
                profile = float(ret.split('|')[2])
                if profile > -9:
                    sm += profile
                    c += 1
        print(sm / c)
    print('---- All Done %s ----' % date)
