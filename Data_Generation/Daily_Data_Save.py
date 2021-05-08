'''
This code will download daily pricing data, on a minutely basis, to our SP500 directory.
'''

import functools
import requests
import bs4 as bs
import datetime as dt
import math
import time
from matplotlib import style
from alpaca_trade_api.rest import REST
import alpaca_trade_api as tradeapi
import pandas as pd
import pickle
import random
import multiprocessing as mp
from Functions.Alpaca_Key_Store import initiate_API_keys
# ---------------------------------------------------------------------------------------------------------------------#
ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_API_BASE_URL = initiate_API_keys()
ALPACA_PAPER = True
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_API_BASE_URL, 'v2')
# ---------------------------------------------------------------------------------------------------------------------#
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

style.use('seaborn')


class Data_Save():
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        return

    def new_upload(self, tickers):

        for ticker in tickers:
            try:
                data = api.polygon.historic_agg_v2(str(ticker), 1, timespan='day', _from=self.start_date,
                                                   to=self.end_date).df
            except (ValueError):
                continue

            df = data.reset_index()

            if len(df) == 0:
                continue

            #df = df.reset_index(drop=True)
            #filename = 'Daily_SP500_Price_Data/{}.pk'.format(ticker)
            #with open(filename, 'wb') as file:
            #    pickle.dump(df, file)

            print("{}.pk".format(ticker) + " has been downloaded.")

        return


resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(resp.text, "lxml")
table = soup.find('table', {'class': 'wikitable sortable'})
tickers_trial = []
for row in table.findAll('tr')[1:]:
    ticker = row.findAll('td')[0].text.strip()
    mapping = str.maketrans(".", "-")
    ticker = ticker.translate(mapping)
    ticker = ticker.replace("-", ".")
    tickers_trial.append(ticker)

tickers = tickers_trial

# Simply change the end date to the start date and fill in a new end date!
ds = Data_Save('2017-01-17', '2021-02-22')

# Is there a way to determine which stocks have recently had splits? Splits call on IEX Cloud gives most recent date
# ... and split magnitude.

t_len = float(len(tickers))

groups = 16
groups = groups
g = math.floor((t_len) / groups)
if g < 1:
    g = 1


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


tick_chunks = list(chunks(tickers, g))

if __name__ == '__main__':
    pool = mp.Pool(groups)
    pool.map(functools.partial(ds.new_upload), tick_chunks)


