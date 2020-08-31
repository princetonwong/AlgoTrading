import backtrader as bt
from BacktraderAPI import BTIndicator

#All backtrader indicators: https://www.backtrader.com/docu/indautoref/

#Channel
class AroonStrategyBase(bt.Strategy):

    params = dict(aroonPeriod=25,
                  aroonUpBand=100,
                  aroonLowBand=0
                  )

    def __init__(self):
        super(AroonStrategyBase, self).__init__()
        self.aroon = bt.indicators.AroonUpDownOscillator(self.data, period=self.p.aroonPeriod)
        self.aroonMidBand = int((self.p.aroonUpBand + self.p.aroonLowBand)/2)
        self.aroonCross = bt.indicators.CrossOver(self.aroon.aroonup, self.aroon.aroondown, subplot=True)

class BBandsStrategyBase(bt.Strategy):

    #https://backtest-rookies.com/2018/02/23/backtrader-bollinger-mean-reversion-strategy/

    params = dict(movAvPeriod=20, bBandSD=2, bBandExit="median",)

    def __init__(self):
        super(BBandsStrategyBase, self).__init__()
        self.boll = bt.indicators.BollingerBands(period=self.p.movAvPeriod, devfactor=self.p.bBandSD)
        self.crossUpBollTop = bt.indicators.CrossUp(self.data, self.boll.lines.top, plot = False)
        self.crossDownBollBottom = bt.indicators.CrossDown(self.data, self.boll.lines.bot, plot=False)
        self.crossOverBollMid = bt.indicators.CrossOver(self.data, self.boll.lines.mid, plot = False)
        self.crossDownBollBottom.csv = True
        self.crossUpBollTop.csv = True

class KeltnerChannelStrategyBase(bt.Strategy):
    params = dict(movAvPeriod=20, kChanSD=1.5)

    def __init__(self):
        super(KeltnerChannelStrategyBase, self).__init__()
        self.kChan = BTIndicator.KeltnerChannel(period=self.p.movAvPeriod, devfactor=self.p.kChanSD)
        self.cxKChanTop = bt.indicators.CrossOver(self.data, self.kChan.top, plot= False)
        self.cxKChanBot = bt.indicators.CrossOver(self.data, self.kChan.bot, plot=False)
        self.cxKChanMid = bt.indicators.CrossOver(self.data, self.kChan.mid, plot=False)

class BBandsKChanSqueezeStrategyBase(BBandsStrategyBase, KeltnerChannelStrategyBase):
    def __init__(self):
        super(BBandsKChanSqueezeStrategyBase, self).__init__()
        self.squeeze = BTIndicator.KeltnerChannelBBSqueeze()
        self.bBandCxKChan = bt.ind.CrossOver(self.squeeze.squeeze, 0, plot=False)


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

        self.cciCrossUpperband = bt.ind.CrossUp(self.cci, self.upperband, plot=False)
        self.cciCrossUpperband.csv = True
        self.cciCrossLowerband = bt.ind.CrossDown(self.cci, self.lowerband, plot=False)
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

class EMAStrategyBase(bt.Strategy):

    params = dict(emaPeriod=30)

    def __init__(self):
        super(EMAStrategyBase,self).__init__()
        self.ema = bt.indicators.ExponentialMovingAverage(self.data,period=self.p.emaPeriod)

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
        self.smaFastCrossoverSlow = bt.ind.CrossOver(self.sma1, self.sma2, plot=False)
        self.sma2.csv = True

#RSI
class RSIStrategyBase(bt.Strategy):
    params = dict(rsiPeriod=21, rsiUpperband=70, rsiLowerband=30)

    def __init__(self):
        super(RSIStrategyBase, self).__init__()
        self.rsi = bt.ind.RSI_SMA(self.data, period=self.p.rsiPeriod, safediv = True)

class DTOStrategyBase(bt.Strategy):
    params = dict(rsiPeriod=10, pPeriod=8, upperband=70, lowerband=30)

    def __init__(self):
        super(DTOStrategyBase, self).__init__()
        self.dto = BTIndicator.DynamicTradeOscillator(rsiPeriod=self.p.rsiPeriod, pPeriod=self.p.pPeriod, upperband=self.p.upperband, lowerband=self.p.lowerband)
        self.dtoCxUpper = bt.ind.CrossOver(self.dto, self.p.upperband, plot=False)
        self.dtoCxLower = bt.ind.CrossOver(self.dto, self.p.lowerband, plot=False)

class StochRSIStrategyBase(bt.Strategy):
    params = dict(rsiPeriod=10, pPeriod=8, kPeriod=5, dPeriod=3, upperband=70, lowerband=30)

    def __init__(self):
        super(StochRSIStrategyBase, self).__init__()
        self.stochRSI = BTIndicator.StochRSI(rsiPeriod=self.p.rsiPeriod, pPeriod=self.p.pPeriod,
                                             kPeriod=self.p.kPeriod, dPeriod=self.p.dPeriod,
                                             upperband=self.p.upperband, lowerband=self.p.lowerband)
        self.stochRSIKXD = bt.ind.CrossOver(self.stochRSI.k, self.stochRSI.d, plot=False)

#MACD
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

class ZeroLagMACDStrategyBase(bt.Strategy):
    params = dict(macdFastPeriod=12, macdSlowPeriod=26, macdSignalPeriod=9)

    def __init__(self):
        super(ZeroLagMACDStrategyBase, self).__init__()
        self.zeroLag = BTIndicator.ZeroLagMACD(fastPeriod=self.p.macdFastPeriod,
                                               slowPeriod=self.p.macdSlowPeriod,
                                               signalPeriod=self.p.macdSignalPeriod)
        self.zeroLag.csv = True
        self.macdHistoXZero = bt.ind.CrossOver(self.zeroLag.histo, 0.0, plot=False)
        self.macdHistoXZero.csv = True

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

#Candle
class PiercingCandleStrategyBase(bt.Strategy):
    params = dict(smaPeriod=5, lookback=6)

    def __init__(self):
     super(PiercingCandleStrategyBase, self).__init__()
     self.trend = BTIndicator.StreakBySMA(smaPeriod=self.p.smaPeriod, lookback=self.p.lookback).trend
     self.piercingCandle = BTIndicator.TwoBarPiercingCandle().pattern

class AbsoluteStrengthOscillatorStrategyBase(bt.Strategy):
    params = dict(period=21, smoothing=34, rsiFactor=30)

    def __init__(self):
        self.aso = BTIndicator.AbsoluteStrengthOscilator(period=self.p.period,
                                                         smoothing=self.p.smoothing,
                                                         rsifactor=self.p.rsiFactor)
        self.asoBullsCrossoverBears = bt.ind.CrossOver(self.aso.bulls, self.aso.bears, plot=False)

class ASIStrategyBase(bt.Strategy):
    def __init__(self):
        super(ASIStrategyBase, self).__init__()
        self.asi = BTIndicator.AccumulationSwingIndex()
        self.asiXZero = bt.ind.CrossOver(self.asi.asi, 0.0, plot=False)

class StreakStrategyBase(bt.Strategy):
    params = dict(lookback=6)

    def __init__(self):
        super(StreakStrategyBase, self).__init__()
        self.streak = BTIndicator.Streak(plot=False)
        self.streak.csv = True
        self.smaStreak = BTIndicator.StreakBySMA(smaPeriod=5, lookback=self.p.lookback, plot=False)
        self.smaStreak.csv = True