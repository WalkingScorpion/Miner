import requests
import json
import datetime
import time
import sys
import pandas as pd
import pysnowball as ball

class RtSnowballFetcher(object):
    url = 'https://stock.xueqiu.com/v5/stock/realtime/quotec.json'
    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62"
    }

    def __init__(self, code):
        origin = code.split(',')
        new = []
        for c in origin:
            p = c.split('.')
            new.append(p[1] + p[0])
        self.code = ','.join(new)
        self.df = None

    def extract_snapshot(self, code):
        r = self.df[self.df.ts_code == code].reset_index(drop=True)
        return r

    def build_dataframe(self, jdat):
        col_name = ['ts_code', 'trade_date', 'open', 'high',
            'low', 'close', 'pre_close', 'change', 'pct_chg',
            'vol', 'amount', 'tor']
        timestamp_list = []
        code_list = []
        current_list = []
        pre_close_list = []
        percent_list = []
        change_list = []
        vol_list = []
        amount_list = []
        open_list = []
        high_list = []
        low_list = []
        tor_list = []
        for n in jdat['data']:
            chg = n['chg']
            if chg == None:
                continue
            t = int(n['timestamp'] / 1000)
            d = datetime.datetime.strftime(datetime.datetime.fromtimestamp(t), '%Y%m%d %H:%M:%S')
            timestamp_list.append(d)
            s = n['symbol']
            t = s[0:2]
            c = s[2:]
            code = c + "." + t
            code_list.append(code)
            cur = n['current']
            current_list.append(cur)
            percent_list.append(n['percent'])
            change_list.append(chg)
            pre_close_list.append(n['last_close'])
            vol_list.append(1.0 * n['volume'] / 100) # trasfer to tushare standard
            amount_list.append(1.0 * n['amount'] / 1000) # trasfer to tushare standard
            open_list.append(n['open'])
            high_list.append(n['high'])
            low_list.append(n['low'])
            tor_list.append(n['turnover_rate'])
        data = []
        data.append(code_list)
        data.append(timestamp_list)
        data.append(open_list)
        data.append(high_list)
        data.append(low_list)
        data.append(current_list)
        data.append(pre_close_list)
        data.append(change_list)
        data.append(percent_list)
        data.append(vol_list)
        data.append(amount_list)
        data.append(tor_list)
        df = pd.DataFrame(data).T
        df.columns = col_name
        return df

    def fetch_data(self):
        ball.set_token('xq_a_token=71c23ae269a6dc16cd704cdce4529b613425cdd2;')
        dat = ball.quotec(self.code)
        self.df = self.build_dataframe(dat)

if __name__=="__main__":
    f = RtSnowballFetcher(sys.argv[1])
    df = f.fetch_data()
    print (df)
