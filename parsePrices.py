import os
import json
import datetime as dt

import pandas as pd

with open('clientList.json') as f:
    client_list = json.load(f)

ticker_map = {v['ticker']:k for k, v in client_list.items()}
ticker_map

def dt_compile(d, t):
    return dt.datetime.strptime("{} {}".format(d, t), '%m/%d/%Y %I:%M %p')

class DataFile:
    data_dir = 'data'
    fq_path = os.path.join(os.path.curdir, data_dir)

    def __init__(self, file):
        self.file = file
        self.fq_file = os.path.join(DataFile.fq_path, file)

    @property
    def symbol(self):
        return self.file[:-4]

    def __repr__(self):
        return self.symbol

    @property
    def fullname(self):
        return ticker_map[self.symbol]

    @property
    def df(self):
        df = pd.read_csv(self.fq_file)
        df['datetime'] = df.apply(lambda x: dt_compile(x['Date'], x['Time']), axis=1)
        return df

    @staticmethod
    def collect():
        data = [DataFile(file) for file in os.listdir(DataFile.fq_path)]
        data_dict = {d.symbol: d for d in data}
        return data_dict
