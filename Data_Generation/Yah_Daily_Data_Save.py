'''
This code will download daily pricing data, on a minutely basis, to our SP500 directory.
'''

import csv
import pickle
import pandas as pd
import pandas_datareader.data as web
from matplotlib import style

# ---------------------------------------------------------------------------------------------------------------------#
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

style.use('seaborn')


class Data_Save():
    def __init__(self, start_date, end_date, tickers):
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = tickers
        return

    def new_upload(self):
        tickers = self.tickers

        for ticker in tickers:

            try:
                start = '2000-01-01'
                end = '2021-04-29'
                data = web.DataReader(str(ticker), 'yahoo', start, end)
                df = data.reset_index()
            except:
                print("------------------------------")
                print("{} failed to download.".format(ticker))
                print("------------------------------")
                continue

            filename = 'Daily_Price_Data/{}.pk'.format(ticker)
            with open(filename, 'wb') as file:
                pickle.dump(df, file)

            print("{}.pk".format(ticker) + " has been downloaded.")

        return


with open('../Stock_Exchange_Lists/NYSE.csv') as csv_file:
    data_1 = csv.reader(csv_file, delimiter=",")

    tickers_1 = []
    sector_1 = []

    for row in data_1:
        tickers_1.append(row[0])
        sector_1.append(row[5])

        tickers_1 = [x.strip(' ') for x in tickers_1]
        sector_1 = [x.strip(' ') for x in sector_1]

    while ("" in tickers_1):
        tickers_1.remove("")

del tickers_1[0]
del sector_1[0]

with open('../Stock_Exchange_Lists/NASDAQ.csv') as csv_file:
    data_2 = csv.reader(csv_file, delimiter=",")

    tickers_2 = []
    sector_2 = []

    for row in data_2:
        tickers_2.append(row[0])
        sector_2.append(row[5])

        tickers_2 = [x.strip(' ') for x in tickers_2]
        sector_2 = [x.strip(' ') for x in sector_2]

    while ("" in tickers_2):
        tickers_2.remove("")

del tickers_2[0]
del sector_2[0]

# Compile all tickers from each stock exchange of interest.
total_tickers = []
total_tickers.extend(tickers_1)
total_tickers.extend(tickers_2)

# Deleting any duplicates from those exchanges. Successful.
total_tickers = list(dict.fromkeys(total_tickers))

# Simply change the end date to the start date and fill in a new end date!
ds = Data_Save('2000-01-01', '2021-04-29', total_tickers)
ds.new_upload()




