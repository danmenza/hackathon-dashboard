import requests
import pandas as pd
import math
import pytz
import dateutil.parser
import datetime as dt
from sec import SEC
import json
import time
import os

def getLocalTime(isotime_string):
    est = pytz.timezone('US/Eastern')
    x = dateutil.parser.parse(isotime_string).astimezone(est)
    timeLocal = dt.datetime(x.year,x.month,x.day, x.hour, x.minute)
    return timeLocal

def getNews(ticker):
    cachedDataExists = True

    try:
        df = pd.read_pickle("cachedData/{}.pkl".format(ticker))
    except:
        cachedDataExists = False
        print("No File")

    if cachedDataExists == True:
        print("Got data")
        currentUnixTime = time.time()
        fileCreateTime = os.path.getctime("cachedData/{}.pkl".format(ticker))

        if (currentUnixTime - 60 * 60 * 4) < fileCreateTime:
            return df

    # Get number of articles for ticker in past 30 days
    url = ('https://newsapi.org/v2/everything?'
           'q={}&'
           'language=en&'
           'from=2018-03-23&'
           'sortBy=popularity&'
           'domains=seekingalpha.com, marketwatch.com&'
           'apiKey=your_api_key'.format(ticker))

    proxies = {'http':'proxy_if_needed',
       'https':'proxy_if_needed'}

    response = requests.get(url, proxies=proxies)
    numArticles = response.json()['totalResults']

    articleTitles = []
    articleURLS = []
    articleTimes = []

    # Loop through pages, appending article info to existing lists
    for currentPage in range(1, math.ceil(numArticles / 100) + 1):
        #print(currentPage)
        pageURL = ('https://newsapi.org/v2/everything?'
                   'q={}&'
                   'language=en&'
                   'from=2018-03-23&'
                   'sortBy=popularity&'
                   'pageSize=100&'
                   'page={}&'
                   'domains=seekingalpha.com, marketwatch.com&'
                   'apiKey=your_api_key'.format(ticker, currentPage))
        pageResponse = requests.get(pageURL, proxies=proxies)
        pageArticles = pageResponse.json()['articles']

        # print(len(pageArticles))

        pageTitles = [x['title'] for x in pageArticles]
        pageURLS = [x['url'] for x in pageArticles]
        pageTimes = [x['publishedAt'] for x in pageArticles]

        articleTitles = articleTitles + pageTitles
        articleURLS = articleURLS + pageURLS
        articleTimes = articleTimes + pageTimes

    # Create dataframe from lists
    d = {'publishedAt': articleTimes, 'Title': articleTitles, 'URL': articleURLS}
    df = pd.DataFrame(data=d)

    # Convert string to date, UTC to Eastern
    df['localTime'] = df['publishedAt'].apply(lambda x: getLocalTime(x))
    df['Origin'] = 'News source'

    ###### Get SEC reports
    with open('clientList.json') as f:
        client_list = json.load(f)

    ticker_map = {v['ticker']: v['cik'] for k, v in client_list.items()}
    secFilings = SEC(ticker_map[ticker]).df
    secFilings['updated'] = secFilings['updated'].apply(lambda x: x.replace(tzinfo=None))
    secFilings.rename(columns={'filing_type': 'Title', 'updated': 'localTime', 'url': 'URL'}, inplace=True)
    secFilings['publishedAt'] = 'ignore this filler string'
    secFilings['Origin'] = 'SEC'
    df = df.append(secFilings, ignore_index=True)

    df.to_pickle("cachedData/{}.pkl".format(ticker))

    return df