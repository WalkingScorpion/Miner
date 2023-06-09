import sys
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf
from stock_strategy import cat_strategy as cs
from utils import stock_utils
import tushare as ts

def handle(start, end, code_list, df_his, f_info_l):
    local = code_list[start : end]
    begin = datetime.datetime.now()
    stp = begin.strftime("%Y-%m-%d %H:%M:%S")
    code = ','.join(local)
    #print('---- Batch [%d, %d) %s ----' % (start, end, stp))
    rt = rsf.RtSnowballFetcher(code)
    df_rt = rt.fetch_data()
    count = 0
    for c in local:
        h = stock_utils.extract_from_dflist(df_his, c)
        r = stock_utils.extract(df_rt, c)
        s = cs.CatStrategy(h, r)
        mark, reason = s.run_strategy()
        if mark:
            f_info_l[0] = f_info_l[0] + c + " " + reason + '\n'
            print(c + " " + str(mark) + " " + reason)
    sink = datetime.datetime.now()
    gap = (sink - begin).seconds 
    #print('---- Batch time %d s ----' % gap)


if __name__=="__main__":
    #ts.set_token('d78d8913b060771bebe19279df50a929e5f6fc81a48c179bf02a8c88')
    ts.set_token('d2ff623db1a7255defc5b597a2b530c9d671505c49e5e49477cc9ccb')
    df_his, st = stock_utils.fetch_stock_info(days=29, offset=1)
    if (len(sys.argv) > 1):
        st = sys.argv[1]
    code_list = st.split(",")
    while True:
        stp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp = '---- Begin %s ----' % stp
        f_info = ""
        f_info_l = [f_info]
        print(tmp)
        f_info_l[0] = f_info_l[0] + tmp + '\n'
        i = 0
        batch = 150
        while i < len(code_list):
            start = i
            end = i + batch if i + batch < len(code_list) else  len(code_list)
            handle(start, end, code_list, df_his, f_info_l)
            i = i + batch
        stp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp = '---- All Done %s ----' % stp
        print(tmp)
        f_info_l[0] = f_info_l[0] + tmp + '\n'
        with open('newdata', 'w+') as f:
            f.write(f_info_l[0])
