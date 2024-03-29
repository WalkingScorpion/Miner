from datetime import datetime
from utils import stock_utils
import pandas as pd


class CatStrategy(object):
    def __init__(self, history, realtime):
        self.history = history
        self.realtime = realtime
        self.his = history
        if self.realtime is not None:
            rt_date = self.realtime['trade_date'][0].split()[0]
            his_date = self.history['trade_date'][0]
            if  (rt_date == str(his_date)):
                self.history.drop([0], inplace=True)
            self.his = pd.concat([self.realtime, self.history]).reset_index(drop=True)

    def fill_df(self, rdf, row, sell, td, td_gap):
        price = rdf['buy'][row]
        profile = sell / price * 100 - 100
        rdf.loc[row, 'sell_date'] = str(td)
        rdf.loc[row, 'sell'] = sell
        rdf.loc[row, 'profile'] = profile
        rdf.loc[row, 'potd'] = profile / (td_gap + 1)
        b = datetime.strptime(str(rdf['buy_date'][row]).split()[0], '%Y%m%d')
        s = datetime.strptime(str(rdf['sell_date'][row]).split()[0], '%Y%m%d')
        rdf.loc[row, 'pond'] = profile / (s - b).days
        return profile

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
        if box_pct < 0.015 or box_pct > 0.045:
            return False, "[box profile unexcepted. box percentt %lf]" % box_pct
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

    def sell_strategy(self, row, rdf, period=3):
        his = self.his
        i = 0
        drop_list = []
        while i < his.shape[0]:
            n = int(str(his['trade_date'][i]).split()[0])
            b = int(rdf['buy_date'][row].split()[0])
            if n <= b:
                drop_list.append(i)
            i += 1
        his.drop(drop_list)
        his.reset_index(drop=True, inplace=True)
        info = his['ts_code'][0]
        if his.shape[0] < period:
            return "Not Ready"
        s = his.shape[0]
        sell = his['high'][s - 1]
        i = 1
        while i < period - 1:
            index = s - 1 - i
            n = int(str(his['trade_date'][index]).split()[0])
            if his['high'][index] > sell:
                profile = self.fill_df(rdf, row, sell, n, i)
                return " %s | %f | %f" % (n, sell, profile)
            i += 1
        return "Failed"
        

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
