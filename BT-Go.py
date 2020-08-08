from futu import *
import backtrader as bt
from BacktraderAPI import BTStrategy, BTDataFeed

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_30M
CCIPARAMETERS = (26, 0.015, 100 ,5)
TIMERANGE = ("2020-03-01", "00:00:00", "2020-07-31", "16:31:00")

data = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE)

cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(BTStrategy.RSIStrategy)
cerebro.broker.setcash(90000.0)
cerebro.broker.setcommission(commission=0.001)
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run(stdstats = True)
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot(style = "candle", iplot= True, subtxtsize = 6, maxcpus=1)