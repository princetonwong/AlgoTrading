import pandas as pd
import backtrader as bt
import BacktraderAPI.BTStrategy as BTStrategy

class _ScreenerBase(bt.Analyzer):
    def getScreenerResultsDf(self):
        self.index = list()
        self.result = list()
        self.resultDF = pd.Series()

        return self.resultDF

    def updateResultDF(self):
        self.resultDF = pd.Series(self.result, index=self.index)


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

        self.updateResultDF()
        return self.resultDF

class RSIScreener(_ScreenerBase):
    params = dict(period=21, rsiUpperband=60, rsiLowerband=40)

    def start(self):
        super(RSIScreener, self).start()
        self.rsi = bt.ind.RSI(self.data, period=self.p.period)

    def stop(self):
        super(RSIScreener, self).stop()
        self.rets.rsi = self.rsi[0]

        if self.rsi < self.p.rsiUpperband:
            self.rets.RSISignal = 1
        elif self.rsi > self.p.rsiLowerband:
            self.rets.RSISignal = -1
        else:
            self.rets.RSISignal = 0

    def getScreenerDf(self):
        super(RSIScreener, self).getScreenerDf()
        rsi = round(self.get_analysis().rsi, 2)
        rsiSignal = self.get_analysis().RSISignal
        self.index += ["RSI", "RSISignal"]
        self.result += [rsi, rsiSignal]

        self.updateResultDF()
        return self.resultDF

class MACDScreener(_ScreenerBase):
    params = dict(macdFast=12, macdSlow=26, diffPeriod=9)

    def start(self):
        super(MACDScreener, self).start()
        self.macd = bt.indicators.MACD(period_me1=self.p.macdFast,
                                       period_me2=self.p.macdSlow,
                                       period_signal=self.p.diffPeriod, subplot=False)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal, subplot=False)

    def stop(self):
        super(MACDScreener, self).stop()
        self.rets.macd = self.macd[0]

        if self.mcross == 1:
            self.rets.macdSignal = 1
        elif self.mcross == -1:
            self.rets.macdSignal = -1
        else:
            self.rets.macdSignal = 0

    def getScreenerDf(self):
        super(MACDScreener, self).getScreenerDf()
        macd = round(self.get_analysis().macd, 3)
        macdSignal = self.get_analysis().macdSignal
        self.index += ["MACD", "MACDSignal"]
        self.result += [macd, macdSignal]

        self.updateResultDF()
        return self.resultDF