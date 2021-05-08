# Andrew Antczak
# March 29th, 2021

'''
This code will recieve input from 'Strategy_Analysis.py' and will produce signals as output to 'Strategy_Analysis.py'.

'''

import pandas as pd
import numpy as np


class MacdSignalProduction:
    def __init__(self):

        self.buy_search = {}
        self.buy_act = {}
        # Indicators
        self.macd = {}
        self.macd_sig = {}
        self.ema_short = {}
        self.ema_long = {}
        self.ema_signal = {}
        self.ema = {}

        self.macd_sig_c = {}
        self.macd_hist = {}

    def signal_line(self, macd_sig, ticker):
        k = 2.0 / (9 + 1)
        if len(macd_sig) == 9:
            self.ema_signal["{}".format(ticker)] = np.sum(macd_sig) / 9.0
        elif len(macd_sig) > 9:
            self.ema_signal["{}".format(ticker)] = self.macd["{}".format(ticker)] * k + self.ema_signal[
                "{}".format(ticker)] * (1 - k)
        else:
            self.ema_signal["{}".format(ticker)] = np.nan
        return

    def short_ema(self, i, close_prices, price, ticker):
        k = 2.0 / (12 + 1)
        if i == 12:
            self.ema_short["{}".format(ticker)] = np.sum(close_prices) / 9.0
        elif i > 12:
            self.ema_short["{}".format(ticker)] = price * k + self.ema_short["{}".format(ticker)] * (1 - k)
        else:
            self.ema_short["{}".format(ticker)] = np.nan
        return

    def long_ema(self, i, close_prices, price, ticker):
        k = 2.0 / (26 + 1)
        if i == 26:
            self.ema_long["{}".format(ticker)] = np.sum(close_prices) / 26.0
        elif i > 26:
            self.ema_long["{}".format(ticker)] = price * k + self.ema_long["{}".format(ticker)] * (1 - k)
        else:
            self.ema_long["{}".format(ticker)] = np.nan
        return

    def macd_calc(self, ticker):
        self.macd["{}".format(ticker)] = self.ema_short["{}".format(ticker)] - self.ema_long["{}".format(ticker)]
        return

    def macd_hist_zero(self, i, close_prices, price, macd_sig, s, ticker):
        self.short_ema(i, close_prices, price, ticker)
        self.long_ema(i, close_prices, price, ticker)
        self.macd_calc(ticker)
        self.signal_line(macd_sig, ticker)
        self.macd_sig_c["{}".format(ticker)] = self.ema_signal["{}".format(ticker)]
        self.macd_hist["{}_{}".format(i, ticker)] = self.macd["{}".format(ticker)] - self.macd_sig_c["{}".format(ticker)]
        try:
            del self.macd_hist["{}_{}".format(i - 3, ticker)]
        except:
            pass

        try:
            hist_o = self.macd["{}".format(ticker)] - self.macd_sig_c["{}".format(ticker)]
            hist_t = self.macd_hist["{}_{}".format(i - 1, ticker)]
            hist_th = self.macd_hist["{}_{}".format(i - 2, ticker)]
        except:
            hist_o = 0.0
            hist_t = 0.0
            hist_th = 0.0

        if s == 1:
            if self.macd["{}".format(ticker)] > self.macd_sig_c["{}".format(ticker)]:
                s = 0

        if s == 0:
            if self.macd["{}".format(ticker)] < self.macd_sig_c["{}".format(ticker)]:
                self.buy_search["{}".format(ticker)] = True

            if hist_th < hist_t < hist_o and self.buy_search["{}".format(ticker)] is True and self.macd["{}".format(ticker)] <= 0.0:
                self.buy_act["{}".format(ticker)] = True

        return s