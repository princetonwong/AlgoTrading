from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper; h = Helper()
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTObserver, BTCommInfo, BTScreener
from BacktraderAPI.BTDataFeed import DataFeedSource

class BTKernelRun:
    defaultAllParams = dict(INITIALCASH=50000,
                            SYMBOL="HK.MHImain",
                            SUBTYPE=SubType.K_1M,
                            TIMERANGE=("2020-06-21", "00:00:00", "2020-09-23", "23:59:00"),
                            REMARKS="WithStopLoss",
                            )

    defaultStrategyParams = dict(STRATEGY = BTStrategy.EmptyStrategy,
                                 STRATEGYPARAMS = dict()
                                 )


    def __init__(self, allParams, strategyParams, isOptimization = False, isScreening = False, isDifferentData = False):
        self.cerebro = bt.Cerebro()

        self.allParams = allParams or self.defaultAllParams
        self.strategyParams = strategyParams or self.defaultStrategyParams

        self.isOptimization = isOptimization
        self.isScreening = isScreening
        self.isDifferentData = isDifferentData

        self.initialCash = self.allParams["INITIALCASH"]
        self.symbol = self.allParams["SYMBOL"]
        self.subType = self.allParams["SUBTYPE"]
        self.timerange = self.allParams["TIMERANGE"]
        self.remarks = self.allParams["REMARKS"]

        self.strategyName = self.strategyParams["STRATEGYNAME"]
        self.strategyParams = self.strategyParams["STRATEGYPARAMS"]

        if "." in self.symbol:
            self.datafeedSource = DataFeedSource.FutuFuture
        else:
            self.datafeedSource = DataFeedSource.Yahoo

        self.folderName = ""

    def setFolderName(self, symbols):
        if self.isOptimization:
            prefix = "Optimization"
        elif self.isScreening:
            prefix = "Screen"
            self.strategyName = BTStrategy.EmptyStrategy
        else:
            prefix = "RunOnce"

        if self.isDifferentData:
            prefix = prefix + ",DiffData"
        else:
            prefix = prefix + ",SameData"

        self.folderName = h.initializeFolderName(symbols, self.subType, self.timerange, self.strategyName,
                                                           self.strategyParams, self.remarks, prefix= prefix)
        return self.folderName

    def loadData(self, datafeedSource: DataFeedSource = None):
        self.datafeedSource = datafeedSource or self.datafeedSource

        if self.datafeedSource == DataFeedSource.Yahoo:
            # if self.isOptimization == True:
            #     self.data0 = BTDataFeed.getYahooDataFeeds([self.symbol], self.subType, self.timerange)
            # else:
                self.data0 = BTDataFeed.getYahooDataFeeds([self.symbol], self.subType, self.timerange, folderName=self.folderName)
                
        elif self.datafeedSource == DataFeedSource.YahooOption:
            self.data0 = BTDataFeed.getYahooDataFeeds([self.symbol], self.subType, self.timerange, period="1d", folderName=None)
        elif self.datafeedSource == DataFeedSource.Futu:
            self.data0 = BTDataFeed.getFutuDataFeed(self.symbol, self.subType, self.timerange, self.folderName)
        elif self.datafeedSource == DataFeedSource.FutuFuture:
            self.data0 = BTDataFeed.getFutuDataFeed(self.symbol, self.subType, self.timerange, self.folderName)
        elif self.datafeedSource == DataFeedSource.AlphaVantage:
            self. data0 = BTDataFeed.getAlphaVantageDataFeeds([self.symbol], compact=False, debug=False, fromdate=datetime(2019, 9, 10), todate=datetime(2019, 9, 18))[0] #TODO: Amend Timerange
        elif self.datafeedSource == DataFeedSource.QuandlWiki:
            self.data0 = BTDataFeed.getHDFWikiPriceDataFeed([self.symbol], startYear= "2016")

        self.cerebro.adddata(self.data0, name=self.symbol)

    def addWriter(self, writeCSV = False):
        if self.isOptimization is False:
            self.cerebro.addwriter(bt.WriterFile, csv=writeCSV, out= h.generateFilePath("BackTraderData", ".csv"),
                              rounding=3)
        else:
            self.cerebro.addwriter(bt.WriterFile, rounding=3)

    def addDataFilter(self, filter):
        self.data0.addfilter(filter(self.data0))

    def addSizer(self, sizer):
        self.cerebro.addsizer(sizer)

    def addBroker(self):
        self.cerebro.broker.setcash(self.initialCash)
        if self.datafeedSource == DataFeedSource.FutuFuture and self.symbol == "HK.MHImain":
            self.cerebro.broker.addcommissioninfo(BTCommInfo.FutuHKIMainCommInfo())
        print('Starting Portfolio Value: %.2f' % self.cerebro.broker.getvalue())

    def addStrategy(self, strategyParams):
        self.addStrategyParams = strategyParams["STRATEGYPARAMS"] or self.strategyParams
        print(f"Strategy parameters are: {self.addStrategyParams}")
        print(f"Optimization is: {self.isOptimization}")
        self.cerebro.addstrategy(self.strategyName, **self.addStrategyParams)


    def addObserver(self, SLTP=False):
        self.cerebro.addobserver(bt.observers.DrawDown)
        self.cerebro.addobserver(bt.observers.Trades)
        self.cerebro.addobserver(bt.observers.Broker)
        self.cerebro.addobserver(BTObserver.BuySellStop)
        self.cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.01)
        self.cerebro.addobserver(bt.observers.TimeReturn)
        if SLTP:
            self.cerebro.addobserver(BTObserver.SLTPTracking)

    def run(self):
        self.results = self.cerebro.run(stdstats=False, runonce=False)
        self.finalPortfolioValue = self.cerebro.broker.getvalue()
        print('Final Portfolio Value: %.2f' % self.finalPortfolioValue)

    def plotBokeh(self):
        from backtrader_plotting import Bokeh
        from backtrader_plotting.schemes import Tradimo
        b = Bokeh(filename=h.generateFilePath("Report", ".html"), style='bar', plot_mode='single',
                  scheme=Tradimo())
        self.cerebro.plot(b, iplot=False)

    def plotIPython(self):
        figs = self.cerebro.plot(style="candle", iplot=False, subtxtsize=6, maxcpus=1, show=False)

        if self.isOptimization is False:
            h.saveFig(figs)

    def addAnalyzer(self):
        self.cerebro.addanalyzer(BTAnalyzer.SharpeRatio)
        self.cerebro.addanalyzer(BTAnalyzer.Returns)
        self.cerebro.addanalyzer(BTAnalyzer.SQN)
        self.cerebro.addanalyzer(BTAnalyzer.Kelly)
        self.cerebro.addanalyzer(BTAnalyzer.VWR)
        self.cerebro.addanalyzer(BTAnalyzer.Returns)
        self.cerebro.addanalyzer(BTAnalyzer.TradeAnalyzer)
        self.cerebro.addanalyzer(BTAnalyzer.DrawDown)

        self.cerebro.addanalyzer(BTAnalyzer.Transactions)
        self.cerebro.addanalyzer(BTAnalyzer.TimeReturn)

    def getAnalysisResults(self, quantStats=False):
        strategy = self.results[0]
        tradeAnalyzerDF = strategy.analyzers.tradeanalyzer.getAnalyzerResultsDf()
        cashDF = pd.Series([self.initialCash, self.finalPortfolioValue],
                           index=["Initial Cash", "Final Portfolio Value"])
        sharpeRatioDF = strategy.analyzers.sharperatio.getAnalyzerResultsDf()
        drawdownDF = strategy.analyzers.drawdown.getAnalyzerResultsDf()
        sqnDF = strategy.analyzers.sqn.getAnalyzerResultsDf()
        returnDF = strategy.analyzers.returns.getAnalyzerResultsDf()
        vwrDF = strategy.analyzers.vwr.getAnalyzerResultsDf()
        kellyDF = strategy.analyzers.kelly.getAnalyzerResultsDf()

        self.statisticsDF = pd.concat([tradeAnalyzerDF, cashDF, returnDF, sqnDF, sharpeRatioDF, vwrDF, drawdownDF, kellyDF])

        self.transactionsDF = strategy.analyzers.transactions.getAnalyzerResultsDf()
        self.timeReturnDF = strategy.analyzers.timereturn.getAnalyzerResultsDf()


        if self.isOptimization is False:
            h.outputXLSX(self.statisticsDF, "Statistics")
            h.outputXLSX(self.transactionsDF, "Transactions")
            h.outputXLSX(self.timeReturnDF, "TimeReturn")

            if quantStats:
                BTAnalyzer.getQuantStatsReport(h, self.timeReturnDF)

        self.stats = {
            "Symbol" : self.symbol,
            "SubType": self.subType,
            "Sharpe Ratio": self.statisticsDF['Sharpe Ratio'],
            "Average Return": self.statisticsDF['Average Return'],
            "Annualized Return": self.statisticsDF['Annualized Return%'],
            "Max DrawDown": self.statisticsDF['Max DrawDown'],
            "Total Open": self.statisticsDF["Total Open"],
            "Total Closed": self.statisticsDF["Total Closed"],
            "Total Won": self.statisticsDF["Total Won"],
            "Total Lost": self.statisticsDF["Total Lost"],
            "Win Streak": self.statisticsDF["Win Streak"],
            "Lose Streak": self.statisticsDF["Losing Streak"],
            "PnL Net": self.statisticsDF["PnL Net"],
            "Strike Rate": self.statisticsDF["Strike Rate"],
            "SQN": self.statisticsDF["SQN"],
            "VWR": self.statisticsDF["VWR"],
            "Kelly Percent": self.statisticsDF["Kelly Percent"]
        }
        return {**self.strategyParams, **self.stats}

    def addScreener(self, screener):
        self.cerebro.addanalyzer(screener, _name="myscreener")

    def getScreeningResults(self):
        strategy = self.results[0]
        myScreenerResults = strategy.analyzers.myscreener.getScreenerResultsDf()

        return myScreenerResults

    #Usage Method

    # def runOneStrategy(self, strategyParams, SLTP=False):
    #     self.setFolderName()
    #     self.loadData()
    #     self.addWriter(writeCSV=True)
    #     self.addSizer(sizer=BTSizer.FixedSizer)
    #     self.addBroker()
    #     self.addStrategy(addStrategyParams=strategyParams)
    #     self.addAnalyzer()
    #     self.addObserver(SLTP=SLTP)
    #     self.run()
    #     # self.plotBokeh()
    #     # self.plotIPython()
    #     self.getAnalysisResults(quantStats=True)
    #     return
    #
    def runDayTradeOption(self, strategyParams, SLTP=False):
        self.setFolderName()
        self.loadData(datafeedSource=DataFeedSource.YahooOption)
        self.addWriter(writeCSV=True)
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy(strategyParams)
        self.addObserver(SLTP=SLTP)
        self.addDataFilter(bt.filters.HeikinAshi)
        self.run()
        self.plotBokeh()
        return self.getAnalysisResults(quantStats=False)
    #
    # def runOptimizationWithSameData(self, strategyParams):
    #     self.setFolderName()
    #     self.addSizer(sizer=BTSizer.FixedSizer)
    #     self.addBroker()
    #     self.addStrategy(addStrategyParams=strategyParams)
    #     self.addAnalyzer()
    #     self.addObserver(SLTP=False)
    #     self.run()
    #     self.getAnalysisResults(quantStats=False)
    #     return
    #
    # def runScreening(self, strategyParams):
    #     self.strategyName = BTStrategy.EmptyStrategy
    #     self.addWriter(writeCSV=True)
    #     self.addBroker()
    #     self.addStrategy(addStrategyParams=strategyParams)
    #     self.addScreener()
    #     self.run()
    #     # self.plotBokeh()
    #     self.getScreeningResults()
    #     return


