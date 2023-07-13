import sys
import requests
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf
from stock_strategy import cat_strategy as cs
from stock_strategy import x_strategy as xs
import tushare as ts
import pandas as pd
from utils import stock_utils

show_url = "http://stockpage.10jqka.com.cn/"
send_url = "http://www.pushplus.plus/send"

def realtime_handle(start, end, code_list, tuf, f_info_l, rdf, strategy='cat'):
    invalid = 0
    local = code_list[start : end]
    code = ','.join(local)
    rt = rsf.RtSnowballFetcher(code)
    rt.fetch_data()
    count = 0
    for c in local:
        h = tuf.extract_snapshot(c)
        r = rt.extract_snapshot(c)
        if r.shape[0] <= 0:
            invalid += 1
            continue
        if strategy == 'cat':
            s = cs.CatStrategy(h, r)
        else:
            s = xs.XStrategy(h, r)
        mark, reason = s.buy_strategy(rdf)
        if mark:
            tmp = "<a href=\"" + show_url + c.split('.')[0] + "\">" + \
                c + "</a> " + reason + ' <br>'
            f_info_l[0] += tmp + '\n'
            f_info_l[1] += tmp
            tmp = c + " " + reason
            print(tmp)
            f_info_l[2] += tmp + '\n'
    return invalid

def stock_history_simulate(check_date, days=60, input_code="", up=2.0, low=5.0):
    ExtraNum = 30
    tufo = tuf.TushareFetcher()
    tufo.fetch_data(date=datetime.datetime.strptime(check_date, "%Y%m%d"), offset=0, days=days + ExtraNum)
    input_code_list = []
    if len(input_code) == 0:
        code_set = set(pd.concat(tufo.dfl[0:len(tufo.dfl) - ExtraNum]).reset_index(drop=True)['ts_code'].tolist())
    else:
        input_code_list = input_code.split(",")
        code_set = set(input_code_list)
    history_dict = dict()
    i = 0
    print('code size: %d' % len(code_set))
    for c in code_set:
        history_dict[c] = tufo.extract_snapshot(c)
        i += 1
        if i % 100 == 0:
            print('extract %d code' % i)

    rdf = stock_utils.new_trace_df()
    account = 200000
    i = len(tufo.dfl) - 1 - ExtraNum
    while i >= 0:
        df = tufo.dfl[i]
        date = df['trade_date'][0]
        if len(input_code_list) == 0:
            code_list = df['ts_code'].tolist()
        else:
            code_list = input_code_list

        # sell first
        drop_list = []
        j = 0
        while j < rdf.shape[0]:
            code = rdf['ts_code'][j]
            h = tufo.extract_snapshot(code)
            s = xs.XStrategy(h[h['trade_date'] <= date].reset_index(drop=True), None, up, low)
            s.sell_strategy(j, rdf, period=1)
            if len(str(rdf['sell_date'][j])) > 0:
                sd = rdf['sell_date'][j]
                tmp = h[h['trade_date'] == int(sd)].reset_index(drop=True)
                high = tmp['high'][0]
                close = tmp['close'][0]
                vol = rdf['vol'][j]
                price = rdf['sell'][j]
                amount = price * vol * 100
                fee = max(amount * 2.5 / 10000, 5.0) + amount *(1.0 / 1000 + 1.0 / 100000)
                profile = amount - rdf['vol'][j] * 100 * rdf['buy'][j] - fee
                waste = (high - price) * rdf['vol'][j] * 100
                upbound = (high - rdf['buy'][j]) / rdf['buy'][j]
                account += amount - fee
                drop_list.append(j)
                print('%d: sell %s, price %lf, vol %d, amount %lf, profile %lf, fee %lf,' % (date, code, price, vol, amount, profile, fee), end=' ')
                buf = ''
                if profile > 0:
                     buf = 'high %lf, waste %lf, upbound %lf' % (high, waste, upbound)
                print(buf)
            j += 1
        rdf.drop(drop_list, inplace=True)
        rdf.reset_index(drop=True, inplace=True)

        # buy
        buy_num = 0
        for code in code_list:
            h = history_dict[code]
            h = h[h['trade_date'] <= date].reset_index(drop=True)
            if h.shape[0] < ExtraNum:
                continue
            s = xs.XStrategy(h, None)
            mark, reason = s.buy_strategy(rdf)
            if mark:
                buy_num += 1

        drop_list = []
        while buy_num > 0:
            index = rdf.shape[0] - buy_num
            per_stock = account / buy_num
            code = rdf['ts_code'][index]
            price = rdf['buy'][index]
            vol = int(per_stock / price / 100)
            if vol > 0:
                rdf.loc[index, 'vol'] = vol
                amount = price * vol * 100
                fee = max(amount * 2.5 / 10000, 5.0)
                account -= amount + fee
                print('%d: buy %s, price %lf, vol %d, amount %lf, fee %lf' % (date, code, price, vol, amount, fee))
            else:
                drop_list.append(index)
            buy_num -= 1
        rdf.drop(drop_list, inplace=True)
        rdf.reset_index(drop=True, inplace=True)
     
        j = 0
        s = 0
        while j < rdf.shape[0]:
            c = rdf['ts_code'][j]
            vol = rdf['vol'][j]
            h = history_dict[c]
            h = h[h['trade_date'] == int(date)].reset_index(drop=True)
            if h.shape[0] > 0:
                s += vol * 100 * h['close'][0]
            else:
                print('Unexpected')
            j += 1
        print('[%d] account: %lf, stock value: %lf, total: %lf' %(date, account, s, s + account))

        i -= 1

def stock_realtime_simulate():
    tufo = tuf.TushareFetcher()
    tufo.fetch_data(offset=1,days=30)
    rt = rsf.RtSnowballFetcher('601168.SH')
    rt.fetch_data()
    date = rt.df['trade_date'][0].split()[0]
    strategy = 'cat'
    code_list = tufo.code_list
    if len(sys.argv) > 1:
        st = sys.argv[1]
        if st.startswith('strategy='):
            strategy = st.split('=')[1]
        else: 
            code_list = st.split(",")
    #while
    stp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tmp = '---- Begin %s ----' % stp
    f_info = ""
    send_info = ""
    trace_info = ""
    f_info_l = [f_info, send_info, trace_info]
    print(tmp)
    f_info_l[0] += tmp + '<br>\n'
    f_info_l[1] += tmp + '<br>'
    i = 0
    batch = 150
    rdf = stock_utils.new_trace_df()
    invalid = 0
    while i < len(code_list):
        start = i
        end = i + batch if i + batch < len(code_list) else  len(code_list)
        invalid += realtime_handle(start, end, code_list, tufo, f_info_l, rdf, strategy=strategy)
        i = i + batch
    stp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tmp = '---- All Done %s with %d invalid ----' % (stp, invalid)
    print(tmp)
    f_info_l[0] += tmp + '<br>\n'
    f_info_l[1] += tmp + '<br>'
    with open('index.html', 'w+') as f:
        f.write(f_info_l[0])
    with open('data/mock_trade/' + date, 'w+') as f:
        f.write(f_info_l[2])
    rdf.to_csv('data/mock_trade/' + date + ".csv")
    params = {
      "token" : "b0b164534ed046bcbd0719fa93954d54",
      "title" : "“猫周期”量化 选股推送",
      "content" : f_info_l[1],
      "topic" : "1",
      "template" : "html",
    }
    requests.get(url = send_url, params = params)
    

if __name__=="__main__":
    stock_realtime_simulate()
    #if len(sys.argv) > 1:
    #    stock_history_simulate("20230616", 30, up=float(sys.argv[1]), low=1.0)
    #else:
    #    stock_history_simulate("20230711", 60, up=3, low=1)
