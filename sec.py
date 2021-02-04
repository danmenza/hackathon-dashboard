import datetime as dt
import dateutil.parser
import pytz

import requests
from bs4 import BeautifulSoup
import pandas as pd


class SEC:

    proxies = {'http':'proxy_if_needed',
       'https':'proxy_if_needed'}

    def __init__(self, cik):

        url = ('https://www.sec.gov/cgi-bin/browse-edgar?'
       'action=getcompany&'
       'CIK={}&'
       'start=0&'
       'count=40&'
       'output=atom').format(str(cik))

        self.r = requests.get(url, proxies=SEC.proxies)

    def parse(e):
        filing_type = e.find('filing-type').text
        updated = e.find('updated').text
        #u_date = dt.datetime.strptime("{}".format(updated), '%Y/%m/%dT%I:%M')
        est = pytz.timezone('US/Eastern')
        u_date = dateutil.parser.parse(updated).astimezone(est)
        href = e.find('link').get('href')
        return {'filing_type':filing_type,'updated':u_date, 'url':href}

    @property
    def df(self):
        soup = BeautifulSoup(self.r.text, 'lxml')
        entries = soup.find_all('entry')

        data = [SEC.parse(e) for e in entries]
        return pd.DataFrame(data)
