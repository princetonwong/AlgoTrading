from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator, BTFilter

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_30M
CCIPARAMETERS = (26, 0.015, 100 ,7)
TIMERANGE = ("2020-06-01", "00:00:00", "2020-08-21", "16:31:00")
# TIMERANGE = None

FOLDERNAME = "{}-{}-{}".format(SYMBOL, SUBTYPE, Helper().get_timestamp())

#Init
cerebro = bt.Cerebro()

cerebro.addwriter(bt.WriterFile, csv=True, out=Helper().getWriterOutputPath(FOLDERNAME), rounding=2)

#Data Feed
data0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)
cerebro.adddata(data0)

# data1 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)
# cerebro.adddata(data1)
# data = BTDataFeed.getHDFWikiPriceDataFeed(["TSLA"], startYear= "2016")

#Data Filter
# data0.addfilter(bt.filters.HeikinAshi(data0))

#Sizer
cerebro.addsizer(BTSizer.FixedSizer)

#Broker
cerebro.broker.setcash(60000.0)
# cerebro.broker.setcommission(commission=0)
cerebro.broker.setcommission(commission=10.6, margin=26000.0, mult=10.0)
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

#Strategy
cerebro.addstrategy(BTStrategy.CCICrossStrategyWithSLOWKDExit0)
# cerebro.optstrategy(BTStrategy.CCICrossStrategyWithSLOWKDExit, hold= range(5,10))

#Analyzer
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")

#Run
results = cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

#Plotting
figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1)
Helper().saveFig(figs, FOLDERNAME)

#Bokeh Plotting
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from backtrader_plotting.bokeh.optbrowser import OptBrowser
b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
fig = cerebro.plot(b, iplot=False)

# b = Bokeh(style='bar', scheme=Tradimo())
# browser = OptBrowser(b, result)
# browser.start()

#Analyzer methods
strategy = results[0]
df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), FOLDERNAME)
df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), FOLDERNAME)
df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), FOLDERNAME)

# strategies = [x[0][0] for x in results]
# for strategy in enumerate(strategies):
#     df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), folderName)
#     df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), folderName)
#     df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), folderName)


