import pandas as pd
import backtrader as bt
import BacktraderAPI.BTStrategy as BTStrategy

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

    def getScreenerDf(self, analysis):
        super(RSIScreener, self).getScreenerDf(analysis)
        rsi = round(analysis.rsi, 2)
        rsiSignal = analysis.RSISignal
        self.index.append("RSI")
        self.index.append("RSISignal")
        self.result.append(rsi)
        self.result.append(rsiSignal)

        resultDF = pd.Series(self.result, index=self.index)

        return resultDF

class MACDScreener(_ScreenerBase):
    params = dict(macdFast=12, macdSlow=26, diffPeriod=9)

    def start(self):
        super(MACDScreener, self).start()
        # macdSB = BTStrategy.MACDStrategyBase()
        # self.macd = macdSB.macd
        # self.mcross = macdSB.mcross
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

    def getScreenerDf(self, analysis):
        super(MACDScreener, self).getScreenerDf(analysis)
        macd = round(analysis.macd, 2)
        macdSignal = analysis.macdSignal
        self.index.append("MACD")
        self.index.append("MACDSignal")
        self.result.append(macd)
        self.result.append(macdSignal)

        resultDF = pd.Series(self.result, index=self.index)

        return resultDF