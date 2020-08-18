from futu import *
import backtrader as bt
import pandas as pd
import numpy as np
import seaborn as sns
from CustomAPI.FutuAPI import FutuAPI
from pathlib import Path

def getFutuDataFeed(symbol: str, subtype: SubType, timeRange):
    if timeRange is None:
        df = FutuAPI().getRealTimeKLine(symbol, subtype)
    else:
        df = FutuAPI().getKLineFromDate(symbol, subtype, timeRange)
    df['datetime'] = pd.to_datetime(df['time_key'], format='%Y-%m-%d %H:%M:%S')
    df = df[['open', 'high', 'low', 'close', 'volume', "datetime"]]
    df.set_index("datetime", inplace=True)
    return bt.feeds.PandasData(dataname=df, openinterest=None)

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

def getHDFWikiPriceDataFeed(tickers: [str]):
    hdfPath = Path.cwd() / "Data" / "assets.h5"
    idx = pd.IndexSlice
    df= (pd.read_hdf(hdfPath, 'quandl/wiki/prices')
            .loc[idx['2006':'2017', tickers], ['adj_open', 'adj_high', 'adj_low', 'adj_close', 'adj_volume']]
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