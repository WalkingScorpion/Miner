import requests
import json
import datetime
import time
import sys
import pandas as pd

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

    def build_dataframe(self, jstr):
        col_name = ['ts_code', 'rt_timestamp', 'rt_open', 'rt_high',
            'rt_low', 'rt_current', 'rt_pre_close', 'rt_change', 'rt_pct_chg',
            'rt_vol', 'rt_amount']
        jdat = json.loads(jstr)
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
            pre_close_list.append(1.0 * (int(cur * 100) - int(chg * 100)) / 100)
            vol_list.append(n['volume'])
            amount_list.append(n['amount'])
            open_list.append(n['open'])
            high_list.append(n['high'])
            low_list.append(n['low'])
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
        df = pd.DataFrame(data).T
        df.columns = col_name
        return df

    def fetch_data(self):
        millis = (int(time.time())) * 1000
        params = {
          "symbol" : self.code, #"SH601168"
        }
        response = requests.get(url = RtSnowballFetcher.url, params = params, headers = RtSnowballFetcher.header)
        df = self.build_dataframe(response.text)
        return (df)

if __name__=="__main__":
    f = RtSnowballFetcher(sys.argv[1])
    df = f.fetch_data()
    print (df)
