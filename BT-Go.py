from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_30M
CCIPARAMETERS = (26, 0.015, 100 ,5)
TIMERANGE = ("2020-03-01", "00:00:00", "2020-07-31", "16:31:00")

folderName = "{}-{}-{}".format(SYMBOL, SUBTYPE, Helper().get_timestamp())

#Init
cerebro = bt.Cerebro()

#Data Feed
data = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE)
cerebro.adddata(data)

#Strategy
cerebro.addstrategy(BTStrategy.maCross)

#Broker
cerebro.broker.setcash(90000.0)
cerebro.broker.setcommission(commission=0.001)
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

#Analyzer
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

#Run
strategies = cerebro.run(stdstats = True)
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

#Plotting
cerebro.plot(style = "candle", iplot= True, subtxtsize = 6, maxcpus=1)

#Analyzer methods
firstStrategy = strategies[0]
BTAnalyzer.printTradeAnalysis(firstStrategy.analyzers.ta.get_analysis())
BTAnalyzer.printSQN(firstStrategy.analyzers.sqn.get_analysis())

df = BTAnalyzer.getTradeAnalysisDf(firstStrategy.analyzers.ta.get_analysis(), folderName)
df2 = BTAnalyzer.getSQNDf(firstStrategy.analyzers.sqn.get_analysis(), folderName)