from CustomAPI.FutuAPI import FutuAPI
from futu import *
import backtrader as bt
import pandas as pd
import CereboStrategy

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_DAY
CCIPARAMETERS = (26, 0.015, 100 ,5)
TIMERANGE = ("2019-07-01", "00:00:00", "2020-07-31", "16:31:00")

#Convenience Method
def getFutuDataFeed(symbol: str, subtype: SubType, timeRange):
    if timeRange is None:
        df = FutuAPI().getRealTimeKLine(symbol, subtype)
    else:
        df = FutuAPI().getKLineFromDate(symbol, subtype, timeRange)
    df['datetime'] = pd.to_datetime(df['time_key'], format='%Y-%m-%d %H:%M:%S')
    df = df[['open', 'high', 'low', 'close', 'volume', "datetime"]]
    df.set_index("datetime", inplace=True)
    return bt.feeds.PandasData(dataname=df, openinterest=None)

data = getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE)

cerebro = bt.Cerebro()
cerebro.addstrategy(CereboStrategy.CCICrossStrategy, cciParameters=CCIPARAMETERS)
cerebro.adddata(data)
cerebro.broker.setcash(30000.0)
cerebro.broker.setcommission(commission=0.001)
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run(stdstats = True)
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot(style = "candle", subtxtsize = 6)