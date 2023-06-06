import tushare as ts
import time
import sys
import datetime
import pandas as pd

class TushareFetcher(object):
    def __init__(self, code):
        self.code = str(code)

    def fetch_one(self, code):
        pro = ts.pro_api()
        d = datetime.timedelta(days=60)
        e = datetime.datetime.now()
        s = e - d
        succ = False
        while (not succ):
            try:
                #df = pro.daily(trade_date='20230605')
                df = ts.pro_bar(ts_code=code, adj='qfq',
                    start_date=s.strftime("%Y%m%d"),
                    end_date=e.strftime("%Y%m%d"),
                    #ma=[5, 10, 20, 30],
                    #factors=['tor', 'vr'],
                    offset=0, limit=30)
                succ = True
            except OSError as err:
                 print(err)
                 time.sleep(5)
        return df

    def fetch_data(self):
        l = []
        code_list = self.code.split(",")
        for c in code_list:
            d = self.fetch_one(c)
            l.append(d)
        r = pd.concat(l)
        return r

if __name__=="__main__":
    f = TushareFetcher(sys.argv[1])
    df = f.fetch_data()
    print (df)
