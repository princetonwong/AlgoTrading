import pandas as pd
import backtrader as bt


class _ScreenerBase(bt.Analyzer):
    def getScreenerDf(self, analysis):
        self.index = list()
        self.result = list()
        resultDF = pd.Series(self.result, index=self.index)
        return resultDF


class DataNameCloseScreener(_ScreenerBase):
    def stop(self):
        super(DataNameCloseScreener, self).stop()
        self.rets.dataName = self.data._name
        self.rets.close = self.data.close[0]

    def getScreenerDf(self, analysis):
        super(DataNameCloseScreener, self).getScreenerDf(analysis)
        dataName = analysis.dataName
        close = round(analysis.close, 2)
        self.index.append("Data Name")
        self.index.append("Close")
        self.result.append(dataName)
        self.result.append(close)

        resultDF = pd.Series(self.result, index=self.index)
        return resultDF


class SMAScreener(_ScreenerBase):
    params = dict(period=10)

    def start(self):
        super(SMAScreener, self).start()
        self.sma = bt.indicators.SMA(self.data, period=self.p.period)

    def stop(self):
        super(SMAScreener, self).stop()
        self.rets.sma = self.sma[0]

        if self.data > self.sma:
            self.rets.SMASignal = 1
        else:
            self.rets.SMASignal = 0

    def getScreenerDf(self, analysis):
        super(SMAScreener, self).getScreenerDf(analysis)
        SMA = round(analysis.sma, 2)
        SMASignal = analysis.SMASignal
        self.index.append("SMA")
        self.index.append("SMASignal")
        self.result.append(SMA)
        self.result.append(SMASignal)

        resultDF = pd.Series(self.result, index=self.index)

        return resultDF
