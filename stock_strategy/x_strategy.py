from datetime import datetime
from utils import stock_utils
from stock_strategy.cat_strategy import CatStrategy
import pandas as pd


class XStrategy(CatStrategy):
    def __init__(self, history, realtime, sell_base=0.5, low_r=1):
        CatStrategy.__init__(self, history, realtime)
        self.sb = sell_base
        self.lr = low_r

    def strategy_level0(self, his, rdf):
        td = his['trade_date'][0]
        op = his['open'][0]
        cl = his['close'][0]
        hi = his['high'][0]
        if (op == None):
            return False, "[Data invalid.]"
        box_pct = (cl - op) / op
        k5 = [
            stock_utils.get_k(his, 5),
            stock_utils.get_k(his, 5, 3),
        ]
        k10 = [
            stock_utils.get_k(his, 10),
            stock_utils.get_k(his, 10, 3),
        ]
        k20 = [
            stock_utils.get_k(his, 20),
            stock_utils.get_k(his, 20, 3),
        ]
       
        b0, _, _ = stock_utils.get_boll(his, 20)
        b1, _, _ = stock_utils.get_boll(his, 20, 1)
        
        if cl < b0 or his['close'][1] < b1:
            return False, "[close price less than boll(20) mid. close %lf boll %lf]" % (cl, b0)
        if abs(op - k5[0]) > (0.015 * k5[0]):
            return False, "[open price vs k5 gap more than 0.015. open %lf k5 %lf]" % (op, k5[0])
        if k5[0] < k5[1] or k10[0] < k10[1] or k20[0] < k20[1]:
            return False, "[Kx decline. k5 %lf->%lf k10 %lf->%lf k20 %lf->%lf]" % (k5[1], k5[0], k10[1], k10[0], k20[1], k20[0])
        if box_pct < 0.005 or box_pct > 0.035:
            return False, "[box profile unexcepted. box percentt %lf]" % box_pct
        if (hi - cl) < (cl - op):
                return False, ''
        if (hi - op) / op > 0.096:
            return False, "[Highest price is too high. highest %lf open %lf]" % (hi, op)
        if (
            (not self.strategy_evol(his)) or
            his['vol'][1] < his['vol'][3] or
            his['vol'][2] > his['vol'][3] or
            his['vol'][1] < his['vol'][2]):
            return False, "[Volume not continue increase]"
        info = '| %s | %lf |' % (td, cl)
        rdf.loc[len(rdf.index)] = [his['ts_code'][0], td, cl, "", 0, "", 0.0, 0.0, 0.0, 0.0]
        return True, info
        
    def strategy_tor(self, his):
        if 'tor' in his:
            tor = his['tor'][0]
            return 5 < tor < 10
        else:
            return False

    def strategy_evol(self, his):
        tsl = str(his['trade_date'][0]).split()
        if len(tsl) > 1:
            ts = tsl[1]
            sec = stock_utils.get_trade_second(ts)
            e_vol = 1.0 * his['vol'][0]  / sec * 3600 * 4
            return e_vol > his['vol'][1]
        else:
            return his['vol'][0] > his['vol'][1]


    def strategy_vr(self, his):
        vr = stock_utils.get_volume_ratio(his)
        return vr > 1

    def buy_strategy(self, rdf):
        his = self.his
        match_level0, info0 = self.strategy_level0(his, rdf)
        if match_level0:
            if self.strategy_tor(his):
                rdf.loc[rdf.shape[0] - 1, 'tags'] += " [tor]"
                info0 += " [tor]"
            if self.strategy_vr(his):
                rdf.loc[rdf.shape[0] - 1, 'tags'] += " [vr]"
                info0 += " [vr]"
        return match_level0, info0

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
        

