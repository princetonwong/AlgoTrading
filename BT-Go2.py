from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_30M
CCIPARAMETERS = (26, 0.015, 100 ,7)
TIMERANGE = ("2020-01-01", "00:00:00", "2020-03-31", "16:31:00")
# TIMERANGE = None

folderName = "{}-{}-{}".format(SYMBOL, SUBTYPE, Helper().get_timestamp())

#Init
cerebro = bt.Cerebro()

cerebro.addwriter(bt.WriterFile, csv=True, out=Helper().getWriterOutputPath(folderName), rounding=2)

#Data Feed
data = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE)
# data = BTDataFeed.getHDFWikiPriceDataFeed(["TSLA"], startYear= "2016")
cerebro.adddata(data)

#Data Filter
data.addfilter(bt.filters.HeikinAshi(data))

#Sizer
cerebro.addsizer(BTSizer.PercentSizer, percents= 50)

#Strategy
cerebro.addstrategy(BTStrategy.CCICrossStrategyWithSLOWKDExit)

#Broker
cerebro.broker.setcash(30000.0)
cerebro.broker.setcommission(commission=0.0004)
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

#Analyzer
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")

#Run
strategies = cerebro.run(stdstats = True)
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

#Analyzer methods
strategy = strategies[0]
df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), folderName)
df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), folderName)
df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), folderName)

#Plotting
figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1)
Helper().saveFig(figs, folderName)


# PyFolio Analyzer (deprecated)
# cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")
def usePyfolio():
    global returns, positions
    pyfoliozer = strategy.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    # returns.index = returns.index.tz_convert(None)
    # positions.index = positions.index.tz_convert(None)
    # transactions.index = transactions.index.tz_convert(None)
    import pyfolio as pf
    fig = pf.create_returns_tear_sheet(
        returns,
        positions=positions,
        transactions=transactions,
        return_fig=True
    )
    # this makes plots not appear in a window
    import matplotlib
    matplotlib.use('Agg')
    fig.savefig('pyfolio_returns_tear_sheet.pdf')
# usePyfolio()

