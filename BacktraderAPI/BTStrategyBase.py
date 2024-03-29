import backtrader as bt
from BacktraderAPI import BTIndicator

#Channel (Volatility)
class BBandsStrategyBase(bt.Strategy):
    params = dict(movAvPeriod=20, bBandSD=2, bBandExit="median",)

    def __init__(self):
        super(BBandsStrategyBase, self).__init__()
        self.boll = bt.indicators.BollingerBands(period=self.p.movAvPeriod, devfactor=self.p.bBandSD)
        self.bollWidth = (self.boll.top - self.boll.bot) / self.boll.mid
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
    params = dict(squeezeThreshold= 0)

    def __init__(self):
        super(BBandsKChanSqueezeStrategyBase, self).__init__()
        self.squeeze = BTIndicator.KeltnerChannelBBSqueeze()
        self.squeeze.csv = True
        self.bBandCxKChan = bt.indicators.CrossOver(self.squeeze.squeeze, 0, plot=False)

class DonchianStrategyBase(bt.Strategy):
    params = dict(donchianPeriod=20, lookback=-1,)

    def __init__(self):
        super(DonchianStrategyBase, self).__init__()
        self.donchian = BTIndicator.DonchianChannels(period= self.p.donchianPeriod, lookback=self.p.lookback)

class VLIStrategyBase(bt.Strategy):
    def __init__(self):
        super(VLIStrategyBase, self).__init__()
        self.vli = BTIndicator.VolatilityLevelIndicator()
        self.volatilityLevel = self.vli.fast > self.vli.slow
        self.extremeVolatiliy = self.vli.bollWidth > self.vli.top


#Oscillator (Strength of Trend)
class AroonStrategyBase(bt.Strategy):
    '''  Amount of time between highs and lows
    Aroon Up: Strength of uptrend
    Aroon Down: Strength of downtrend
    '''

    params = dict(aroonPeriod=25,aroonUpBand=100,aroonLowBand=0)

    def __init__(self):
        super(AroonStrategyBase, self).__init__()
        self.aroon = bt.indicators.AroonUpDownOscillator(self.data, period=self.p.aroonPeriod)
        self.aroonMidBand = int((self.p.aroonUpBand + self.p.aroonLowBand)/2)
        self.aroonCross = bt.indicators.CrossOver(self.aroon.aroonup, self.aroon.aroondown, subplot=True)

class DMIStrategyBase(bt.Strategy):
    ''' This Strategy Base shows ADX, ADXR, +DI, -DI.
    DI : Price difference between current highs/lows and prior highs/lows
    ADX: Average Difference in +DI and -DI. (common signal: >25)
    ADXR: A Lagging ADX to confirm ADX trend.
    '''
    params = dict(dmiperiod=14, adxBenchmark=25, adxrBenchmark=20)

    def __init__(self):
        super(DMIStrategyBase, self).__init__()
        self.dmi = bt.indicators.DirectionalMovement(period=self.p.dmiperiod)
        self.plusDIXminusDI = bt.indicators.CrossOver(self.dmi.plusDI, self.dmi.minusDI, subplot=True)
        self.adxXBenchmark = bt.indicators.CrossOver(self.dmi.adx, self.p.adxBenchmark, subplot=True)
        self.adxrXBenchmark = bt.indicators.CrossOver(self.dmi.adxr, self.p.adxBenchmark, subplot=True)
        self.dmi.csv = True
        self.plusDIXminusDI.csv = True

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

        self.cciXUpperband = bt.ind.CrossOver(self.cci, self.upperband, plot=False)
        self.cciXUpperband.csv = True
        self.cciXLowerband = bt.ind.CrossOver(self.cci, self.lowerband, plot=False)
        self.cciXLowerband.csv = True

class StochasticCCIStrategyBase(CCIStrategyBase):
    params = dict(kPeriod=5, dPeriod=3)

    def __init__(self):
        super(StochasticCCIStrategyBase, self).__init__()
        self.stochCCI = BTIndicator.StochasticCCI(kPeriod=self.p.kPeriod, dPeriod=self.p.dPeriod)
        # self.kCxd = bt.indicators.CrossOver(self.stochCCI.k, self.stochCCI.d, plot=False)
        self.stochcciXUpperband = bt.ind.CrossOver(self.stochCCI.k, self.upperband, plot=False)
        self.stochcciXUpperband.csv = True
        self.stochcciXLowerband = bt.ind.CrossOver(self.stochCCI.k, self.lowerband, plot=False)
        self.stochcciXLowerband.csv = True

class CCIHeikinAshiStrategyBase(bt.Strategy):
    params = dict(cciPeriod=26, cciFactor=0.015, cciThreshold=100)

    def __init__(self):
        super(CCIHeikinAshiStrategyBase, self).__init__()
        self.dataclose = bt.ind.HeikinAshi(self.data1)

        self.upperband = self.p.cciThreshold
        self.lowerband = -self.p.cciThreshold
        self.hkacci = BTIndicator.talibCCI(self.dataclose, period=self.p.cciPeriod, factor=self.p.cciFactor, upperband=self.upperband, lowerband=self.lowerband)
        self.hkacci.csv = True

        self.hkacciXUpperband = bt.ind.CrossOver(self.hkacci, self.upperband, plot=False)
        self.hkacciXUpperband.csv = True
        self.hkacciXLowerband = bt.ind.CrossOver(self.hkacci, self.lowerband, plot=False)
        self.hkacciXLowerband.csv = True

class TTFStrategyBase(bt.Strategy):
    params = dict(lookback=15, upperband=100, lowerband=-100)

    def __init__(self):
        super(TTFStrategyBase, self).__init__()
        self.ttf = BTIndicator.TrendTriggerFactor(lookback=self.p.lookback, upperband=self.p.upperband, lowerband=self.p.lowerband)
        self.ttf.csv = True
        self.ttfCxLower = bt.indicators.CrossOver(self.ttf.ttf, self.ttf.lowerband, plot=False)
        self.ttfCxUpper = bt.indicators.CrossOver(self.ttf.ttf, self.ttf.upperband, plot=False)

class StochasticTTFStrategyBase(TTFStrategyBase):
    params = dict(kPeriod=9, dPeriod=5)

    def __init__(self):
        super(StochasticTTFStrategyBase, self).__init__()
        self.stochTTF = BTIndicator.StochasticTTF(kPeriod=self.p.kPeriod, dPeriod=self.p.dPeriod)
        self.kCxd = bt.indicators.CrossOver(self.stochTTF.k, self.stochTTF.d, plot=False)

class AwesomeOscillatorStrategyBase(bt.Strategy):
    params = dict(aoFast=5, aoSlow=34, lookback= 2)

    def __init__(self):
        super(AwesomeOscillatorStrategyBase, self).__init__()
        self.ao = bt.ind.AwesomeOscillator(fast= self.p.aoFast, slow= self.p.aoSlow)
        self.aoXZero = bt.ind.CrossOver(self.ao, 0, plot= False)
        self.aoStreak = BTIndicator.StreakByAwesomeOscillator(aoFast= self.p.aoFast, aoSlow= self.p.aoSlow, lookback= self.p.lookback)
        self.aoStreakXZero = bt.ind.CrossOver(self.aoStreak.streak, 0, plot=False)


class KDJStrategyBase(bt.Strategy):
    def __init__(self):
        super(KDJStrategyBase, self).__init__()
        self.kdj = BTIndicator.KDJIndicator(kPeriod=9, dPeriod=3, jPeriod=3)
        self.streakKDJ = BTIndicator.StreakByKDJ()


#Resistance, Support
class SMAStrategyBase(bt.Strategy):
    params = dict(SMAFastPeriod=10, SMASlowPeriod=20)

    def __init__(self):
        super(SMAStrategyBase, self).__init__()
        self.smaFast, self.smaSlow = bt.ind.SMA(period=self.p.SMAFastPeriod), bt.ind.SMA(period=self.p.SMASlowPeriod)
        self.smaFastCrossoverSlow = bt.ind.CrossOver(self.smaFast, self.smaSlow, plot=False)
        self.smaFast.csv = True
        self.smaSlow.csv = True

class EMAStrategyBase(bt.Strategy):
    params = dict(EMAFastPeriod=10, EMASlowPeriod=20)

    def __init__(self):
        super(EMAStrategyBase,self).__init__()
        self.emaFast, self.emaSlow = bt.ind.EMA(period=self.p.EMAFastPeriod), bt.ind.EMA(period=self.p.EMASlowPeriod)
        self.emaFastXemaSlow = bt.ind.CrossOver(self.emaFast, self.emaSlow, plot=False)
        self.emaFast.csv = True
        self.emaSlow.csv = True

class KAMAStrategyBase(bt.Strategy):
    params = dict(smaPeriod=30, kamaPeriod=30, kamaFast=2, kamaSlow=30)

    def __init__(self):
        super(KAMAStrategyBase, self).__init__()
        self.kama = BTIndicator.AdaptiveMovingAverage(period=self.p.kamaPeriod, fast=self.p.kamaFast, slow= self.p.kamaSlow)
        self.sma = bt.ind.MovingAverageSimple(self.kama, period= self.p.smaPeriod)
        self.sma.plotinfo.plotmaster = self.data
        self.kama.csv = True
        self.kamaXsma = bt.ind.CrossOver(self.kama, self.sma)

class IchimokuCloudStrategyBase(bt.Strategy):
    '''
       https://medium.com/@harrynicholls/7-popular-technical-indicators-and-how-to-use-them-to-increase-your-trading-profits-7f13ffeb8d05
       https://tradingtools.net/simplified-ichimoku-strategy/
       https://school.stockcharts.com/doku.php?id=technical_indicators:ichimoku_cloud
    '''

    params = dict(kijun=26, tenkan=9, chikou=26, senkou=52, senkou_lead=26)

    def __init__(self):
        super(IchimokuCloudStrategyBase, self).__init__()
        self.ichimoku = bt.indicators.Ichimoku(kijun=self.p.kijun,
                                               tenkan=self.p.tenkan,
                                               chikou = self.p.chikou,
                                               senkou=self.p.senkou,
                                               senkou_lead=self.p.senkou_lead
                                               )
        self.tenkanXKijun = bt.indicators.CrossOver(self.ichimoku.tenkan_sen, self.ichimoku.kijun_sen, plot=False)
        self.XKijun = bt.indicators.CrossOver(self.data, self.ichimoku.kijun_sen, plot=False)
        self.XSenkouA = bt.indicators.CrossOver(self.data, self.ichimoku.senkou_span_a, plot=False)
        self.XSenkouB = bt.indicators.CrossOver(self.data, self.ichimoku.senkou_span_b, plot=False)
        # self.ichimokuCloud = self.ichimoku.senkou_span_a - self.ichimoku.senkou_span_b
        # self.tenkanGreaterKijun = self.ichimoku.tenkan_sen - self.ichimoku.kijun_sen
        # # self.ichimokuCloud = self.ichimoku.senkou_span_a > self.ichimoku.senkou_span_b
        # self.tenkanGreaterKijun = self.ichimoku.tenkan_sen > self.ichimoku.kijun_sen


#Trend Changing, RSI, Stochastic
class RSIStrategyBase(bt.Strategy):
    params = dict(rsiPeriod=21, rsiUpperband=70, rsiLowerband=30)

    def __init__(self):
        super(RSIStrategyBase, self).__init__()
        self.rsi = bt.ind.RSI_Safe(self.data, period=self.p.rsiPeriod, safediv = True)

class StochasticStrategyBase(bt.Strategy):
    params = dict(period_Stoch=5, period_dfast=3, period_dslow=3)

    def __init__(self):
        super(StochasticStrategyBase, self).__init__()
        self.stoch = bt.ind.StochasticFull(period=self.p.period_Stoch, period_dfast=self.p.period_dfast,
                                           period_dslow=self.p.period_dslow, safediv=True)
        self.kCrossOverD = bt.ind.CrossOver(self.stoch.percK, self.stoch.percD, subplot=False)

class WillamsRStrategyBase(bt.Strategy):
    params = dict(willRperiod=14, willRUpperband=-20, willRLowerband=-80)

    def __init__(self):
        super(WillamsRStrategyBase, self).__init__()
        self.williamsR = bt.indicators.WilliamsR(self.data,
                                                 period=self.p.willRperiod,
                                                 upperband=self.p.willRUpperband,
                                                 lowerband=self.p.willRLowerband,
                                                 )
        self.willRCrossoverLow = bt.indicators.CrossOver(self.williamsR, self.p.willRLowerband, subplot=True)
        self.willRCrossoverUp = bt.indicators.CrossOver(self.williamsR, self.p.willRUpperband, subplot=True)

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

class ASOStrategyBase(bt.Strategy):
    params = dict(period=21, smoothing=34, rsiFactor=30, asoThreshold= 0)

    def __init__(self):
        super(ASOStrategyBase, self).__init__()
        self.aso = BTIndicator.AbsoluteStrengthOscilator(period=self.p.period,
                                                         smoothing=self.p.smoothing,
                                                         rsifactor=self.p.rsiFactor)
        self.aso.csv = True
        self.ashXZero = bt.ind.CrossOver(self.aso.ash, 0, plot=False)
        self.ashXUpper = bt.ind.CrossOver(self.aso.ash, self.p.asoThreshold, plot=False)
        self.ashXLower = bt.ind.CrossOver(self.aso.ash, -self.p.asoThreshold, plot=False)

class CMOStrategyBase(bt.Strategy):
    params = dict(period=21, cmoThreshold= 30)

    def __init__(self):
        super(CMOStrategyBase, self).__init__()
        self.cmo = bt.ind.MovingAverageSimple(bt.talib.CMO(timeperiod=self.p.period), period=3)
        self.cmo.plotinfo.plotyhlines = [0.0, self.p.cmoThreshold, -self.p.cmoThreshold]
        self.cmo.csv = True
        self.cmoXZero = bt.ind.CrossOver(self.cmo, 0, plot=False)
        self.cmoXUpper = bt.ind.CrossOver(self.cmo, self.p.cmoThreshold, plot=False)
        self.cmoXLower = bt.ind.CrossOver(self.cmo, -self.p.cmoThreshold, plot=False)


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


#Candle
class PiercingCandleStrategyBase(bt.Strategy):
    params = dict(smaPeriod=5, lookback=6)

    def __init__(self):
     super(PiercingCandleStrategyBase, self).__init__()
     self.trend = BTIndicator.StreakBySMA(smaPeriod=self.p.smaPeriod, lookback=self.p.lookback).trend
     self.piercingCandle = BTIndicator.TwoBarPiercingCandle().pattern


#Trend Direction
class ASIStrategyBase(bt.Strategy):
    def __init__(self):
        super(ASIStrategyBase, self).__init__()
        self.si = BTIndicator.SwingIndex()
        self.asi = BTIndicator.AccumulationSwingIndex()
        self.siXZero = bt.ind.CrossOver(self.si.si, 0.0, plot=False)
        self.asiXZero = bt.ind.CrossOver(self.asi.asi, 0.0, plot=False)

class StreakStrategyBase(bt.Strategy):
    params = dict(lookback=6)

    def __init__(self):
        super(StreakStrategyBase, self).__init__()
        self.streak = BTIndicator.Streak(plot=False)
        self.streak.csv = True
        self.smaStreak = BTIndicator.StreakBySMA(smaPeriod=5, lookback=self.p.lookback, plot=False)
        self.smaStreak.csv = True

class PSARStrategyBase(bt.Strategy):

    def __init__(self):
        self.psar = bt.ind.ParabolicSAR()

