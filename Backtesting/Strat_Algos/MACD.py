# AUTHOR: Andrew Antczak

# DATE: May 8th, 2021

# Background:
# This code is building the dataframe that will contain macd buy/sell signals.

import os
import datetime as dt
import time

import pandas as pd
import numpy as np
import pickle

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


def macd(tickers, input_list):

    main_df = pd.DataFrame()
    failed_tickers = []

    for ticker in tickers:
        time_step = input_list[0]
        start_date = input_list[1]
        end_date = input_list[2]
        period_1 = input_list[3]
        period_2 = input_list[4]
        period_signal = input_list[5]
        smoothing = input_list[6]

        data = pd.DataFrame()
        today = time.mktime(dt.datetime.strptime(start_date, "%Y-%m-%d").timetuple())
        s_today = str(dt.datetime.fromtimestamp(today))[0:10]
        end_date_reached = False
        c = 0

        if time_step == 'Daily':
            # if os.path.exists('../../Data_Store/Daily_SP500_Price_Data/{}.pk'.format(ticker)):
            if os.path.exists('../../Data_Store/Yah_Daily_Prices/Daily_Price_Data/{}.pk'.format(ticker)):
                # filename = '../../Data_Store/Daily_SP500_Price_Data/{}.pk'.format(ticker)
                filename = '../../Data_Store/Yah_Daily_Prices/Daily_Price_Data/{}.pk'.format(ticker)
                with open(filename, 'rb') as file:
                    # Change Index to timestamp for original Polygon Data
                    # Change Index to Date for Yah Finance Data
                    data = pd.DataFrame(pickle.load(file)).set_index('Date', drop=True)
            else:
                failed_tickers.append(ticker)
                continue

            data = data.loc[start_date:end_date]
        else:
            while end_date_reached is False:

                today = s_today
                today = time.mktime(dt.datetime.strptime(today, "%Y-%m-%d").timetuple())

                if c == 0:
                    c += 1
                    if os.path.exists('../../Data_Store/{}_SP500_Price_Data/{}_{}.pk'.format(time_step, ticker, s_today)):
                        filename = '../../Data_Store/{}_SP500_Price_Data/{}_{}.pk'.format(time_step, ticker, s_today)
                        with open(filename, 'rb') as file:
                            data = pd.DataFrame(pickle.load(file)).set_index('timestamp', drop=True)
                    else:
                        data = pd.DataFrame()
                else:
                    if os.path.exists('../../Data_Store/{}_SP500_Price_Data/{}_{}.pk'.format(time_step, ticker, s_today)):
                        filename = '../../Data_Store/{}_SP500_Price_Data/{}_{}.pk'.format(time_step, ticker, s_today)
                        with open(filename, 'rb') as file:
                            df = pd.DataFrame(pickle.load(file)).set_index('timestamp', drop=True)
                    else:
                        df = pd.DataFrame()

                    frames = [data, df]
                    data = pd.concat(frames)

                s_today = str(dt.datetime.fromtimestamp(today) + dt.timedelta(days=1))[0:10]
                if s_today == end_date:
                    end_date_reached = True
                else:
                    continue

        data = data.fillna(0)
        multiplier = {}

        for period in [period_1, period_2]:
            multiplier["{}".format(period)] = float(smoothing / (1 + period))
            data['sma_{}'.format(period)] = data['Adj Close'].rolling(window=period).mean()
            data['ema_{}'.format(period)] = [
                data['Adj Close'][i] * multiplier["{}".format(period)] + data['sma_{}'.format(period)][i - 1] * (
                            1 - multiplier["{}".format(period)]) for i in range(0, len(data))]
            data['ema_{}'.format(period)] = [
                data['Adj Close'][i] * multiplier["{}".format(period)] + data['ema_{}'.format(period)][i - 1] * (
                            1 - multiplier["{}".format(period)]) for i in range(0, len(data))]

        data['MACD'] = data['ema_{}'.format(period_1)] - data['ema_{}'.format(period_2)]
        sig_multiplier = float(smoothing / (1 + period_signal))
        data['sma_MACD'] = data['MACD'].rolling(window=period).mean()
        data['signal_line'] = [data['MACD'][i] * sig_multiplier + data['sma_MACD'][i] * (1 - sig_multiplier) for i in
                               range(0, len(data))]
        data['signal_line'] = [data['MACD'][i] * sig_multiplier + data['signal_line'][i - 1] * (1 - sig_multiplier) for
                               i in range(0, len(data))]

        macd = []
        for i, element in enumerate(data['MACD']):
            if data['MACD'][i] > data['signal_line'][i] and data['MACD'][i-1] < data['signal_line'][i-1]:
                macd.append(-1)
            elif data['MACD'][i] < data['signal_line'][i] and data['MACD'][i-1] > data['signal_line'][i-1]:
                macd.append(1)
            else:
                macd.append(0)

        data['Signal'] = macd
        data = data.rename(columns={'Close': '{} close'.format(ticker)})
        data = data.rename(columns={'Signal': '{} signal'.format(ticker)})

        data.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close', 'ema_{}'.format(period_1), 'ema_{}'.format(period_2),
                   'signal_line', 'MACD', 'sma_MACD', 'sma_{}'.format(period_1), 'sma_{}'.format(period_2)], 1, inplace=True)

        if main_df.empty:
            main_df = data
        else:
            main_df = main_df.join(data, how='outer')

    return main_df, failed_tickers