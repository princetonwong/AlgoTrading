from CustomAPI.Backtest import *
from CustomAPI.Plot import *
from CustomAPI.BacktestSummary import *
import pandas as pd

class Execution():
    def __init__(self, symbols, subtypes, timeRange=None):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.analytics = pd.DataFrame()
        self.summaries = []
        self.description = ', '.join(symbols[0:2]) + " " + ', '.join(subtypes[0:2])
        self.backtests = []

        for symbol in symbols:
            for subtype in subtypes:
                backtest, data = self.downloadBacktestData(symbol, subtype, timeRange)
                self.backtests.append(backtest)


    def runBatchTests(self, bbandsParameters=(20, 2, 2), maParameters=(5, 10, 20, 60),
                      cciParameters=(20, 0.015, 100, 7), macdParameters=(5, 35, 5), slowkdParameters=(9, 3, 3)):
        newBacktests = []
        for backtest in self.backtests:
            backtest = self.runBacktest(backtest, bbandsParameters, maParameters, cciParameters, macdParameters, slowkdParameters)
            newBacktests.append(backtest)

        self.backtests = newBacktests

    def runSummary(self, feePerOrder):
        for backtest in self.backtests:
            summary = BacktestSummary(backtest, feePerOrder= feePerOrder)
            self.summaries.append(summary)
            self.analytics = pd.concat([summary.analytics, self.analytics])
        return self.summaries

    @staticmethod
    def downloadBacktestData(symbol, subtype, timeRange=None):
        backtest = Backtest(symbol, subtype)
        data = backtest.obtainDataFromFutu(timeRange)
        return backtest, data

    ## Details
    @staticmethod
    def runBacktest(backtest: Backtest, bbandsParameters, maParameters, cciParameters,
                    macdParameters, slowkdParameters):
        backtest.runBBANDS(bbandsParameters)
        # backtest.runMA(maParameters)
        backtest.runMACD(macdParameters, tIndex=-2)
        backtest.runSLOWKD(slowkdParameters)
        backtest.runCCI(cciParameters)
        backtest.orderBy(CCI=True)
        return backtest


    #Plotting
    def plotTimeSeries(self):
        for backtest in self.backtests:
            plotting = BacktestPlot(backtest)
            # plotting.plot(MACD=True, SLOWKD=True, Volume=True, CCI=True)
            plotting.plotMACD()
            plotting.plotSLOWKD()
            plotting.plotVolume()
            plotting.plotCCI()
            plotting.savePNG("KLine---")
            # plotting.showPNG()
            plotting.closePlot()

    def plotCumulativeReturn(self):
        for backtest in self.backtests:
            plotting = BacktestPlot(backtest)
            plotting.plotAnalytics()
            plotting.savePNG("Cum_Return---")
            # plotting.showPNG()
            plotting.closePlot()

    def plotDailyReturnHistogram(self):
        for summary in self.summaries:
            plotting = SummaryPlot(summary)
            plotting.plotProfitPerOrderHistogram()
            plotting.savePNG("Histogram---")
            # plotting.showPNG()
            plotting.closePlot()

   # Output
    def outputAnalyticsXLSX(self):
        filename = "Summary---{} {}.xlsx".format(self.description, self.timestamp)
        subset = ["CumulativeReturn", "DailyWinRate", "ProfitBeforeFee", "SharpeRatio"]
        return Helper().gradientAppliedXLSX(self.analytics.reset_index(drop= True), filename, subset)

    def outputOrdersXLSX(self):
        for summary in self.summaries:
            filename = "Orders---{} {}.xlsx".format(summary.filename, self.timestamp)
            subset = ["holding", "orderPlaced", "macdScore", "slowkdScore", "CCIScore", "open", "close",
                      "profitPerOrder"]
            Helper().gradientAppliedXLSX(summary.orders.sort_values("time_key"), filename, subset)

    def outputModelDataXLSX(self):
        for backtest in self.backtests:
            filename = "Data---{} {}.xlsx".format(backtest.filename, self.timestamp)
            subset = ["holding", "orderPlaced", "macdScore", "slowkdScore", "CCIScore", "open", "close", "ZScore"]
            Helper().gradientAppliedXLSX(backtest.model.data, filename, subset)







