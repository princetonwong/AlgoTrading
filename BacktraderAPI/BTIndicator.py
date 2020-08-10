import backtrader as bt

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