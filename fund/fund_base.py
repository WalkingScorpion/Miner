from datetime import datetime

class ExRecord(object):
    def __init__(self, date, share, nav):
        self.share = share
        self.date = date
        self.nav = nav

class FundBase(object):
    date_format = '%Y-%m-%d'
    def __init__(self, detail=False):
        self.code = None
        self.detail = detail
        self.df = None
        self.profile = 0.0
        self.current = 0.0
        self.fee = 0.0
        self.current_x_day = 0.0
        self.record = []

    def set_code(self, code):
        self.code = code

    def bind_data(self, dataframe):
        self.df = dataframe

    def clear(self):
        self.code = None
        self.df = None
        self.profile = 0.0
        self.current = 0.0
        self.fee = 0.0
        self.current_x_day = 0.0
        self.record = []
 

    def buy_fee_rule(self, current):
        return 0.0

    def sell_fee_rule(self, current, gap):
        return 0.0

    def buy(self, row, share):
        nav = self.df['acc_nav'][row]
        date = self.df['date'][row]
        current = nav * share
        fee = self.buy_fee_rule(current)
        self.fee = self.fee + fee
        self.profile = self.profile - fee
        diff = current + fee
        self.current = self.current - diff
        self.push_share(date, share, nav)
        if (self.detail):
            print('%s:\t-%ld\t%lf\t-%lf\t%lf\tfinal:%ld' % (date, share, nav, current, fee, self.get_share()))
        
    def sell(self, row, share):
        nav = self.df['acc_nav'][row]
        date = self.df['date'][row]
        current = nav * share
        fee = self.calc_sell_fee(date, share, nav)
        self.fee = self.fee + fee
        self.profile = self.profile - fee
        self.current_x_day = self.current_x_day + self.calc_current_x_day(date, share)
        self.profile = self.profile + self.calc_profile(share, nav)
        diff = current - fee
        self.current = self.current + diff
        self.pop_share(share)
        if (self.detail):
            print('%s:\t%ld\t%lf\t%lf\t%lf\tfinal:%ld' % (date, share, nav, current, fee, self.get_share()))

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
        if (self.detail):
            print('\tprofile %lf' % (p))
        return p

    def calc_current_x_day(self, date, share):
        fee = 0.0
        i = 0
        left = share
        e = datetime.strptime(date, FundBase.date_format)
        current_x_day = 0.0
        while (left > 0 and i < len(self.record)):
            s = datetime.strptime(self.record[i].date, FundBase.date_format)
            interval = e - s
            current = 0.0
            diff = 0
            nav = self.record[i].nav
            if (left > self.record[i].share):
                diff = self.record[i].share 
            else:
                diff = left
            current_x_day = current_x_day + nav * diff * interval.days
            if (self.detail):
                print('\tcurrent:%lf\tdays:%ld' % (nav * diff, interval.days))
            left = left - diff
            i = i + 1
        if (len(self.record) <= i and left > 0):
            print('Error Calc: No Enough Share. Left: %ld' % left)
        return current_x_day

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

    def get_nature_ratio(self):
        total = self.df.shape[0]
        if (total <= 0):
            return 0.0
        enav = self.df.iloc[0]['acc_nav']
        snav = self.df.iloc[total - 1]['acc_nav']
        d = 1.0 * (enav - snav) / snav
        e = datetime.strptime(self.df.iloc[0]['date'], FundBase.date_format)
        s = datetime.strptime(self.df.iloc[total - 1]['date'], FundBase.date_format)
        interval = e - s
        return d / interval.days * 365

    def get_vprofile(self):
        total = self.df.shape[0]
        if (total <= 0):
            return 0.0
        nav = self.df.iloc[0]['acc_nav']
        v = 0.0
        for r in self.record:
            v = v + (nav - r.nav) * r.share
        return v

    def get_equal_current_on_year(self):
        total = self.df.shape[0]
        if (total <= 0):
            return 0.0
        cxd = self.current_x_day + \
          self.calc_current_x_day(self.df.iloc[0]['date'], self.get_share())
        return cxd / 365
    

    def get_manual_ratio(self):
        coy = self.get_equal_current_on_year()
        if (coy <= 0.0):
            return 0.0;
        p = self.profile + self.get_vprofile()
        return p / coy

    def show(self):
        total = self.df.shape[0]
        if (total <= 0):
            return
        es = self.df.iloc[0]['date']
        ss = self.df.iloc[total - 1]['date']
        e = datetime.strptime(self.df.iloc[0]['date'], FundBase.date_format)
        s = datetime.strptime(self.df.iloc[total - 1]['date'], FundBase.date_format)
        interval = e - s
        nav = self.df.iloc[0]['acc_nav']
        print('[ %s ]' % self.code)
        print('From %s To %s' % (ss, es))
        print('current on period: %lf, general profile: %lf, fee: %lf' % (self.get_equal_current_on_year() * 365 / interval.days, \
            self.profile + self.get_vprofile(), self.fee))
        print('nature ratio: %lf\nmanual ratio: %lf' % (self.get_nature_ratio(), self.get_manual_ratio()))


