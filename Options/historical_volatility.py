from yahoofinancials import YahooFinancials
from datetime import date, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from BacktraderAPI.BTDataFeed import *
from futu import *

def plot(stock_symbol, lengthOfTime):
    def historical_volatility(prices, end_time, plot=False):
        end = end_time.strftime('%Y-%m-%d')
        start = (end_time - timedelta(days=365)).strftime('%Y-%m-%d')
        prices = prices[
            (prices["formatted_date"] >  start) & (prices["formatted_date"] <= end)]

        prices.sort_index(ascending=False, inplace=True)
        prices['returns'] = (np.log(prices.close / prices.close.shift(-1)))
        daily_std = np.std(prices.returns)
        volatility = daily_std * 252 ** 0.5

        if plot:
            # Plot histograms
            fig, ax = plt.subplots(1, 1, figsize=(7, 5))
            n, bins, patches = ax.hist(
                prices.returns.values,
                bins=50, alpha=0.65, color='blue',
                label='12-month')

            ax.set_xlabel('log return of stock price')
            ax.set_ylabel('frequency of log return')
            ax.set_title('Historical Volatility for ' +
                         stock_symbol)

            # get x and y coordinate limits
            x_corr = ax.get_xlim()
            y_corr = ax.get_ylim()

            # make room for text
            header = y_corr[1] / 5
            y_corr = (y_corr[0], y_corr[1] + header)
            ax.set_ylim(y_corr[0], y_corr[1])

            # print historical volatility on plot
            x = x_corr[0] + (x_corr[1] - x_corr[0]) / 30
            y = y_corr[1] - (y_corr[1] - y_corr[0]) / 15
            ax.text(x, y, 'Annualized Volatility: ' + str(np.round(volatility * 100, 1)) + '%',
                    fontsize=11, fontweight='bold')
            x = x_corr[0] + (x_corr[1] - x_corr[0]) / 15
            y -= (y_corr[1] - y_corr[0]) / 20

            # display plot
            fig.tight_layout()

        return volatility

    end_time = date.today()
    start_time = date.today() - timedelta(days=lengthOfTime)

    # reformat date range
    end = end_time.strftime('%Y-%m-%d')
    start = start_time.strftime('%Y-%m-%d')
    # get prices
    json_prices = YahooFinancials(stock_symbol).get_historical_price_data(start, end, 'daily')

    # transform json file to dataframe
    prices = pd.DataFrame(json_prices[stock_symbol]
                          ['prices'])[['formatted_date', 'close']]

    end_dateList = [date.today() - timedelta(days=i) for i in range(lengthOfTime)]
    volList = [historical_volatility(prices, end_date) for end_date in end_dateList]

    ranked = pd.Series(volList[:365]).rank()
    rankNow = round (ranked[0] /365 * 100)


    volNow = round(volList[0] * 100, 2)
    plt.plot(end_dateList, volList)
    plt.title(f"Historical volaitily of {stock_symbol} now: {volNow}%, rank: {rankNow}")
    plt.show()

    return volNow, rankNow

if __name__ == '__main__':
    lengthOfTime = 8 * 365
    for t in ["TSLA", "AAPL"]:
        plot(t, lengthOfTime)







