from Run_Engine import RunAnalysis
from Ticker_Attainment.get_sp500_tickers import get_sp500
from Strat_Algos.SPY_Bench import bench_pull
import numpy as np
import os
import pandas as pd
import random
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
'''
This code will run a backtest on any strategy input and produce the following statistical measures:

1) Expected Value - Includes Assessment for Normalcy
2) Win Rate
3) Average Win
4) Average Loss
5) Mean Hold Time
6) Sharpe Ratio and/or Probabilistic Sharpe Ratio
7) Calmar Ratio
8) Some type of benchmark measure ~ Perhaps buy/hold during bet duration, at each time-step a) Win Rate, Avg. Win, Avg. Loss
9) Maxmium Drawdown
10) Portfolio Return

This code will NOT run a portfolio simulation in terms of overall returns.

Overall returns are a bad assessment of backtest capability as they are heavily dependent upon market fluctuations
during the time-period that they're run and therefore can easily dilute and/or hide the true impact/potential of any
given strategy.
'''

'''
STRATEGY CALL EXPLANATION

All Strategies: Last Input (True/False) --- Shorting Activation

MOVING AVERAGE DERIVATIVE INPUTS: "Moving Average": time-step ('Daily', 'Hourly', 'Minutely'), start_date, end_date, 
moving average length, bollinger length, std

'Moving Average', ['Daily', '2017-02-13', '2018-02-26', ma_len, boll_len, 3]


BOLLINGER BAND: "Bollinger Band": time-step ('Daily, 'Hourly', 'Minutely'), start_date, end_date, ma_len, boll_len, std

'Bollinger Band', ['Daily', start_date, end_date, 100, 100, 4]


RSI: "RSI": time-step('Daily', 'Hourly', 'Minutely'), start_date, end_date, window, strength

'RSI', ['Daily', start_date, end_date, 14, 70]


BOLLINGER BULL, RUSSELL APPLICATION INPUTS: "Bollinger Bull": year, start_date, ma_len, std

'Bollinger Bull', [year, '{}-04-01'.format(year), 15, 1]

'''


'''
TICKER GENERATION EXPLANATION

SP500 TICKERS: tickers = get_sp500(500) # You can choose a number of tickers to be randomly pulled.

RUSSELL TICKERS: 
year = 2010
tickers = os.listdir('../../Data_Store/Russell_OHLCV_Data/{}/'.format(year)) # If you're pulling tickers for Russell
tickers = [os.path.splitext(x)[0] for x in tickers] # If you're pulling tickers for Russell

YAHOO TICKERS:
* This includes over 5000 daily time-step tickers. These time-series start as early as 2000.
tickers = os.listdir('../../Data_Store/Yah_Daily_Prices/Daily_Price_Data/')
tickers = [os.path.splitext(x)[0] for x in tickers]

'''

tickers = ['AMZN', 'MMC', 'AAPL', 'PFE', 'TGT']

start_date = '2000-01-01'
end_date = '2021-04-01'

stat_df = pd.DataFrame(columns=['Expected Value', 'Win Rate', 'Avg. Win', 'Avg. Loss', 'Sharpe', 'Calmar', 'Portfolio Return',
                      'Max Drawdown', 'Avg. Hold Time', 'SPY Return', 'Benchmark Expected Value', 'Benchmark Win Rate',
                      'Benchmark Avg. Win', 'Benchmark Avg. Loss'])

main_df = pd.DataFrame()

first = True

ra = RunAnalysis(tickers, 'RSI', ['Daily', start_date, end_date, 5, 90], False)
data, trades, hold_times = ra.run_sim()

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
    try:
        price = data['{} close'.format(ticker)].dropna()
        bm_pct = ((price[-1] - price[0])/\
                 (price[0])) * 100.0
        bm_returns.append(bm_pct)
    except:
        pass

bm_avg = np.mean(bm_returns)

bm_pos_trades = [trade for trade in bm_returns if trade > 0]
bm_neg_trades = [trade for trade in bm_returns if trade < 0]

bm_win_rate = len(bm_pos_trades)/(len(bm_returns)) * 100.0

bm_avg_win = np.mean(bm_pos_trades)
bm_avg_loss = np.mean(bm_neg_trades)

spy_bench = bench_pull('SPY', [start_date, end_date])

ret_avg = data['Daily_Ret'].mean()
sharpe = data['Daily_Ret'].mean()/data['Daily_Ret'].std()
sharpe*=np.sqrt((252 * 6))

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

#stat_df.to_excel('Test_Analysis.xlsx')

