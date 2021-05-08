#  Andrew Antczak
# March 30th, 2021

import requests
import bs4 as bs
import random


def get_sp500(number):
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip()
        mapping = str.maketrans(".", "-")
        ticker = ticker.translate(mapping)
        tickers.append(ticker)

    if number == 500:
        return tickers
    else:
        return random.sample(tickers, number)