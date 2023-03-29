from datetime import datetime

class ExRecord(object):
    def __init__(self, date, share, nav):
        self.share = share
        self.date = date
        self.nav = nav

class FundBase(object):
    date_format = '%Y-%m-%d'
    def __init__(self, dataframe, detail=False):
        self.detail = detail
        self.df = dataframe
        self.profile = 0.0
        self.current = 0.0
        self.record = []

    def buy_fee_rule(self, current):
        return 0.0

    def sell_fee_rule(self, current, gap):
        return 0.0

    def buy(self, row, share):
        nav = self.df['acc_nav'][row]
        date = self.df['date'][row]
        current = nav * share
        self.profile = self.profile - self.buy_fee_rule(current)
        diff = current + self.buy_fee_rule(current)
        self.current = self.current - diff
        self.push_share(date, share, nav)
        if (self.detail):
            print('%s:\t-%lf\t%lf\t%ld\t%lf' % (date, diff, self.profile, self.get_share(), nav))
        
    def sell(self, row, share):
        nav = self.df['acc_nav'][row]
        date = self.df['date'][row]
        current = nav * share
        self.profile = self.profile - self.calc_sell_fee(date, share, nav)
        self.profile = self.profile + self.calc_profile(share, nav)
        diff = current - self.calc_sell_fee(date, share, nav)
        self.current = self.current + diff
        self.pop_share(share)
        if (self.detail):
            print('%s:\t%lf\t%lf\t%ld\t%lf' % (date, diff, self.profile, self.get_share(), nav))

    def calc_profile(self, share, nav):
        p = 0.0
        i = 0
        left = share
        while (left > 0 and i < len(self.record)):
            diff = 0
            if (left > self.record[i].share):
                diff = self.record[i].share
            else:
                diff = left
            p = p + (nav - self.record[i].nav) * diff
            left = left - diff
            i = i + 1
        if (len(self.record) <= i and left > 0):
            print('Error Exchange: No Enough Share. Left: %ld' % left)
        return p

    def calc_sell_fee(self, date, share, nav):
        fee = 0.0
        i = 0
        left = share
        e = datetime.strptime(date, FundBase.date_format)
        while (left > 0 and i < len(self.record)):
            s = datetime.strptime(self.record[i].date, FundBase.date_format)
            interval = e - s
            current = 0.0
            diff = 0
            if (left > self.record[i].share):
                diff = self.record[i].share
            else:
                diff = left
            current = nav * diff
            fee = fee + self.sell_fee_rule(current, interval.days)
            left = left - diff
            i = i + 1
        if (len(self.record) <= i and left > 0):
            print('Error Exchange: No Enough Share. Left: %ld' % left)
        return fee
        

    def push_share(self, date, share, nav):
        self.record.append(ExRecord(date, share, nav))

    def pop_share(self, share):
        left = share
        while (left > 0 and len(self.record) > 0):
            diff = 0
            if (left > self.record[0].share):
                diff = self.record[0].share
                left = left - self.record[0].share
                self.record.pop(0)
            else:
                self.record[0].share = self.record[0].share - left
                left = 0
            if (left > self.record[0].share):
                left = left - self.record[0].share
                self.record.pop(0)
            else:
                self.record[0].share = self.record[0].share - left
                left = 0
        if (len(self.record) == 0 and left > 0):
            print('Error Pop: No Enough Share. Left: %ld' % left)

    def get_share(self):
        s = 0
        for r in self.record:
            s = s + r.share
        return s
        
    def show(self):
        print('current: %lf' % (self.current))
        print('profile: %lf' % (self.profile))
        total = self.df.shape[0]
        if (total > 0):
            nav = self.df.iloc[0]['acc_nav']
            value = nav * self.get_share()
            print('value: %lf' % (value))


