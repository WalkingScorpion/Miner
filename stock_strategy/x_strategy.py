from datetime import datetime
from utils import stock_utils
from stock_strategy.cat_strategy import CatStrategy
import pandas as pd


class XStrategy(CatStrategy):
    def __init__(self, history, realtime, sell_base=0.5, low_r=1):
        CatStrategy.__init__(self, history, realtime)
        self.sb = sell_base
        self.lr = low_r


    def sell_strategy(self, row, rdf, period=3):
        his = self.his
        i = 0
        drop_list = []
        b = int(str(rdf['buy_date'][row]).split()[0])
        while i < his.shape[0]:
            n = int(str(his['trade_date'][i]).split()[0])
            if n <= b:
                drop_list.append(i)
            i += 1
        his.drop(drop_list, inplace=True)
        his.reset_index(drop=True, inplace=True)
        info = his['ts_code'][0]
        s = his.shape[0]
        base_coef = self.sb / 100
        lr = self.lr / 100
        price = rdf['buy'][row]
        i = 0
        while i < period and 0 <= s - 1 - i:
            index = s - 1 - i
            n = int(str(his['trade_date'][index]).split()[0])
            #sell = (1 + base_coef * (i + 1)) * price
            sell = (1 + base_coef) * price
            if his['high'][index] > sell:
                profile = self.fill_df(rdf, row, sell, n, i)
                return " %d | %f | %f" % (n, sell, profile)
            if his['low'][index] < price * (1 - lr):
                sell = price * (1 - lr)
                profile = self.fill_df(rdf, row, sell, n, i)
                return " %d | %f | %f" % (n, sell, profile)
            i += 1
        if his.shape[0] < period:
            return "Not Ready"
        else:
            sell = his['close'][index]
            profile = self.fill_df(rdf, row, sell, n, period)
            return " %d | %f | %f" % (n, sell, profile)
        

