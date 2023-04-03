from datetime import datetime
from fund import fund_base as fb

class EasyStrategy(object):
    def __init__(self, init, coe = 0.2, thres = 5):
        self.fm = None
        self.name = None
        self.init = init
        #self.bcoe = coe
        self.bcoe = 0.25
        self.scoe = coe
        self.bthreshold = thres
        self.sthreshold = thres

    def bind_fund_map(self, fund_map):
        self.fm = fund_map

    def set_name(self, name):
        self.name = name

    def run_strategy(self):
        for (code, fund) in self.fm.items():
            df = fund.df
            total = df.shape[0]
            b_count = 0
            s_count = 0
            row = total - 1
            while (row >= 0):
                today = df.iloc[row]
                if today['ratio'] < 0.0:
                    b_count = b_count + 1
                    s_count = 0;
                else:
                    b_count = 0;
                    s_count = s_count + 1
                nav = today['acc_nav']
                now_share = fund.get_share()
                init_share = int(1.0 * self.init / nav)
                if (b_count >= self.bthreshold):
                    ex_share = now_share if now_share < self.bcoe * init_share \
                                   else int(self.bcoe * now_share)
                    ex_share = init_share if ex_share <= 0 else ex_share
                    fund.buy(row, ex_share)
                if (s_count >= self.sthreshold):
                    ex_share = now_share if now_share < self.scoe * init_share \
                                   else int(self.scoe * now_share)
                    ex_share = now_share if ex_share < self.scoe * init_share else ex_share
                    fund.sell(row, ex_share)
                row = row - 1

    def show(self):
        print('##### %s #####' % self.name)
        for fund in self.fm.values():
            fund.show()
