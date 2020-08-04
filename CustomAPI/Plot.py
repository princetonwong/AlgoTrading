from CustomAPI.Draw import Draw
from CustomAPI.Helper import Helper
import matplotlib.pyplot as pyplot
import numpy as np
import os

class Plot():
    def __init__(self):
        self.filename = ""

    @staticmethod
    def showPNG():
        pyplot.show()

    @staticmethod
    def closePlot():
        pyplot.close()

    def savePNG(self, prefix=""):
        path = Helper().getOutputFolderPath()
        pyplot.savefig(os.path.join(path, prefix + self.filename + ".png"), dpi=100)

class SummaryPlot(Plot):
    def __init__(self, summary):
        self.summary = summary
        self.filename = summary.filename

    def plotProfitPerOrderHistogram(self):
        import scipy.stats as st
        pyplot.close()
        x = self.summary.orders["profitPerOrder"].dropna()
        pyplot.hist(x, density=True, bins=40, label="Data")
        mn, mx = pyplot.xlim()
        pyplot.xlim(mn, mx)
        kde_xs = np.linspace(mn, mx, 301)
        kde = st.gaussian_kde(x)
        pyplot.plot(kde_xs, kde.pdf(kde_xs), label="PDF")
        pyplot.legend(loc="upper left")
        pyplot.ylabel('Probability')
        pyplot.xlabel('Data')
        pyplot.title("Histogram")

class BacktestPlot(Plot):
    def __init__(self, backtest):
        self.filename = backtest.filename
        self.backtest = backtest
        pyplot.close()
        figure = pyplot.figure(1, figsize=(25, 10), dpi=100, frameon=False)
        self.mainAxis = self.plotKLine(MA= False, BBANDS= True)

    def plotAnalytics(self):
        df = self.backtest.model.data
        pyplot.figure(2, figsize=(20, 10))
        pyplot.title('Strategy Performance', fontsize=18)
        pyplot.plot(df.index, df["CumulativeReturn"])
        pyplot.plot(df.index, df['close'] / df['close'][0])
        pyplot.legend(['CCI', self.filename], fontsize=14)



    def plotKLine(self, MA=False, BBANDS=False):
        mainAxis = pyplot.subplot2grid((7, 1), (0, 0), rowspan=3, colspan=1)
        mainAxis.set_xlim(0, self.backtest.count + 1)
        mainAxis.set_title(self.backtest.filename)
        Draw().KLine(dataFrame=self.backtest.model.data, axis=mainAxis)
        Draw().OrderPlaced(df=self.backtest.model.data, axis=mainAxis)
        if MA:
            Draw().MA(self.backtest.model.data, mainAxis)
        if BBANDS:
            Draw().BBANDS(self.backtest.model.data, mainAxis)
        return mainAxis

    def plotMACD(self, drawCrossOnKLine=False):
        axis2 = pyplot.subplot2grid((7, 1), (3, 0), rowspan=1, colspan=1, sharex=self.mainAxis)
        axis2.set_xlim(0, self.backtest.count + 1)
        axis2.set_yticks([self.backtest.macdThreshold, -self.backtest.macdThreshold])
        axis2.axhline(self.backtest.macdThreshold, color='r')
        axis2.axhline(-self.backtest.macdThreshold, color='r')
        Draw().MACD(dataFrame=self.backtest.model.data, axis=axis2)
        Draw().MACDCross(dataFrame=self.backtest.model.data, axis=axis2)
        if drawCrossOnKLine:
            Draw().MACDCrossOnKLine(dataFrame=self.backtest.model.data, macdThreshold=self.backtest.macdThreshold, axis=self.mainAxis)

    def plotSLOWKD(self):
        axis = pyplot.subplot2grid((7, 1), (4, 0), rowspan=1, colspan=1, sharex=self.mainAxis)
        axis.set_xlim(0, self.backtest.count + 1)
        axis.axhline(50 + self.backtest.slowkdThreshold, color='r')
        axis.axhline(50 - self.backtest.slowkdThreshold, color='r')
        Draw().SLOWKD(self.backtest.model.data, axis=axis)
        Draw().SLOWKDCross(self.backtest.model.data, axis=axis)

    def plotVolume(self):
        axis3 = pyplot.subplot2grid((7, 1), (5, 0), rowspan=1, colspan=1, sharex=self.mainAxis)
        axis3.set_xlim(0, self.backtest.count + 1)
        Draw().Volume(dataFrame=self.backtest.model.data, axis=axis3)

    def plotCCI(self, drawCrossOnKline=False):
        axis = pyplot.subplot2grid((7, 1), (6, 0), rowspan=1, colspan=1, sharex=self.mainAxis)
        axis.set_xlim(0, self.backtest.count + 1)
        axis.axhline(self.backtest.cciThreshold, color='r')
        axis.axhline(-self.backtest.cciThreshold, color='g')
        Draw().CCI(dataFrame=self.backtest.model.data, axis=axis)
        Draw().CCICross(self.backtest.model.data, axis)
        if drawCrossOnKline:
            Draw().CCICross(dataFrame=self.backtest.model.data, axis=self.mainAxis)

