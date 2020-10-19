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

    def getScreenerResultsDf(self):
        super(RSIScreener, self).getScreenerResultsDf()
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

    def getScreenerResultsDf(self):
        super(MACDScreener, self).getScreenerResultsDf()
        macd = round(self.get_analysis().macd, 3)
        macdSignal = self.get_analysis().macdSignal
        self.index += ["MACD", "MACDSignal"]
        self.result += [macd, macdSignal]

        self.updateResultDF()
        return self.resultDF

class IchimokuScreener(_ScreenerBase):
    params = dict(kijun=26, tenkan=9, chikou=26, senkou=52, senkou_lead=26)

    def start(self):
        super(IchimokuScreener, self).start()
        self.ichimoku = bt.indicators.Ichimoku(kijun=self.p.kijun,
                                               tenkan=self.p.tenkan,
                                               chikou=self.p.chikou,
                                               senkou=self.p.senkou,
                                               senkou_lead=self.p.senkou_lead
                                               )
        self.tenkanXKijun = bt.indicators.CrossOver(self.ichimoku.tenkan_sen, self.ichimoku.kijun_sen)
        self.XKijun = bt.indicators.CrossOver(self.data, self.ichimoku.kijun_sen)
        self.XSenkouA = bt.indicators.CrossOver(self.data, self.ichimoku.senkou_span_a)
        self.XSenkouB = bt.indicators.CrossOver(self.data, self.ichimoku.senkou_span_b)
        self.cloud = self.ichimoku.senkou_span_a - self.ichimoku.senkou_span_b
        self.tenkanGreaterKijun = self.ichimoku.tenkan_sen - self.ichimoku.kijun_sen

    def stop(self):
        super(IchimokuScreener, self).stop()
        self.rets.ichimoku = self.ichimoku[0]
        self.rets.ichimokuSignal = 0

        if self.tenkanGreaterKijun > 0:
            if (self.cloud > 0 and self.data > self.ichimoku.senkou_span_a) or (
                    self.cloud < 0 and self.data > self.ichimoku.senkou_span_b):
                if self.tenkanXKijun == 1 or self.XSenkouB == 1:
                    self.rets.ichimokuSignal = 1

        elif self.tenkanGreaterKijun < 0:
            if (self.cloud > 0 and self.data < self.ichimoku.senkou_span_b) or (
                    self.cloud < 0 and self.data < self.ichimoku.senkou_span_a):
                if self.tenkanXKijun == -1 or self.XSenkouB == -1:
                    self.rets.ichimokuSignal = -1

        else:
            self.rets.ichimokuSignal = 0

    def getScreenerResultsDf(self):
        super(IchimokuScreener, self).getScreenerResultsDf()
        ichimoku = round(self.get_analysis().ichimoku, 3)
        ichimokuSignal = self.get_analysis().ichimokuSignal
        self.index += ["Ichimoku", "IchimokuSignal"]
        self.result += [ichimoku, ichimokuSignal]

        self.updateResultDF()
        return self.resultDF

class WilliamsROverboughtScreener(_ScreenerBase):
    params = dict(willRperiod=14, willRUpperband=-20, willRLowerband=-80)

    def start(self):
        super(WilliamsROverboughtScreener, self).start()
        self.williamsR = bt.indicators.WilliamsR(self.data,
                                                 period=self.p.willRperiod,
                                                 upperband=self.p.willRUpperband,
                                                 lowerband=self.p.willRLowerband,
                                                 )
        self.willRCrossoverLow = bt.indicators.CrossOver(self.williamsR, self.p.willRLowerband)
        self.willRCrossoverUp = bt.indicators.CrossOver(self.williamsR, self.p.willRUpperband)

    def stop(self):
        super(WilliamsROverboughtScreener, self).stop()
        self.rets.williamsROverbought = self.williamsR[0]
        self.rets.williamsROverboughtSignal = 0

        if self.willRCrossoverUp == 1:
            self.rets.williamsROverboughtSignal = 1

    def getScreenerResultsDf(self):
        super(WilliamsROverboughtScreener, self).getScreenerResultsDf()
        williamsROverbought = round(self.get_analysis().williamsROverbought, 3)
        williamsROverboughtSignal = self.get_analysis().williamsROverboughtSignal
        self.index += ["WilliamsROverbought", "WilliamsROverboughtSignal"]
        self.result += [williamsROverbought, williamsROverboughtSignal]

        self.updateResultDF()
        return self.resultDF

class WilliamsROversoldScreener(_ScreenerBase):
    params = dict(willRperiod=14, willRUpperband=-20, willRLowerband=-80)

    def start(self):
        super(WilliamsROversoldScreener, self).start()
        self.williamsR = bt.indicators.WilliamsR(self.data,
                                                 period=self.p.willRperiod,
                                                 upperband=self.p.willRUpperband,
                                                 lowerband=self.p.willRLowerband,
                                                 )
        self.willRCrossoverLow = bt.indicators.CrossOver(self.williamsR, self.p.willRLowerband)
        self.willRCrossoverUp = bt.indicators.CrossOver(self.williamsR, self.p.willRUpperband)

    def stop(self):
        super(WilliamsROversoldScreener, self).stop()
        self.rets.williamsROversold = self.williamsR[0]
        self.rets.williamsROversoldSignal = 0

        if self.willRCrossoverLow == -1:
            self.rets.williamsROversoldSignal = 1

    def getScreenerResultsDf(self):
        super(WilliamsROversoldScreener, self).getScreenerResultsDf()
        williamsROversold = round(self.get_analysis().williamsROversold, 3)
        williamsROversoldSignal = self.get_analysis().williamsROversoldSignal
        self.index += ["WilliamsROversold", "WilliamsROversoldSignal"]
        self.result += [williamsROversold, williamsROversoldSignal]

        self.updateResultDF()
        return self.resultDF
