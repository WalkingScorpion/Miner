import sys
import requests
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf
from stock_strategy import cat_strategy as cs
import tushare as ts

show_url = "http://stockpage.10jqka.com.cn/"
send_url = "http://www.pushplus.plus/send"

def handle(start, end, code_list, tuf, f_info_l):
    local = code_list[start : end]
    begin = datetime.datetime.now()
    stp = begin.strftime("%Y-%m-%d %H:%M:%S")
    code = ','.join(local)
    #print('---- Batch [%d, %d) %s ----' % (start, end, stp))
    rt = rsf.RtSnowballFetcher(code)
    rt.fetch_data()
    count = 0
    for c in local:
        h = tuf.extract_snapshot(c)
        r = rt.extract_snapshot(c)
        s = cs.CatStrategy(h, r)
        mark, reason = s.run_strategy()
        if mark:
            f_info_l[0] += "<a href=\"" + show_url + c.split('.')[0] + "\">" + \
              c + "</a> " + reason + ' <br>\n'
            f_info_l[1] += "<a href=\"" + show_url + c.split('.')[0] + "\">" + \
              c + "</a> " + reason + ' <br>'
            print(c + " " + str(mark) + " " + reason)
    sink = datetime.datetime.now()
    gap = (sink - begin).seconds 
    #print('---- Batch time %d s ----' % gap)


if __name__=="__main__":
    tuf = tuf.TushareFetcher()
    tuf.fetch_data(offset=1)
    df_his = tuf.dfl
    if (len(sys.argv) > 1):
        st = sys.argv[1]
        code_list = st.split(",")
    else:
        code_list = tuf.code_list
    #while
    stp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tmp = '---- Begin %s ----' % stp
    f_info = ""
    send_info = ""
    f_info_l = [f_info, send_info]
    print(tmp)
    f_info_l[0] += tmp + '<br>\n'
    f_info_l[1] += tmp + '<br>'
    i = 0
    batch = 150
    while i < len(code_list):
        start = i
        end = i + batch if i + batch < len(code_list) else  len(code_list)
        handle(start, end, code_list, tuf, f_info_l)
        i = i + batch
    stp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tmp = '---- All Done %s ----' % stp
    print(tmp)
    f_info_l[0] += tmp + '<br>\n'
    f_info_l[1] += tmp + '<br>'
    with open('index.html', 'w+') as f:
        f.write(f_info_l[0])
    params = {
      "token" : "b0b164534ed046bcbd0719fa93954d54",
      "title" : "“猫周期”量化 选股推送",
      "content" : f_info_l[1],
      "topic" : "1",
      "template" : "html",
    }
    requests.get(url = send_url, params = params)
