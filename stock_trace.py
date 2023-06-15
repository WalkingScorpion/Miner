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

        df_path = 'data/mock_trade/' + d + '.csv'
        rdf = pd.read_csv(df_path, index_col=0)
        i = 0
        while i < rdf.shape[0]:
            code = rdf['ts_code'][i]
            rt = rsf.RtSnowballFetcher(code)
            rt.fetch_data()
            h = tuf.extract_snapshot(code)
            r = rt.extract_snapshot(code)
            s = xs.XStrategy(h, r, 1.5)
            s.sell_strategy(i, rdf)
            i += 1
        print(rdf)
        print("potd:", rdf[(rdf['profile'] > -9) & (rdf['sell_date'].notnull())]['potd'].mean())
        print("pond:", rdf[(rdf['profile'] > -9) & (rdf['sell_date'].notnull())]['pond'].mean())
        rdf.to_csv(df_path)
            
        print('---- All Done %s ----' % d)
