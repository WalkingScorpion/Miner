from datetime import datetime
from utils import stock_utils
import pandas as pd


class CatStrategy(object):
    def __init__(self, history, realtime):
        self.history = history
        self.realtime = realtime

    def strategy_level0(self, his):
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
        if box_pct < 0.025 or box_pct > 0.055:
            return False, "[box profile unexcepted. box percentt %lf]" % box_pct
        if (hi - op) / op > 0.096:
            return False, "[Highest price is too high. highest %lf open %lf]" % (hi, op)
        if (
            his['vol'][1] < his['vol'][2] or
            his['vol'][2] < his['vol'][3]):
            return False, "[Volume not continue increase]"
        info = '[%s] [%lf]' % (td, cl)
        return True, info
        
    def strategy_tor(self, his):
        tor = his['tor'][0]
        return 5 < tor < 10

    def strategy_evol(self, his):
        ts = his['trade_date'][0].split()[1]
        sec = stock_utils.get_trade_second(ts)
        e_vol = 1.0 * his['vol'][0]  / sec * 3600 * 4
        return e_vol > his['vol'][1]

    def strategy_vr(self, his):
        vr = stock_utils.get_volume_ratio(his)
        return vr > 1

    def run_strategy(self):
        rt_date = self.realtime['trade_date'][0].split()[0]
        his_date = self.history['trade_date'][0]
        if  (rt_date == str(his_date)):
            self.history = self.history.drop([0])
        his = pd.concat([self.realtime, self.history]).reset_index(drop=True)
        match_level0, info0 = self.strategy_level0(his)
        if match_level0:
            if self.strategy_tor(his):
                info0 += " [tor]"
            if self.strategy_evol(his):
                info0 += " [evol]"
            if self.strategy_vr(his):
                info0 += " [vr]"
        return match_level0, info0
