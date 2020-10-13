import pandas as pd
import backtrader as bt


class _ScreenerBase(bt.Analyzer):
    def getScreenerResultsDf(self):
        self.index = list()
        self.result = list()
        self.resultDF = pd.Series()

        return self.resultDF

    def updateResultDF(self):
        resultDF = pd.Series(self.result, index=self.index)


class DataNameCloseScreener(_ScreenerBase):
    def stop(self):
        super(DataNameCloseScreener, self).stop()
        self.rets.dataName = self.data._name
        self.rets.close = self.data.close[0]

        print(self.rets)

    def getScreenerResultsDf(self):
        super(DataNameCloseScreener, self).getScreenerResultsDf()
        dataName = self.get_analysis().dataName
        close = round(self.get_analysis().close, 2)
        self.index += ["Data Name", "Close"]
        self.result += [dataName, close]

        self.updateResultDF()
        return self.resultDF


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

    def getScreenerResultsDf(self):
        super(SMAScreener, self).getScreenerResultsDf()

        SMA = round(self.get_analysis().sma, 2)
        SMASignal = self.get_analysis().SMASignal
        self.index += ["SMA", "SMASignal"]
        self.result += [SMA, SMASignal]

        resultDF = pd.Series(self.result, index=self.index)

        return resultDF
