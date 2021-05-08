# Andrew Antczak
# March 29th, 2021

'''
This code runs the actual backtest and sends the trade results to Strategy_Analysis.py for statistical analysis.
'''

from Strat_Algos.MA_Deriv import ma_sig_gen
from Strat_Algos.Bollinger_Bull import boll_zero_deriv, boll_f_inc_zero_deriv
from Strat_Algos.Bollinger_Band import boll_band
from Strat_Algos.RSI import rsi
import numpy as np
from datetime import datetime as dt
import os
import time
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class RunAnalysis:
    def __init__(self, tickers, strategy, strat_inputs, short_activation):
        self.tickers = tickers
        self.strategy = strategy
        if self.strategy == 'Moving Average':
            self.call = ma_sig_gen
        elif self.strategy == 'Bollinger Bull':
            self.call = boll_zero_deriv
        elif self.strategy == 'Bollinger Force Increase Bull':
            self.call = boll_f_inc_zero_deriv
        elif self.strategy == 'Bollinger Band':
            self.call = boll_band
        elif self.strategy == 'RSI':
            self.call = rsi

        self.inputs = strat_inputs

        self.short_act = short_activation

        self.df = {} # DataFrame Initialization
        self.price = {}
        self.start_price = {}
        return

    def run_sim(self):
        data, failed_tickers = self.call(self.tickers, self.inputs)
        for ticker in failed_tickers:
            if ticker in self.tickers:
                self.tickers.remove(ticker)
        dates = list(data.index.values)
        for i, date in enumerate(dates):
            dates[i] = str(date)[0:10]

        data['Cash'] = [float(20000) for i in range(len(data))]

        shorted = {}
        owned = {}
        for ticker in self.tickers:
            shorted["{}".format(ticker)] = False
            owned["{}".format(ticker)] = False
            data['{} shorted'.format(ticker)] = [0 for i in range(len(data))]
            data['{} bought'.format(ticker)] = [0 for i in range(len(data))]
            data['{} cash'.format(ticker)] = [float(20000)/len(self.tickers) for i in range(len(data))]
            data['{} sold'.format(ticker)] = [0 for i in range(len(data))]

        trades = []
        hold_times = []

        for i, date in enumerate(dates):
            sum = float(0)
            for ticker in self.tickers:
                if data['{} signal'.format(ticker)][i] == 1:
                    if shorted["{}".format(ticker)]:

                        short_date = data.loc[data['{} shorted'.format(ticker)] == 1].index.values[0]
                        short_date = str(short_date)[0:10]

                        s_pct_change = -1*(data['{} close'.format(ticker)][date] - data['{} close'.format(ticker)][short_date])\
                                       /(data['{} close'.format(ticker)][short_date]) + 1

                        data['{} cash'.format(ticker)][date:] = data['{} cash'.format(ticker)][short_date] * s_pct_change

                        s_pct_change = (s_pct_change - 1)*100.0

                        trades.append(s_pct_change)

                        data['{} shorted'.format(ticker)][short_date] = 0

                        shorted["{}".format(ticker)] = False

                        short_date = dt.strptime(short_date, "%Y-%m-%d")
                        s_date = dt.strptime(date, "%Y-%m-%d")
                        diff = s_date - short_date
                        hold_times.append(diff)

                    if not owned["{}".format(ticker)]:
                        data['{} bought'.format(ticker)][i] = 1 # Mark date bought for later access.

                        owned["{}".format(ticker)] = True

                elif data['{} signal'.format(ticker)][i] == -1:
                    try:
                        if owned["{}".format(ticker)]:
                            b_date = data.loc[data['{} bought'.format(ticker)] == 1].index.values[0]

                            b_date = str(b_date)[0:10]

                            pct_change = (data['{} close'.format(ticker)][date] - data['{} close'.format(ticker)][b_date])/\
                                         (data['{} close'.format(ticker)][b_date]) + 1

                            data['{} cash'.format(ticker)][date:] = data['{} cash'.format(ticker)][b_date] * pct_change

                            pct_change = (pct_change - 1)*100.0

                            trades.append(pct_change)

                            data['{} bought'.format(ticker)][b_date] = 0

                            owned["{}".format(ticker)] = False

                            b_date = dt.strptime(b_date, "%Y-%m-%d")
                            s_date = dt.strptime(date, "%Y-%m-%d")
                            diff = s_date - b_date
                            hold_times.append(diff)

                        if not shorted["{}".format(ticker)] and self.short_act:

                            shorted["{}".format(ticker)] = True

                            data['{} shorted'.format(ticker)][i] = 1 # Mark data shorted for later access.

                    except:
                        pass
                else:
                    pass

                if i == 0:
                    pass
                else:
                    sum += data['{} cash'.format(ticker)][i]

            if i == 0:
                pass
            else:
                data['Cash'].loc[date] = sum

        sum = 0
        for ticker in self.tickers:
            sum += data['{} cash'.format(ticker)][i]
        data['Cash'][i] = sum

        data['Daily_Ret'] = data['Cash'].pct_change(1)

        return data, trades, hold_times
