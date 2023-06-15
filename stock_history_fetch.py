import sys
import requests
import time
import datetime
import os
from data_fetcher import rt_snowball_fetcher as rsf
from data_fetcher import tushare_fetcher as tuf

if __name__=="__main__":
    tuf = tuf.TushareFetcher()
    tuf.fetch_data(offset=0,days=750)
