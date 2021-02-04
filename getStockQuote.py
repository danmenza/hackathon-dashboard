import requests
import datetime

import pandas as pd
from urllib.request import Request, urlopen
import json
from pandas.io.json import json_normalize
import time


def getStockQuote(ticker, backup_df):
    proxies = {'http': 'proxy_if_needed',
               'https': 'proxy_if_needed'}
    try:
        response = requests.get("https://api.iextrading.com/1.0/tops?symbols={}".format(ticker), proxies=proxies)
        lastQuote = response.json()
        quotePrice = lastQuote[0]['lastSalePrice']
        quoteTime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastQuote[0]['lastSaleTime'] / 1000)))
        quoteDate = " "
        return quoteDate, quoteTime, quotePrice
    except:
        try:
            response = requests.get("https://api.iextrading.com/1.0/stock/{}/chart/1d".format(ticker) , proxies=proxies)
            lastQuote = response.json()
            quotePrice = lastQuote[-1]['close']
            quoteDate = lastQuote[-1]['date']
            quoteDate = datetime.datetime.strptime(quoteDate, '%Y%m%d')
            quoteDate = str(quoteDate.month)+"/"+str(quoteDate.day)+"/"+str(quoteDate.year)
            quoteTime = lastQuote[-1]['label']
        except:
            last_index = backup_df['datetime'].argmax()
            quotePrice = backup_df.loc[last_index]['Close']
            quoteTime = backup_df[last_index]['Time']
            quoteDate = backup_df[last_index]['Date']
            print("Neither worked")

        return quoteDate, quoteTime, quotePrice