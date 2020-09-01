from backtrader.indicators import *

#RSI
class DynamicTradeOscillator(bt.Indicator):
    lines = ('dto', )
    params = dict(rsiPeriod=10, pPeriod=8, upperband=70, lowerband=30)

    def _plotinit(self):
        self.plotinfo.plotyhlines = [self.p.upperband, self.p.lowerband]

    def __init__(self):
        rsi = bt.ind.RSI_Safe(period=self.p.rsiPeriod)
        maxrsi = bt.ind.Highest(rsi, period=self.p.pPeriod)
        minrsi = bt.ind.Lowest(rsi, period=self.p.pPeriod)
        self.l.dto = DivByZero(rsi - minrsi , maxrsi - minrsi) * 100

class StochRSI(DynamicTradeOscillator):
    lines = ('k', "d",)
    params = dict(kPeriod=5, dPeriod=3)

    def __init__(self):
        super(StochRSI, self).__init__()
        self.l.k = bt.ind.MovingAverageSimple(self.l.dto, period= self.p.kPeriod)
        self.l.d = bt.ind.MovingAverageSimple(self.k, period= self.p.dPeriod)

class ConnorsRSI(bt.Indicator):
    '''
    Calculates the ConnorsRSI as:
        - (RSI(per_rsi) + RSI(Streak, per_streak) + PctRank(per_rank)) / 3
    '''
    lines = ('crsi',)
    params = dict(prsi=3, pstreak=2, prank=100, upperband=90, lowerband=10)

    def _plotinit(self):
        self.plotinfo.plotyhlines = [self.p.upperband, self.p.lowerband]

    def __init__(self):
        # Calculate the components
        rsi = bt.ind.RSI(self.data, period=self.p.prsi, safediv=True)

        streak = Streak(self.data)
        rsi_streak = bt.ind.RSI(streak, period=self.p.pstreak)

        prank = bt.ind.PercentRank(self.data, period=self.p.prank)

        # Apply the formula
        self.l.crsi = (rsi + rsi_streak + prank) / 3.0

class DonchianChannels(bt.Indicator):
    '''
    Params Note:
      - `lookback` (default: -1)
        If `-1`, the bars to consider will start 1 bar in the past and the
        current high/low may break through the channel.
        If `0`, the current prices will be considered for the Donchian
        Channel. This means that the price will **NEVER** break through the
        upper/lower channel bands.
    '''

    alias = ('DCH', 'DonchianChannel',)

    lines = ('dcm', 'dch', 'dcl',)  # dc middle, dc high, dc low
    params = dict(
        period=20,
        lookback=-1,  # consider current bar or not
    )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        dcm=dict(ls='--'),  # dashed line
        dch=dict(_samecolor=True),  # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),  # use same color as prev line (dch)
    )

    def __init__(self):
        hi, lo = self.data.high, self.data.low
        if self.p.lookback:  # move backwards as needed
            hi, lo = hi(self.p.lookback), lo(self.p.lookback)

        self.l.dch = bt.ind.Highest(hi, period=self.p.period)
        self.l.dcl = bt.ind.Lowest(lo, period=self.p.period)
        self.l.dcm = (self.l.dch + self.l.dcl) / 2.0  # avg of the above

class talibCCI(bt.Indicator):
    '''
      Introduced by Donald Lambert in 1980 to measure variations of the
      "typical price" (see below) from its mean to identify extremes and
      reversals

      Formula:
        - tp = typical_price = (high + low + close) / 3
        - tpmean = MovingAverage(tp, period)
        - deviation = tp - tpmean
        - meandev = MeanDeviation(tp)
        - cci = deviation / (meandeviation * factor)

      See:
        - https://en.wikipedia.org/wiki/Commodity_channel_index
      '''
    alias = ('CCI',)

    lines = ('cci', "upperband", "lowerband")

    params = (('period', 26),
              ('factor', 0.015),
              ('movav', bt.ind.MovAv.Simple),
              ('upperband', 100.0),
              ('lowerband', -100.0),)

    def _plotlabel(self):
        plabels = [self.p.period, self.p.factor]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def _plotinit(self):
        self.plotinfo.plotyhlines = [0.0, self.p.upperband, self.p.lowerband]
        # self.plotinfo.plothlines = [self.p.upperband, self.p.lowerband]

    def __init__(self):
        # self.addminperiod(self.p.period)
        # self.l.tp = (self.data.high + self.data.low + self.data.close) / 3.0
        # self.l.tpmean = self.p.movav(self.l.tp, period=self.p.period)
        self.l.cci = bt.talib.CCI(self.data.high, self.data.low, self.data.close, timeperiod = self.p.period)

    def next(self):
        self.l.upperband[0] = self.p.upperband
        self.l.lowerband[0] = self.p.lowerband
    #     # self.l.tp[0] = (self.data.high[0] + self.data.low[0] + self.data.close[0]) / 3.0
    #     # self.l.tpmean = bt.ind.MovAv(self.l.tp, period= self.p.period)
    #     print (self.l.tpmean[0])
    #     self.l.dev[0] = self.l.tp[0] - self.l.tpmean[0]
    #     print (self.l.tp.get(size=self.p.period))
    #     print (self.l.tpmean[0])
    #     print (self.l.tp.get(size=self.p.period) - self.l.tpmean[0])
    #     self.lines.meandev[0] = np.mean(abs(self.l.tp.get(size=self.p.period) - self.l.tpmean[0]))
    #     self.lines.cci = self.l.dev / (self.p.factor * self.l.meandev)
    #
    # def once(self, start, end):
    #     darray = self.data.array
    #     larray = self.line.array
    #     alpha = self.alpha
    #     alpha1 = self.alpha1
    #
    #     # Seed value from SMA calculated with the call to oncestart
    #     prev = larray[start - 1]
    #     for i in range(start, end):
    #         larray[i] = prev = prev * alpha1 + darray[i] * alpha

class AbsoluteStrengthOscilator(bt.Indicator):
    lines = ('ash', 'bulls', 'bears',)  # output lines

    # customize the plotting of the *ash* line
    plotlines = dict(ash=dict(_method='bar', alpha=0.33, width=0.66), bulls=dict(_plotskip=True,), bears=dict(_plotskip=True,),)

    RSI, STOCH = range(0, 2)  # enum values for the parameter mode

    params = dict(
        period=9,
        smoothing=2,
        mode=STOCH,
        rsifactor=0.5,
        movav=bt.ind.WMA,  # WeightedMovingAverage
        smoothav=None,  # use movav if not specified
        pointsize=None,  # use only if specified
    )

    def __init__(self):
        # Start calcs according to selected mode
        if self.p.mode == self.RSI:
            p0p1 = self.data - self.data(-1)  # used twice below
            half_abs_p0p1 = self.p.rsifactor * abs(p0p1)  # used twice below

            bulls = half_abs_p0p1 + p0p1
            bears = half_abs_p0p1 - p0p1
        else:
            bulls = self.data - bt.ind.Lowest(self.data, period=self.p.period)
            bears = bt.ind.Highest(self.data, period=self.p.period) - self.data

        avbulls = self.p.movav(bulls, period=self.p.period)
        avbears = self.p.movav(bears, period=self.p.period)

        # choose smoothing average and smooth the already averaged values
        smoothav = self.p.smoothav or self.p.movav  # choose smoothav
        smoothbulls = smoothav(avbulls, period=self.p.smoothing, plot=False)
        smoothbears = smoothav(avbears, period=self.p.smoothing, plot=False)

        if self.p.pointsize:  # apply only if it makes sense
            smoothbulls /= self.p.pointsize
            smoothbears /= self.p.pointsize

        # Assign the final values to the output lines
        self.l.bulls = smoothbulls
        self.l.bears = smoothbears
        self.l.ash = smoothbulls - smoothbears

class TrendTriggerFactor(bt.Indicator):
    lines = ('ttf', 'upperband', "lowerband")
    params = dict(lookback=15, upperband=100, lowerband=-100)

    def _plotinit(self):
        self.plotinfo.plotyhlines = [0.0, self.p.upperband, self.p.lowerband]

    def __init__(self):
        high = self.data.high
        low= self.data.low
        lookback = self.p.lookback
        bp = Highest(high, period= lookback) - Lowest(low(-15), period= lookback)
        sp = Highest(high(-15), period= lookback) - Lowest(low, period= lookback)
        self.l.ttf = DivByZero(bp-sp, 0.5 * (bp +sp)) * 100

    def next(self):
        self.l.upperband[0] = self.p.upperband
        self.l.lowerband[0] = self.p.lowerband

class StochasticTTF(TrendTriggerFactor):
    lines = ('k', "d",)
    params = dict(kPeriod=9, dPeriod=5)

    def __init__(self):
        super(StochasticTTF, self).__init__()
        self.l.k = bt.ind.MovingAverageSimple(self.l.ttf, period= self.p.kPeriod)
        self.l.d = bt.ind.MovingAverageSimple(self.k, period= self.p.dPeriod)

class ChandelierExit(bt.Indicator):

    ''' https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/chandelier-exit/ '''

    lines = ('chandLong', 'chandShort')
    params = (('period', 22), ('multiplier', 3),)

    plotinfo = dict(subplot=False)

    def __init__(self):
        self.highest = bt.ind.Highest(self.data.high, period=self.p.period)
        self.lowest = bt.ind.Lowest(self.data.low, period=self.p.period)
        self.atr = self.p.multip * bt.ind.ATR(self.data, period=self.p.period)
        self.l.chandLong = self.highest - self.atr
        self.l.chandShort = self.lowest + self.atr

class ChandelierExitHistogram(ChandelierExit):
    lines = ("histo",)
    plotinfo = dict(subplot=True)
    plotlines = dict(long=dict(_plotskip=True, ), short=dict(_plotskip=True, ), histo=dict(_method='bar', alpha=0.50, width=1.0))

    def __init__(self):
        super(ChandelierExitHistogram, self).__init__()
        self.lines.histo = self.lines.long - self.lines.short

class KeltnerChannel(bt.Indicator):

    lines = ('mid', 'top', 'bot',)
    params = (('period', 20), ('devfactor', 1.5),
              ('movav', bt.ind.MovAv.Simple),)

    plotinfo = dict(subplot=False)
    plotlines = dict(
        mid=dict(ls='--'),
        top=dict(_samecolor=True),
        bot=dict(_samecolor=True),
    )

    def _plotlabel(self):
        plabels = [self.p.period, self.p.devfactor]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def __init__(self):
        self.lines.mid = ma = self.p.movav(self.data, period=self.p.period)
        atr = self.p.devfactor * bt.ind.ATR(self.data, period=self.p.period)
        self.lines.top = ma + atr
        self.lines.bot = ma - atr

class KeltnerChannelBBSqueeze(bt.Indicator):

    '''
    https://www.netpicks.com/squeeze-out-the-chop/

    Both indicators are symmetrical, meaning that the upper and lower bands or channel lines are the same distance from the moving average. That means that we can focus on only one side in developing our indicator. In our case, we’ll just consider the upper lines.

    The basic formulas we need are:

        Bollinger Band = Moving Average + (Number of standard deviations X Standard Deviation)
        Keltner Channel = Moving Average + (Number of ATR’s X ATR)

    Or if we translate this into pseudo-code:

        BBUpper = Avg(close, period) + (BBDevs X StdDev(close, period))
        KCUpper = Avg(close, period) + (KCDevs X ATR(period))

    The squeeze is calculated by taking the difference between these two values:

        Squeeze = BBUpper – KCUpper

    Which simplifies down to this:

        Squeeze = (BBDevs X StdDev(close, period)) – (KCDevs X ATR(period))
    '''

    lines = ('squeeze',)
    params = (('period', 20), ('bbdevs', 2.0), ('kcdevs', 1.5), ('movav', bt.ind.MovAv.Simple),)
    plotlines = dict(squeeze=dict(_method='bar', alpha=0.50, width=1.0))

    plotinfo = dict(subplot=True)

    def _plotlabel(self):
        plabels = [self.p.period, self.p.bbdevs, self.p.kcdevs]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def __init__(self):
        bb = bt.ind.BollingerBands(
            period=self.p.period, devfactor=self.p.bbdevs, movav=self.p.movav)
        kc = KeltnerChannel(
            period=self.p.period, devfactor=self.p.kcdevs, movav=self.p.movav)
        bbavg = bt.ind.MovingAverageSimple(bb.top, period= 3)
        kcavg = bt.ind.MovingAverageSimple(kc.top, period= 3)
        self.lines.squeeze = bbavg - kcavg

class VolumeWeightedAveragePrice(bt.Indicator):
    plotinfo = dict(subplot=False)

    params = (('period', 30), )

    alias = ('VWAP', 'VolumeWeightedAveragePrice',)
    lines = ('VWAP',)
    plotlines = dict(VWAP=dict(alpha=0.50, linestyle='-.', linewidth=2.0))



    def __init__(self):
        # Before super to ensure mixins (right-hand side in subclassing)
        # can see the assignment operation and operate on the line
        cumvol = bt.ind.SumN(self.data.volume, period = self.p.period)
        typprice = ((self.data.close + self.data.high + self.data.low)/3) * self.data.volume
        cumtypprice = bt.ind.SumN(typprice, period=self.p.period)
        self.lines[0] = cumtypprice / cumvol

        super(VolumeWeightedAveragePrice, self).__init__()

class HeiKinAshiStochasticBase(bt.ind.HeikinAshi):
    lines = ('percK', 'percD',)
    params = (('period', 14), ('period_dfast', 3), ('movav', MovAv.Simple),
              ('upperband', 80.0), ('lowerband', 20.0),
              ('safediv', False), ('safezero', 0.0))

    plotlines = dict(percD=dict(_name='%D', ls='--'),
                     percK=dict(_name='%K'))

    def _plotlabel(self):
        plabels = [self.p.period, self.p.period_dfast]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def _plotinit(self):
        self.plotinfo.plotyhlines = [self.p.upperband, self.p.lowerband]

    def __init__(self):
        highesthigh = Highest(self.l.ha_high, period=self.p.period)
        lowestlow = Lowest(self.l.ha_low, period=self.p.period)
        knum = self.l.ha_close - lowestlow
        kden = highesthigh - lowestlow
        if self.p.safediv:
            self.k = 100.0 * DivByZero(knum, kden, zero=self.p.safezero)
        else:
            self.k = 100.0 * (knum / kden)
        self.d = self.p.movav(self.k, period=self.p.period_dfast)

        super(HeiKinAshiStochasticBase, self).__init__()

class HeiKinAshiStochasticFull(HeiKinAshiStochasticBase):
    '''
    This version displays the 3 possible lines:

      - percK
      - percD
      - percSlow

    Formula:
      - k = d
      - d = MovingAverage(k, period_dslow)
      - dslow =

    See:
      - http://en.wikipedia.org/wiki/Stochastic_oscillator
    '''
    lines = ('percDSlow',)
    params = (('period_dslow', 3),)

    plotlines = dict(percDSlow=dict(_name='%DSlow'))

    def _plotlabel(self):
        plabels = [self.p.period, self.p.period_dfast, self.p.period_dslow]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def __init__(self):
        super(HeiKinAshiStochasticFull, self).__init__()
        self.lines.percK = self.k
        self.lines.percD = self.d
        self.l.percDSlow = self.p.movav(
            self.l.percD, period=self.p.period_dslow)

class TwoBarPiercingCandle(bt.Indicator):
    '''
        The Piercing: in a downtrend, O1 >C1, O2 <C2, O2 ≤C1, C2<O1, and C2>C1+0.5(O1−C1).

        High winning rate in bullish market, and oscillating market, rare occurence

        See:
        - Profitable candlestick trading strategies—The evidence from a new perspective
        doi:10.1016/j.rfe.2012.02.001
      '''
    lines = ('pattern', )

    def __init__(self):
        self.l.pattern = bt.talib.CDLPIERCING(self.data.open, self.data.high, self.data.low, self.data.close)

class MoneyFlowIndicator(bt.Indicator):
    lines = ('mfi',)
    params = dict(period=14)

    alias = ('MoneyFlowIndicator',)

    def __init__(self):
        tprice = (self.data.close + self.data.low + self.data.high) / 3.0
        mfraw = tprice * self.data.volume

        flowpos = bt.ind.SumN(mfraw * (tprice > tprice(-1)), period=self.p.period)
        flowneg = bt.ind.SumN(mfraw * (tprice < tprice(-1)), period=self.p.period)

        mfiratio = bt.ind.DivByZero(flowpos, flowneg, zero=100.0)
        self.l.mfi = 100.0 - 100.0 / (1.0 + mfiratio)

#MACD
class ZeroLagMACD(bt.Indicator):
    lines = ('macd', "signal", "histo",)
    params = dict(fastPeriod=12, slowPeriod=26, signalPeriod=9)
    plotlines = dict(histo=dict(_method='bar', alpha=0.50, width=1.0))

    def __init__(self):
        self.emaFast = bt.ind.ExponentialMovingAverage(self.data, period= self.p.fastPeriod)
        self.emaSlow = bt.ind.ExponentialMovingAverage(self.data, period= self.p.slowPeriod)
        self.emaemaFast = bt.ind.ExponentialMovingAverage(self.emaFast.ema, period=self.p.fastPeriod)
        self.emaemaSlow = bt.ind.ExponentialMovingAverage(self.emaSlow.ema, period=self.p.slowPeriod)
        self.l.macd = (self.emaFast.ema * 2 - self.emaemaFast.ema) - (self.emaSlow.ema * 2 - self.emaemaSlow.ema)

        self.l.signal = bt.ind.ExponentialMovingAverage(self.l.macd, period=self.p.signalPeriod)
        # self.l.signal = (bt.ind.ExponentialMovingAverage(self.l.macd).ema * 2 - bt.ind.ExponentialMovingAverage(self.emaLineMACD.ema, period=self.p.signalPeriod).ema)

        self.l.histo = (self.l.macd - self.l.signal)

class SwingIndex(bt.Indicator):
    lines = ('si',)
    def nextstart(self):
        self.line[0] = 0

    def next(self):
        high = self.data.high
        low = self.data.low
        dataopen = self.data.open
        close = self.data.close
        if abs(high[0] - close[-1]) >= abs(low[0] - close[-1]):
            if abs(high[0] - close[-1]) >= (high[0] - low[0]):
                self.r = abs(high[0] - close[-1]) - .5 * (abs(low[0] - close[-1])) + .25 * (abs(close[-1] - dataopen[-1]))
            else:
                self.r = (high[0] - low[0]) + .25 * (abs(close[-1] - dataopen[-1]))
        else:
            if abs(low[0] - close[-1]) >= (high[0] - low[0]):
                self.r = abs(low[0] - close[-1]) - .5 * (abs(high[0] - close[-1])) + .25 * (abs(close[-1] - dataopen[-1]))
            else:
                self.r = (high[0] - low[0]) + .25 * (abs(close[-1] - dataopen[-1]))

        self.k = max(abs(high[0] - close[-1]), abs(low[0] - close[-1]))

        self.nominator = (close[0] - close[-1]) + .5 * (close[0] - dataopen[0]) + .25 * (close[-1] - dataopen[-1])

        if self.r == 0:
            self.l.si[0] = 0
        else:
            self.l.si[0] = 50 * self.nominator/ self.r * self.k / 3

class AccumulationSwingIndex(bt.Indicator):
    lines = ('asi',)
    def __init__(self):
        self.l.asi = bt.ind.Accum(SwingIndex().si)

#Streak
class Streak(bt.ind.PeriodN):
    '''
    Keeps a counter of the current upwards/downwards/neutral streak
    '''
    lines = ('streak',)
    params = dict(period=2)  # need prev/cur days (2) for comparisons
    plotlines = dict(streak=dict(_method='bar', alpha=0.50, width=1.0))

    curstreak = 0

    def next(self):
        d0, d1 = self.data[0], self.data[-1]

        if d0 > d1:
            self.l.streak[0] = self.curstreak = max(1, self.curstreak + 1)
        elif d0 < d1:
            self.l.streak[0] = self.curstreak = min(-1, self.curstreak - 1)
        else:
            self.l.streak[0] = self.curstreak = 0

class StreakBySMA(bt.Indicator):
    lines = ('trend',"streak",)
    params = dict(smaPeriod=5, lookback=6)
    plotlines = dict(trend=dict(_method='bar', alpha=0.50, width=1.0))

    curstreak = 0

    def _plotinit(self):
        self.plotinfo.plotyhlines = [self.p.lookback, -self.p.lookback]

    def __init__(self):
        self.sma = bt.ind.MovingAverageSimple(period= self.p.smaPeriod, plot=False)
        self.addminperiod(self.p.smaPeriod + self.p.lookback)

    def next(self):
        d0, d1 = self.sma[0], self.sma[-1]

        if d0 > d1:
            self.l.streak[0] = self.curstreak = max(1, self.curstreak + 1)
        elif d0 < d1:
            self.l.streak[0] = self.curstreak = min(-1, self.curstreak - 1)
        else:
            self.l.streak[0] = self.curstreak = 0

        if self.curstreak >= self.p.lookback:
            self.l.trend[0] = 1
        elif self.curstreak <= -self.p.lookback:
            self.l.trend[0] = -1
        else:
            self.l.trend[0] = 0