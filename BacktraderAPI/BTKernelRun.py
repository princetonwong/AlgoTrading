from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTObserver, BTCommInfo, BTScreener
from BacktraderAPI.BTDataFeed import DataFeedSource

class BTCoreRun:
    helper = Helper()
    defaultAllParams = dict(INITIALCASH=50000,
                            SYMBOL="HK.MHImain",
                            SUBTYPE=SubType.K_1M,
                            TIMERANGE=("2020-06-21", "00:00:00", "2020-09-23", "23:59:00"),
                            # TODO: Create CSV Writer to store Stock Info
                            STRATEGYNAME=BTStrategy.PSARStrategy,
                            STRATEGYPARAMS=dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6,
                                                        trailHold=1, stopLossPerc=0.016),
                            REMARKS="WithStopLoss",
                            )

    defaultStrategyParams = dict(STRATEGY = BTStrategy.EmptyStrategy,
                                 STRATEGYPARAMS = dict()
                                 )


    def __init__(self, allParams, strategyParams, isOptimization = False, isScreening = False):
        self.cerebro = bt.Cerebro()

        self.allParams = allParams or self.defaultAllParams
        self.strategyParams = strategyParams or self.defaultStrategyParams

        self.isOptimization = isOptimization
        self.isScreening = isScreening

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

    def setFolderName(self):
        if self.isOptimization:
            self.folderName = "[Opt]" + self.helper.initializeFolderName(self.symbol, self.subType,
                                                                         self.timerange,
                                                                         self.strategyName,
                                                                         self.strategyParams,
                                                                         self.remarks)
        elif self.isScreening:
            self.folderName = "[Screen]" + self.helper.initializeFolderName(self.symbol, self.subType,
                                                                         self.timerange,
                                                                         self.strategyName,
                                                                         self.strategyParams,
                                                                         self.remarks)
        else:
            self.folderName = self.helper.initializeFolderName(self.symbol, self.subType, self.timerange, self.strategyName, self.strategyParams, self.remarks)

    def loadData(self, datafeedSource: DataFeedSource = None):
        self.datafeedSource = datafeedSource or self.datafeedSource

        if self.datafeedSource == DataFeedSource.Yahoo:
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
            self.cerebro.addwriter(bt.WriterFile, csv=writeCSV, out= self.helper.generateFilePath("BackTraderData", ".csv"),
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

    def addStrategy(self, addStrategyParams):
        self.addStrategyParams = addStrategyParams["STRATEGYPARAMS"]
        print(f"Strategy parameters are: {self.addStrategyParams}")
        print(f"Optimization is: {self.isOptimization}")
        self.cerebro.addstrategy(self.strategyName, **self.addStrategyParams)

    def addAnalyzer(self):
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                                     annualize=True, _name="sharperatio")
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        self.cerebro.addanalyzer(BTAnalyzer.Kelly, _name="kelly")
        self.cerebro.addanalyzer(bt.analyzers.VWR, _name="vwr")
        self.cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Minutes, _name="timereturn")

    def addScreener(self):
        self.cerebro.addanalyzer(BTScreener.MyScreener, _name="screener_sma")

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
        b = Bokeh(filename=self.helper.generateFilePath("Report", ".html"), style='bar', plot_mode='single',
                  scheme=Tradimo())
        self.cerebro.plot(b, iplot=False)

    def plotIPython(self):
        figs = self.cerebro.plot(style="candle", iplot=False, subtxtsize=6, maxcpus=1, show=False)

        if self.isOptimization is False:
            self.helper.saveFig(figs)

    def getAnalysisResults(self, quantStats=False):
        strategy = self.results[0]
        taAnalyzer = strategy.analyzers.ta.get_analysis()
        sharpeRatioAnalyzer = strategy.analyzers.sharperatio.get_analysis()
        drawdownAnalyzer = strategy.analyzers.drawdown.get_analysis()
        sqnAnalyzer = strategy.analyzers.sqn.get_analysis()
        returnAnalyzer = strategy.analyzers.returns.get_analysis()
        vwrAnalyzer = strategy.analyzers.vwr.get_analysis()
        transactionsAnalyzer = strategy.analyzers.transactions.get_analysis()
        timeReturnAnalyzer = strategy.analyzers.timereturn.get_analysis()

        taAnalyzerDF = BTAnalyzer.getTradeAnalysisDf(taAnalyzer)
        sqnDF = BTAnalyzer.getSQNDf(sqnAnalyzer)
        drawdownDF = BTAnalyzer.getDrawDownDf(drawdownAnalyzer)
        sharpeRatioDF = BTAnalyzer.getSharpeRatioDf(sharpeRatioAnalyzer)
        vwrDF = BTAnalyzer.getVWRDf(vwrAnalyzer)
        returnDF = BTAnalyzer.getReturnDf(returnAnalyzer)
        cashDF = pd.Series([self.initialCash, self.finalPortfolioValue], index=["Initial Cash", "Final Portfolio Value"])
        kellyDF = pd.Series([strategy.analyzers.kelly.get_analysis().kellyPercent], index=["Kelly Percent"])
        transactionsDF = BTAnalyzer.getTransactionsDf(transactionsAnalyzer)
        timeReturnDF = BTAnalyzer.getTimeReturnDf(timeReturnAnalyzer)

        statsDF = pd.concat([taAnalyzerDF,cashDF,returnDF,sqnDF,sharpeRatioDF,vwrDF,drawdownDF,kellyDF])

        if self.isOptimization is False:
            self.helper.outputXLSX(statsDF, "Statistics")
            self.helper.outputXLSX(transactionsDF, "Transactions")
            self.helper.outputXLSX(timeReturnDF, "TimeReturn")

            if quantStats: #TODO: Fix
                import quantstats as qs
                qs.extend_pandas()
                qs.stats.sharpe(timeReturnDF)
                # qs.plots.snapshot(timeReturnDF, title='Facebook Performance')
                qs.reports.html(timeReturnDF, output="qs.html")
            #     stock.sharpe()

        self.stats = {
            "Symbol" : self.symbol,
            "SubType": self.subType,
            "Sharpe Ratio": statsDF['Sharpe Ratio'],
            "Average Return": statsDF['Average Return'],
            "Annualized Return": statsDF['Annualized Return%'],
            "Max DrawDown": statsDF['Max DrawDown'],
            "Total Open": statsDF["Total Open"],
            "Total Closed": statsDF["Total Closed"],
            "Total Won": statsDF["Total Won"],
            "Total Lost": statsDF["Total Lost"],
            "Win Streak": statsDF["Win Streak"],
            "Lose Streak": statsDF["Losing Streak"],
            "PnL Net": statsDF["PnL Net"],
            "Strike Rate": statsDF["Strike Rate"],
            "SQN": statsDF["SQN"],
            "VWR": statsDF["VWR"],
            "Kelly Percent": statsDF["Kelly Percent"]
        }
        return {**self.strategyParams, **self.stats}

    def getScreeningResults(self):
        strategy = self.results[0]
        smaScreenerAnalysis = strategy.analyzers.screener_sma.get_analysis()
        smaScreenerResults = BTScreener.MyScreener().getScreenerDf(smaScreenerAnalysis)

        self.stats = {
            "Symbol": self.symbol,
            **smaScreenerResults,
        }
        return {**self.stats}

    def runOneStrategy(self, strategyParams, SLTP=False):
        self.setFolderName()
        self.loadData()
        self.addWriter(writeCSV=True)
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy(addStrategyParams=strategyParams)
        self.addAnalyzer()
        self.addObserver(SLTP=SLTP)
        self.run()
        self.plotBokeh()
        # self.plotIPython()
        return self.getAnalysisResults(quantStats=False)

    def runDayTradeOption(self, strategyParams, SLTP=False):
        self.setFolderName()
        self.loadData(datafeedSource=DataFeedSource.YahooOption)
        self.addWriter(writeCSV=True)
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy(addStrategyParams=strategyParams)
        # self.addAnalyzer()
        self.addObserver(SLTP=SLTP)
        self.run()
        self.plotBokeh()
        # self.plotIPython()
        return self.getAnalysisResults(quantStats=False)

    def runOptimizationWithSameData(self, strategyParams):
        self.setFolderName()
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy(addStrategyParams=strategyParams)
        self.addAnalyzer()
        self.addObserver(SLTP=False)
        self.run()
        return self.getAnalysisResults(quantStats=False)

    def runScreening(self, strategyParams):
        self.strategyName = BTStrategy.EmptyStrategy
        self.addWriter(writeCSV=True)
        self.addBroker()
        self.addStrategy(addStrategyParams=strategyParams)
        self.addScreener()
        self.run()
        # self.plotBokeh()
        # self.plotIPython()
        return self.getScreeningResults()

