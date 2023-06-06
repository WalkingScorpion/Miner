import sys
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf
from stock_strategy import cat_strategy as cs
from utils import stock_utils

if __name__=="__main__":
    if (len(sys.argv) > 1):
        st = sys.argv[1]
    else:
        st = stock_utils.fetch_code_list()
    code_list = st.split(",")
    i = 0
    batch = 190
    while i < len(code_list):
        begin = datetime.datetime.now()
        stp = begin.strftime("%Y-%m-%d %H:%M:%S")
        start = i
        end = i + batch if i + batch < len(code_list) else  len(code_list)
        local = code_list[start : end]
        code = ','.join(local)
        print('---- Batch [%d, %d) %s ----' % (start, end, stp))
        rt = rsf.RtSnowballFetcher(code)
        history30 = tuf.TushareFetcher(code)
        df_his = history30.fetch_data()
        df_rt = rt.fetch_data()
        for c in local:
            h = stock_utils.extract(df_his, c)
            r = stock_utils.extract(df_rt, c)
            s = cs.CatStrategy(h, r)
            mark, reason = s.run_strategy()
            print (c, mark, reason)
        i = i + batch
        sink = datetime.datetime.now()
        gap = (sink - begin).seconds 
        print('---- Batch time %d s----' % gap)
        wait = 70 - gap
        if wait > 0:
            time.sleep(wait)
