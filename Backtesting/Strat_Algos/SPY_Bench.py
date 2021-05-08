# Andrew Antczak
# April 3rd, 2021

'''
This code will take inputs from 'Strategy_Analysis.py' and will produce signal outputs to 'Strategy_Analysis.py'

This code contains a function producing a signal dataframe for a bullish stock, using bollinger bands.
This strategy is being considered for use in our annual Russell Rebalancing.

If the stock crosses the moving average, headed down, AND the moving average has a derivative of zero, indicating a
trend reversal, we will sell.
'''

import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
import numpy as np
import pickle
import os
import datetime as dt
import time


def bench_pull(ticker, input_list):
    start_date = input_list[0]
    end_date = input_list[1]

    try:
        data = pdr.get_data_yahoo("{}".format(ticker), start="{}".format(start_date), end="{}".format(end_date))
    except:
        return np.nan

    start_date = str(data.first_valid_index())[0:10]
    g_index_data = data.reset_index()
    end_date = str(g_index_data.iloc[-1]['Date'])[0:10]

    pct_change = (data['Adj Close'].loc[end_date] - data['Adj Close'].loc[start_date])/\
                 (data['Adj Close'].loc[start_date]) * 100.0

    return pct_change