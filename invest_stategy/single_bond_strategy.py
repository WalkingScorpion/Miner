
class SingleBondStrategy(object):
    bcoe = 0.2
    scoe = 0.2
    bthreshold = 3
    sthreshold = 3
    def __init__(self, fund_map, init):
        self.fm = fund_map
        self.init = init

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
                if (b_count >= SingleBondStrategy.bthreshold):
                    ex_share = now_share if now_share < SingleBondStrategy.bcoe * self.init \
                                   else int( SingleBondStrategy.bcoe * now_share)
                    ex_share = self.init if ex_share <= 0 else ex_share
                    fund.buy(row, ex_share)
                if (s_count >= SingleBondStrategy.sthreshold):
                    ex_share = now_share if now_share < SingleBondStrategy.scoe * self.init \
                                   else int( SingleBondStrategy.scoe * now_share)
                    ex_share = now_share if ex_share <  SingleBondStrategy.scoe * self.init else ex_share
                    fund.sell(row, ex_share)
                row = row - 1

    def show(self):
        pass
