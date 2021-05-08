# Andrew Antczak
# March 29th, 2021

'''
This code will take inputs from 'Strategy_Analysis.py' and will produce signal outputs to 'Strategy_Analysis.py'

This code contains a function producing a signal dataframe for moving average derivatives.
'''

import pandas as pd
import numpy as np
import pickle
import os
import datetime as dt
import time


def rsi(tickers, input_list):

    main_df = pd.DataFrame()
    failed_tickers = []

    for ticker in tickers:
        time_step = input_list[0]
        start_date = input_list[1]
        end_date = input_list[2]
        window = input_list[3]
        strength = input_list[4]

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
        data['Pct_Change'] = data['Adj Close'].pct_change()
        data['+_Change'] = data.apply(lambda x: x['Pct_Change'] if x['Pct_Change'] > 0.0 else np.nan, axis=1)
        data['-_Change'] = data.apply(lambda x: x['Pct_Change'] if x['Pct_Change'] < 0.0 else np.nan, axis=1)
        data['+_Sum'] = (data['+_Change'].rolling(window=window, min_periods=1).sum()) / window
        data['-_Sum'] = - (data['-_Change'].rolling(window=window, min_periods=1).sum()) / window
        data['RSI'] = [(100 - (100 / (1 + (data['+_Sum'][i] / data['-_Sum'][i])))) for i in range(0, len(data))]

        rsi= []
        for i, element in enumerate(data['RSI']):
            if data['RSI'][i] > float(strength):
                rsi.append(-1)
            elif data['RSI'][i] < 100-float(strength):
                rsi.append(1)
            else:
                rsi.append(0)

        data['Signal'] = rsi
        data = data.rename(columns={'Close': '{} close'.format(ticker)})
        data = data.rename(columns={'Signal': '{} signal'.format(ticker)})

        data.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close', 'Pct_Change', '+_Change', '-_Change', '+_Sum', '-_Sum',
                   'RSI'], 1, inplace=True)

        if main_df.empty:
            main_df = data
        else:
            main_df = main_df.join(data, how='outer')

    return main_df, failed_tickers