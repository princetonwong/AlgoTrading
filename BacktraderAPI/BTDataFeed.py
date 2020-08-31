from futu import *
import backtrader as bt
import pandas as pd
import numpy as np
import seaborn as sns
from CustomAPI.FutuAPI import FutuAPI
from pathlib import Path
from CustomAPI.Helper import Helper
from Keys import *
from alpha_vantage.timeseries import TimeSeries

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

def getAlphaVantageFeeds(symbol_list, compact=False, debug=False, *args, **kwargs):
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
        data = bt.feeds.PandasData(
            dataname=data_list[i][0],  # This is the Pandas DataFrame
            name=data_list[i][1],  # This is the symbol
            timeframe=bt.TimeFrame.Days,
            compression=1,
            fromdate=datetime(2018, 1, 1),
            todate=datetime(2019, 1, 1)
        )
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