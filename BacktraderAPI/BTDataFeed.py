from futu import *
import backtrader as bt
import pandas as pd
from CustomAPI.FutuAPI import FutuAPI
from pathlib import Path
from CustomAPI.Helper import Helper
from Keys import *
from alpha_vantage.timeseries import TimeSeries
import yfinance
from enum import Enum, unique


def getFutuDataFeed(symbol: str, subtype: SubType, timeRange, folderName = None):
    if timeRange is None:
        df = FutuAPI().getRealTimeKLine(symbol, subtype)
    else:
        df = FutuAPI().getKLineFromDate(symbol, subtype, timeRange)
    df['datetime'] = pd.to_datetime(df['time_key'], format='%Y-%m-%d %H:%M:%S')
    df = df[['open', 'high', 'low', 'close', 'volume', "datetime"]]
    df.set_index("datetime", inplace=True)

    if folderName is not None:
        Helper().gradientAppliedXLSX(df, "FutuRAWData", ['close'])

    return bt.feeds.PandasData(dataname=df, openinterest=None)

@unique
class YahooInterval(Enum):
    K_1M = "1m"
    K_5M = "5m"
    K_15M = "15m"
    K_30M = "30m"
    K_60M = "60m"
    K_DAY = "1d"

def getYahooDataFeeds(symbol_list, subtype, timerange, folderName = None):
    yahooSubtype = YahooInterval[subtype].value
    yahooStart, yahooEnd = timerange[0], timerange[2]

    df = yfinance.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers= symbol_list,

        start = yahooStart,
        end =yahooEnd,
        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        # period="5d",

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval= yahooSubtype,

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by='ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust=True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost=False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads=True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy=None
    )

    if folderName is not None:
        Helper().gradientAppliedXLSX(df, "YahooData", ['close'])

    return bt.feeds.PandasData(dataname=df, openinterest=None)

def getAlphaVantageDataFeeds(symbol_list, compact=False, debug=False, folderName = None, *args, **kwargs):
    '''
    Helper function to download Alpha Vantage Data.

    This will return a nested list with each entry containing:
        [0] pandas dataframe
        [1] the name of the feed.
    '''
    data_list = list()
    size = 'compact' if compact else 'full'

    for symbol in symbol_list:
        if debug:
            print('Downloading: {}, Size: {}'.format(symbol, size))
        # Submit our API and create a session
        alpha_ts = TimeSeries(key=AlphaVantage_API_KEY, output_format='pandas')
        data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        #Convert the index to datetime.
        data.index = pd.to_datetime(data.index)
        data.columns = ['Open', 'High', 'Low', 'Close','Volume']

        if debug:
            print(data)

        data_list.append((data, symbol))

    dataFeeds = list()
    for i in range(len(data_list)):
        symbolName= data_list[i][1]
        data = bt.feeds.PandasData(
            dataname=data_list[i][0],  # This is the Pandas DataFrame
            name= symbolName,  # This is the symbol
            timeframe=bt.TimeFrame.Days,
            compression=1,
            fromdate=datetime(2018, 1, 1),
            todate=datetime(2019, 1, 1)
        )
        if folderName is not None:
            Helper().gradientAppliedXLSX(data, "AlphaVantageData-{}".format(symbolName), ['close'])

        dataFeeds.append(data)

    return dataFeeds

def getExcelDataFeed(excelPath: str):
    df = pd.read_excel(excelPath, parse_dates=['time_key'])
    df['datetime'] = pd.to_datetime(df['time_key'], format='%Y-%m-%d %H:%M:%S')
    df = df[['open', 'high', 'low', 'close', 'volume', "datetime"]]
    df.set_index("datetime", inplace=True)
    return bt.feeds.PandasData(dataname=df, openinterest=None)

def getCSVDataFeed(csvPath: str):
    return bt.feeds.GenericCSVData(dataname=csvPath, fromdate=datetime.datetime(2020, 1, 1),
                                   todate=datetime.datetime(2020, 12, 31),
                                   nullvalue=0.0, dtformat=('%Y-%m-%d %H:%M:%S'), datetime=2,
                                   high=5, low=6, open=3, close=4, volume=7, openinterest=-1)

def getHDFWikiPriceDataFeed(tickers: [str], startYear="2006", endYear:str = "2017"):
    hdfPath = Path.cwd() / "Data" / "assets.h5"
    idx = pd.IndexSlice
    df= (pd.read_hdf(hdfPath, 'quandl/wiki/prices')
            .loc[idx[startYear:endYear, tickers], ['adj_open', 'adj_high', 'adj_low', 'adj_close', 'adj_volume']]
            .rename(columns={"adj_open": "open", "adj_high": "high", "adj_low": "low", "adj_close": "close", "adj_volume": "volume"})
            .reset_index(level=[0,1]))
            # .unstack('ticker')
            # .sort_index()
            # .shift(-1)
            # .tz_localize('UTC'))
    # df['datetime'] =
    # df = df[['open', 'high', 'low', 'close', 'volume', "datetime"]]
    # df.set_index("datetime", inplace=True)

    df['datetime'] = df["date"]
    df = df[['open', 'high', 'low', 'close', 'volume', "datetime"]]
    df.set_index("datetime", inplace=True)

    return bt.feeds.PandasData(dataname=df, openinterest=None)