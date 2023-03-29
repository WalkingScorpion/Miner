import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd

class EastMoneyFetcher(object):
    url = 'https://fundf10.eastmoney.com/F10DataApi.aspx'
    per = str(49)
    ftype = 'lsjz'

    def __init__(self, code, sdate, edate):
        self.code = str(code)
        self.sdate = str(sdate)
        self.edate = str(edate)
        self.date = []
        self.nav = []
        self.acc_nav = []
        self.ratio = []

    def reset_data(self):
        self.date.clear()
        self.nav.clear()
        self.acc_nav.clear()
        self.ratio.clear()
        

    def get_page_num(self):
        params = {
          "type" : EastMoneyFetcher.ftype,
          "code" : self.code, #"110036"
          "sdate" : self.sdate, #"2020-01-01",
          "edate" : self.edate, #"2023-03-24",
          "per" : EastMoneyFetcher.per,
        }
        response = requests.get(url = EastMoneyFetcher.url, params = params)
        body = re.findall(r'{(.*)}', response.text)[0]
        dic = {}
        for line in  body.split(","):
            item = line.split(":")
            dic[item[0].strip()] = item[1]
        #record_num = int(dic['records'])
        page_num = int(dic['pages'])
        return page_num

    def get_page_data(self, pageid):
        params = {
          "type" : EastMoneyFetcher.ftype,
          "code" : self.code, #"110036"
          "sdate" : self.sdate, #"2020-01-01",
          "edate" : self.edate, #"2023-03-24",
          "per" : EastMoneyFetcher.per,
          "page" : str(pageid), 
        }
        response = requests.get(url = EastMoneyFetcher.url, params = params)
        body = re.findall(r'{(.*)}', response.text)[0]
        dic = {}
        for line in  body.split(","):
            item = line.split(":")
            dic[item[0].strip()] = item[1]
        content = dic['content']
        tbody = re.findall(r'"(.*)"', content)[0]
        root = ET.XML(tbody)  # Parse XML
        for c1 in root:
            if (c1.tag == 'tbody'):
                for c2 in c1:
                    if (c2.tag == 'tr'):
                        i = 0
                        for c3 in c2:
                            if (c3.tag == 'td'):
                                if (i == 0):
                                    self.date.append(c3.text)
                                if (i == 1):
                                    self.nav.append(float(c3.text))
                                if (i == 2):
                                    self.acc_nav.append(float(c3.text))
                                if (i == 3):
                                    s = c3.text
                                    if s is None:
                                        s = '0.00%'
                                    self.ratio.append(float(s.split('%')[0]))
                                i = i + 1

    def fetch_data(self):
        page_num = self.get_page_num()
        i = 1;
        while (i <= page_num):
            self.get_page_data(i)
            i = i + 1

    def build_dataframe(self):
        col_name = ['date', 'nav', 'acc_nav', 'ratio']
        data = []
        data.append(self.date)
        data.append(self.nav)
        data.append(self.acc_nav)
        data.append(self.ratio)
        df = pd.DataFrame(data).T
        df.columns = col_name
        return df

