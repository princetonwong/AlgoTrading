import backtrader as bt
from backtrader.indicators import MovingAverageSimple, Highest, Lowest
import numpy as np

class StochRSI(bt.Indicator):
    lines = ('stochrsi',)
    params = dict(
        period=14,  # to apply to RSI
        pperiod=None,  # if passed apply to HighestN/LowestN, else "period"
    )

    def __init__(self):
        rsi = bt.ind.RSI(self.data, period=self.p.period)

        pperiod = self.p.pperiod or self.p.period
        maxrsi = bt.ind.Highest(rsi, period=pperiod)
        minrsi = bt.ind.Lowest(rsi, period=pperiod)

        self.l.stochrsi = (rsi - minrsi) / (maxrsi - minrsi)

class CCICloseSignal(bt.Indicator):
    lines = ("CCI",)
    params = dict(n= 20,
                  a= 0.015,
                  threshold= 100,
                  m= 7
                  )

    def cal_meandev(self, tp, matp):
        mean_dev = (self.p.n - 1) * [np.nan]
        for i in range(len(tp) - self.p.n + 1):
            mean_dev.append(np.mean(abs(tp[i:i + self.p.n] - matp[i + self.p.n - 1])))
        return np.array(mean_dev)

    def __init__(self):
        tp = (self.data.close + self.data.high + self.data.low) / 3
        matp = MovingAverageSimple(tp, period=self.p.n)
        mean_dev = self.cal_meandev(tp, matp)
        cci = (tp - matp) / (self.p.a * mean_dev)

        self.l.cci = cci

class CCIExitSignal(bt.Indicator):
    lines = ("signal",)
    params = (("cciParameters",(20,0.015,100,5)),)


    def __init__(self):
        n, a, cciThreshold, m = self.p.cciParameters
        cci = bt.ind.CommodityChannelIndex(n, a, cciThreshold, -cciThreshold)

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

class MACDHistogram(bt.ind.MACDHisto):
    def __init__(self):
        super(bt.ind.MACDHisto, self).__init__()
        self.lines.histo = (self.lines.macd - self.lines.signal) * 2

# class WilliamRHorizontalLine(bt.ind.WilliamsR):


# from __future__ import (absolute_import, division, print_function, unicode_literals)

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

    lines = ('cci','meandev','dev','tp','tpmean')

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

    def __init__(self):
        # self.addminperiod(self.p.period)
        # self.l.tp = (self.data.high + self.data.low + self.data.close) / 3.0
        # self.l.tpmean = self.p.movav(self.l.tp, period=self.p.period)
        self.l.cci = bt.talib.CCI(self.data.high, self.data.low, self.data.close, timeperiod = self.p.period)

    # def next(self):
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


from backtrader.indicators import Indicator, Max, MovAv, Highest, Lowest, DivByZero
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