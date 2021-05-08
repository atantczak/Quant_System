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
import numpy as np
import pickle
import os
import datetime as dt
import time


def boll_zero_deriv(tickers, input_list):
    main_df = pd.DataFrame()

    for ticker in tickers:
        year = input_list[0]
        start_date = input_list[1]
        end_date = input_list[2]
        ma_len = input_list[3]
        std = input_list[4]

        if os.path.exists('../../Data_Store/Russell_OHLCV_Data/{}/{}.csv'.format(year, ticker)):
            data = pd.read_csv('../../Data_Store/Russell_OHLCV_Data/{}/{}.csv'.format(year, ticker))
        else:
            return pd.DataFrame()

        data = data.set_index('Date', drop=True)
        data = data.loc[start_date:end_date]

        rolling = data['Adj Close'].rolling(ma_len).mean()
        std = std*data['Adj Close'].rolling(ma_len).std()
        data['Moving Average'] = rolling
        data['Upper Bollinger'] = rolling + std
        data['Lower Bollinger'] = rolling - std

        data['Shift'] = data['Moving Average'].shift(ma_len)

        data['MA Derivative'] = (data['Moving Average'] - data['Shift'])/ma_len

        signal = []
        for i, element in enumerate(data['Adj Close']):
            if i == 0:
                signal.append(1)
                continue
            if element < data['Moving Average'][i] and data['MA Derivative'][i] <= 0:
                signal.append(-1)
            else:
                signal.append(0)
        signal[-1] = -1

        data['Signal'] = signal
        data = data.rename(columns={'Adj Close': '{} close'.format(ticker)})
        data = data.rename(columns={'Signal': '{} signal'.format(ticker)})

        data.drop(['Open', 'High', 'Low', 'Close', 'Volume', 'Moving Average', 'Upper Bollinger', 'Lower Bollinger',
                   'Shift', 'MA Derivative'], 1, inplace=True)

        if main_df.empty:
            main_df = data
        else:
            main_df = main_df.join(data, how='outer')

    failed_tickers = []
    return main_df, failed_tickers


def boll_f_inc_zero_deriv(tickers, input_list):
    main_df = pd.DataFrame()

    for ticker in tickers:
        year = input_list[0]
        start_date = input_list[1]
        end_date = input_list[2]
        ma_len = input_list[3]
        std = input_list[4]

        if os.path.exists('../../Data_Store/Russell_OHLCV_Data/{}/{}.csv'.format(year, ticker)):
            data = pd.read_csv('../../Data_Store/Russell_OHLCV_Data/{}/{}.csv'.format(year, ticker))
        else:
            return pd.DataFrame()

        data = data.set_index('Date', drop=True)
        data = data.loc[start_date:end_date]

        rolling = data['Adj Close'].rolling(ma_len).mean()
        std = std*data['Adj Close'].rolling(ma_len).std()
        data['Moving Average'] = rolling
        data['Upper Bollinger'] = rolling + std
        data['Lower Bollinger'] = rolling - std

        data['Shift'] = data['Moving Average'].shift(ma_len)

        data['MA Derivative'] = (data['Moving Average'] - data['Shift'])/ma_len

        signal = []
        sig_search = False
        for i, element in enumerate(data['Adj Close']):
            if i == 0:
                signal.append(1)
                continue
            if not sig_search and i > 15:
                sig_search = True
            if element < data['Moving Average'][i] and data['MA Derivative'][i] <= 0 and sig_search:
                signal.append(-1)
                sig_search = False
            else:
                signal.append(0)
        signal[-1] = -1

        data['Signal'] = signal
        data = data.rename(columns={'Adj Close': '{} close'.format(ticker)})
        data = data.rename(columns={'Signal': '{} signal'.format(ticker)})

        data.drop(['Open', 'High', 'Low', 'Close', 'Volume', 'Moving Average', 'Upper Bollinger', 'Lower Bollinger',
                   'Shift', 'MA Derivative'], 1, inplace=True)

        if main_df.empty:
            main_df = data
        else:
            main_df = main_df.join(data, how='outer')

    return main_df