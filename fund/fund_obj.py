from fund.fund_base import FundBase

class F110035(FundBase):
    def buy_fee_rule(self, current):
        fee = 0.0
        if (current < 0.0):
            fee = 0.0
        elif (current < 1e6):
            fee = 0.08e-2 * current
        elif (current < 5e6):
            fee = 0.04e-2 * current
        elif (current < 10e6):
            fee = 0.0000 * current
        else:
            fee = 1000.0
        return fee

    def sell_fee_rule(self, current, gap):
        fee = 0.0
        if (gap < 0.0):
            fee = 0.0
        elif (gap < 7):
            fee = 1.5e-2 * current
        elif (gap < 30):
            fee = 0.75e-2 * current
        elif (gap < 365):
            fee = 0.1e-2 * current
        elif (gap < 730):
            fee = 0.05e-2 * current
        else:
            fee = 0.0
        return fee

class F007230(FundBase):
    def buy_fee_rule(self, current):
        fee = 0.0
        return fee

    def sell_fee_rule(self, current, gap):
        fee = 0.0
        if (gap < 0):
            fee = 0.0
        elif (gap < 7):
            fee = 1.5e-2 * current
        elif (gap < 30):
            fee = 0.5e-2 * current
        else:
            fee = 0.0
        return fee

