import backtrader as bt
from BacktraderAPI import BTIndicator

#All backtrader indicators: https://www.backtrader.com/docu/indautoref/

class BBandsStrategyBase(bt.Strategy):

    #https://backtest-rookies.com/2018/02/23/backtrader-bollinger-mean-reversion-strategy/

    params = dict(movAvPeriod=20, bBandSD=2, bBandExit="median",)

    def __init__(self):
        super(BBandsStrategyBase, self).__init__()
        self.boll = bt.indicators.BollingerBands(period=self.p.movAvPeriod, devfactor=self.p.bBandSD)
        self.crossDownBollBottom = bt.indicators.CrossDown(self.data, self.boll.lines.bot, subplot = False)
        self.crossUpBollTop = bt.indicators.CrossUp(self.data, self.boll.lines.top, subplot = False)
        self.crossOverBollMid = bt.indicators.CrossOver(self.data, self.boll.lines.mid, subplot = False)

        self.crossDownBollBottom.csv = True
        self.crossUpBollTop.csv= True

class CCIStrategyBase(bt.Strategy):
    params = dict(cciPeriod=26, cciFactor=0.015, cciThreshold=100)

    def __init__(self):
        super(CCIStrategyBase, self).__init__()
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        self.upperband = self.p.cciThreshold
        self.lowerband = -self.p.cciThreshold
        self.cci = BTIndicator.talibCCI(period=self.p.cciPeriod, factor=self.p.cciFactor, upperband=self.upperband, lowerband=self.lowerband)
        self.cci.csv = True

        self.cciCrossUpperband = bt.ind.CrossUp(self.cci, self.upperband, plot=True)
        self.cciCrossUpperband.csv = True
        self.cciCrossLowerband = bt.ind.CrossDown(self.cci, self.lowerband, plot=True)
        self.cciCrossLowerband.csv = True

class ChandelierStrategyExit(bt.Strategy):
    params = dict(chandelierPeriod=22, multiplier=3)

    def __init__(self):
        super(ChandelierStrategyExit, self).__init__()
        self.chandelier = BTIndicator.ChandelierExit(period=self.p.chandelierPeriod, multip=self.p.multiplier)
        self.crossOverChandelierLong = bt.ind.CrossOver(self.data, self.chandelier.long, plot=False)
        self.crossOverChandelierLong.csv = True
        self.crossOverChandelierShort = bt.ind.CrossOver(self.data, self.chandelier.short, plot=False)
        self.crossOverChandelierShort.csv = True

class DMIStrategyBase(bt.Strategy):

    params = dict(dmiperiod=14, adxBenchmark=30)

    def __init__(self):
        super(DMIStrategyBase, self).__init__()
        self.dmi = bt.indicators.DirectionalMovementIndex(self.data, period=self.p.dmiperiod)
        self.dicross = bt.indicators.CrossOver(self.dmi.plusDI, self.dmi.minusDI, subplot=True)
        self.dmi.csv = True
        self.dicross.csv=True

class StochasticStrategyBase(bt.Strategy):
    '''
      - http://en.wikipedia.org/wiki/Stochastic_oscillator
    '''

    params = dict(period_Stoch=5, period_dfast=3, period_dslow=3)

    def __init__(self):
        super(StochasticStrategyBase, self).__init__()
        self.stoch = bt.ind.StochasticFull(period=self.p.period_Stoch, period_dfast=self.p.period_dfast,
                                           period_dslow=self.p.period_dslow, safediv=True)
        self.kCrossOverD = bt.ind.CrossOver(self.stoch.percK, self.stoch.percD, subplot=False)

class DonchianStrategyBase(bt.Strategy):
    params = dict(donchianPeriod=20, lookback=-1,)

    def __init__(self):
        super(DonchianStrategyBase, self).__init__()
        self.donchian = BTIndicator.DonchianChannels(period= self.p.donchianPeriod, lookback=self.p.lookback)

class SMAStrategyBase(bt.Strategy):
    params = dict(SMAFastPeriod=10, SMASlowPeriod=20)

    def __init__(self):
        super(SMAStrategyBase, self).__init__()
        self.sma1, self.sma2 = bt.ind.SMA(period=self.p.SMAFastPeriod), bt.ind.SMA(period=self.p.SMASlowPeriod)
        self.smaFastCrossoverSlow = bt.ind.CrossOver(self.sma1, self.sma2)
        self.sma2.csv = True

class RSIStrategyBase(bt.Strategy):
    params = dict(rsiPeriod=21, rsiUpperband=70, rsiLowerband=30)

    def __init__(self):
        super(RSIStrategyBase, self).__init__()
        self.rsi = bt.ind.RSI_SMA(self.data, period=self.p.rsiPeriod, safediv = True)

class MACDStrategyBase(bt.Strategy):
    params = dict(macdFast=12, macdSlow=26, diffPeriod=9)

    def __init__(self):
        super(MACDStrategyBase, self).__init__()
        self.macd = bt.indicators.MACD(period_me1=self.p.macdFast,
                                       period_me2=self.p.macdSlow,
                                       period_signal=self.p.diffPeriod, subplot=False)
        self.macd.csv = True
        self.macdHistogram = BTIndicator.MACDHistogram(period_me1=self.p.macdFast, period_me2=self.p.macdSlow, period_signal=self.p.diffPeriod)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal, subplot= False)
        self.mcross.csv = True


class WillamsRStrategyBase(bt.Strategy):
    params = dict(willRperiod=14, willRUpperband=-20, willRLowerband=-80)

    def __init__(self):
        super(WillamsRStrategyBase, self).__init__()
        self.williamsR = bt.indicators.WilliamsR(self.data,
                                                 period=self.p.willRperiod,
                                                 upperband=self.p.willRUpperband,
                                                 lowerband=self.p.willRLowerband,
                                                 )
        self.willRCrossoverLow = bt.indicators.CrossOver(self.williamsR, self.p.willRLowerband, subplot=False)
        self.willRCrossoverUp = bt.indicators.CrossOver(self.williamsR, self.p.willRUpperband, subplot=False)