from datetime import datetime
from utils import stock_utils
from stock_strategy.cat_strategy import CatStrategy
import pandas as pd


class XStrategy(CatStrategy):
    def __init__(self, history, realtime, sell_base=0.5):
        CatStrategy.__init__(self, history, realtime)
        self.sb = sell_base

    def sell_strategy(self, code, buy_date, price, period=3, rdf=None):
        rt_date = self.realtime['trade_date'][0].split()[0]
        his_date = self.history['trade_date'][0]
        if  (rt_date == str(his_date)):
            self.history = self.history.drop([0])
        his = pd.concat([self.realtime, self.history]).reset_index(drop=True)
        i = 0
        drop_list = []
        while i < his.shape[0]:
            n = int(str(his['trade_date'][i]).split()[0])
            b = int(buy_date)
            if n <= b:
                drop_list.append(i)
            i += 1
        his = his.drop(drop_list)
        info = his['ts_code'][0]
        s = his.shape[0]
        base_coef = self.sb / 100
        i = 0
        while i < period and 0 <= s - 1 - i:
            index = s - 1 - i
            n = int(str(his['trade_date'][index]).split()[0])
            #sell = (1 + base_coef * (i + 1)) * price
            sell = (1 + base_coef) * price
            if his['high'][index] > sell:
                profile = sell / price * 100 - 100
                if rdf is not None:
                    p = [rdf[rdf.ts_code == code].index.tolist()[0]]
                    rdf.loc[p, 'sell_date'] = str(n)
                    rdf.loc[p, 'sell'] = sell
                    rdf.loc[p, 'profile'] = profile
                    rdf.loc[p, 'potd'] = profile / (i + 1)
                    b = datetime.strptime(rdf['buy_date'][p[0]].split()[0], '%Y%m%d')
                    s = datetime.strptime(rdf['sell_date'][p[0]].split()[0], '%Y%m%d')
                    rdf.loc[p, 'pond'] = profile / (s - b).days
                return " %d | %f | %f" % (n, sell, profile)
            i += 1
        if his.shape[0] < period:
            return "Not Ready"
        else:
            sell = his['close'][index]
            profile = sell / price * 100 - 100
            if rdf is not None:
                p = [rdf[rdf.ts_code == code].index.tolist()[0]]
                rdf.loc[p, 'sell_date'] = str(n)
                rdf.loc[p, 'sell'] = sell
                rdf.loc[p, 'profile'] = profile
                rdf.loc[p, 'potd'] = profile / (i + 1)
                b = datetime.strptime(rdf['buy_date'][p[0]].split()[0], '%Y%m%d')
                s = datetime.strptime(rdf['sell_date'][p[0]].split()[0], '%Y%m%d')
                rdf.loc[p, 'pond'] = profile / (s - b).days
            return " %d | %f | %f" % (n, sell, sell / price * 100 - 100)
        

