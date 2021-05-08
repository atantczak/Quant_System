# AUTHOR: Andrew Antczak

# DATE: April 5th, 2021

# Background:
# This code is to be utilized as a Sanity Check for any strategy.

# Call Nature:
# Locally

import warnings
from datetime import datetime as dt

import numpy as np
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

from Strat_Algos.Bollinger_Bull import boll_zero_deriv, boll_f_inc_zero_deriv
from Strat_Algos.Bollinger_Band import boll_band
from Strat_Algos.MA_Deriv import ma_sig_gen
from Strat_Algos.SPY_Bench import bench_pull


class RunAnalysis:
    def __init__(self, tickers, strategy, strat_inputs, short_activation):
        self.tickers = tickers
        self.strategy = strategy
        if self.strategy == 'Moving Average':
            self.call = ma_sig_gen
        elif self.strategy == 'Bollinger Bull':
            self.call = boll_zero_deriv
        elif self.strategy == 'Bollinger Band':
            self.call = boll_band

        self.inputs = strat_inputs

        self.short_act = short_activation

        self.df = {} # DataFrame Initialization
        self.price = {}
        self.start_price = {}
        return

    def run_sim(self):
        data, failed_tickers = self.call(self.tickers, self.inputs)
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

                        print("{} Short exit at ${} on {}".format(ticker, "%.2f" % data['{} close'.format(ticker)][date], date))

                        shorted["{}".format(ticker)] = False

                        short_date = dt.strptime(short_date, "%Y-%m-%d")
                        s_date = dt.strptime(date, "%Y-%m-%d")
                        diff = s_date - short_date
                        hold_times.append(diff)

                    if not owned["{}".format(ticker)]:
                        data['{} bought'.format(ticker)][i] = 1 # Mark date bought for later access.

                        print("{} Buy at ${} on {}".format(ticker, "%.2f" % data['{} close'.format(ticker)][date], date))

                        owned["{}".format(ticker)] = True

                elif data['{} signal'.format(ticker)][i] == -1:
                    try:
                        if owned["{}".format(ticker)]:
                            b_date = data.loc[data['{} bought'.format(ticker)] == 1].index.values[0]

                            b_date = str(b_date)[0:10]

                            pct_change = (data['{} close'.format(ticker)][date] - data['{} close'.format(ticker)][b_date])/\
                                         (data['{} close'.format(ticker)][b_date]) + 1

                            data['{} cash'.format(ticker)][date:] = data['{} cash'.format(ticker)][b_date] * pct_change

                            print("{} Sell at ${} on {}".format(ticker, "%.2f" % data['{} close'.format(ticker)][date], date))

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

                            print("{} Short at ${} on {}".format(ticker, "%.2f" % data['{} close'.format(ticker)][date], date))

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


tickers = ['AAPL', 'TSLA']

start_date = '2020-01-01'
end_date = '2020-06-01'

stat_df = pd.DataFrame(columns=['Expected Value', 'Win Rate', 'Avg. Win', 'Avg. Loss', 'Sharpe', 'Calmar', 'Portfolio Return',
                      'Max Drawdown', 'Avg. Hold Time', 'SPY Return', 'Benchmark Expected Value', 'Benchmark Win Rate',
                      'Benchmark Avg. Win', 'Benchmark Avg. Loss'])

main_df = pd.DataFrame()

first = True

ra = RunAnalysis(tickers, 'Bollinger Band', ['Daily', start_date, end_date, 5, 5, 1], True)
data, trades, hold_times = ra.run_sim()

data = pd.DataFrame(data)
data.to_csv('Sanity_Check.csv')

exp_val = np.mean(trades)

pos_trades = [trade for trade in trades if trade > 0]
neg_trades = [trade for trade in trades if trade < 0]

win_rate = len(pos_trades) / len(trades) * 100.0

avg_win = np.mean(pos_trades)
avg_loss = np.mean(neg_trades)

avg_hold = np.mean(hold_times)

i = np.argmax(np.maximum.accumulate(data['Cash']) - data['Cash'])  # end of the period
j = np.argmax(data['Cash'][:i])  # start of period

port_ret = (data['Cash'][-1] - data['Cash'][0])/(data['Cash'][0]) * 100.0

max_drawdown = (data['Cash'][j] - data['Cash'][i]) / (data['Cash'][i]) * 100.0

annualized_ret = ((1 + (port_ret/100.0))**(252./len(data)) - 1) * 100.0

calmar_ratio = annualized_ret/max_drawdown

bm_returns = []
for ticker in tickers:
    price = data['{} close'.format(ticker)].dropna()
    bm_pct = ((price[-1] - price[0])/\
             (price[0])) * 100.0
    bm_returns.append(bm_pct)

bm_avg = np.mean(bm_returns)

bm_pos_trades = [trade for trade in bm_returns if trade > 0]
bm_neg_trades = [trade for trade in bm_returns if trade < 0]

bm_win_rate = len(bm_pos_trades)/(len(bm_returns)) * 100.0

bm_avg_win = np.mean(bm_pos_trades)
bm_avg_loss = np.mean(bm_neg_trades)

spy_bench = bench_pull('SPY', [start_date, end_date])

ret_avg = data['Daily_Ret'].mean()
sharpe = data['Daily_Ret'].mean()/data['Daily_Ret'].std()
sharpe*=np.sqrt((252/12)*8)

print("---- STATISTICAL MEASURES ----")
print("Expected Value: {}%".format("%.2f" % exp_val))
print("Win Rate: {}%".format("%.2f" % win_rate))
print("Avg. Win: {}%".format("%.2f" % avg_win))
print("Avg. Loss: {}%".format("%.2f" % avg_loss))
print("---- RISK MEASURES ----")
print("Sharpe Ratio: {}".format("%.2f" % sharpe))
print("Calmar Ratio: {}".format("%.2f" % calmar_ratio))
print("---- PORTFOLIO TRACKING ----")
print("Portfolio Return: {}%".format("%.2f" % port_ret))
print("Maximum Drawdown: {}%".format("%.2f" % max_drawdown))
print("Avg. Hold Time: {}".format(avg_hold))
print("---- BENCHMARK STATISTICS ----")
print("SPY Return: {}%".format("%.2f" % spy_bench))
print("Benchmark Buy and Hold Return: {}%".format("%.2f" % bm_avg))
print("Benchmark Win Rate: {}%".format("%.2f" % bm_win_rate))
print("Benchmark Average Win: {}%".format("%.2f" % bm_avg_win))
print("Benchmark Average Loss: {}%".format("%.2f" % bm_avg_loss))

stat_df.loc[end_date] = [exp_val, win_rate, avg_win, avg_loss, sharpe, calmar_ratio, port_ret, max_drawdown, avg_hold,
                     spy_bench, bm_avg, bm_win_rate, bm_avg_win, bm_avg_loss]

stat_df.to_excel('Sanity_Analysis.xlsx')

