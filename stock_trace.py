import sys
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf
from stock_strategy import cat_strategy as cs
from stock_strategy import x_strategy as xs
import tushare as ts
import pandas as pd

if __name__=="__main__":
    tuf = tuf.TushareFetcher()
    tuf.fetch_data(offset=1)
    df_his = tuf.dfl
    date = sys.argv[1]
    dl = date.split(',')
    for d in dl:
        print('---- Begin %s Trace ----' % d)
#        with open('data/mock_trade/' + d) as f:
#            c = 0
#            sm = 0.0
#            for line in f:
#                line = line.strip()
#                info = line.split('|')
#                code = info[0].strip()
#                trade_time = info[1].strip()
#                price = float(info[2].strip())
#                rt = rsf.RtSnowballFetcher(code)
#                rt.fetch_data()
#                h = tuf.extract_snapshot(code)
#                r = rt.extract_snapshot(code)
#                s = xs.XStrategy(h, r, 1.5)
#                ret = s.sell_strategy(code, trade_time.split()[0], price)
#                print('%s  --->  %s' % (line, ret))
#                sp = ret.split('|')
#                if len(sp) > 2:
#                    profile = float(ret.split('|')[2])
#                    if profile > -9:
#                        sm += profile
#                        c += 1
#            print(sm / c)

        df_path = 'data/mock_trade/' + d + '.csv'
        rdf = pd.read_csv(df_path, index_col=0)
        i = 0
        while i < rdf.shape[0]:
            code = rdf['ts_code'][i]
            price = rdf['buy'][i]
            trade_time = rdf['buy_date'][i]
            rt = rsf.RtSnowballFetcher(code)
            rt.fetch_data()
            h = tuf.extract_snapshot(code)
            r = rt.extract_snapshot(code)
            s = xs.XStrategy(h, r, 1.5)
            s.sell_strategy(code, trade_time.split()[0], price, rdf = rdf)
            i += 1
        print(rdf)
        print("potd:", rdf[(rdf['profile'] > -9) & (rdf['sell_date'].notnull())]['potd'].mean())
        print("pond:", rdf[(rdf['profile'] > -9) & (rdf['sell_date'].notnull())]['pond'].mean())
        rdf.to_csv(df_path)
            
        print('---- All Done %s ----' % d)
