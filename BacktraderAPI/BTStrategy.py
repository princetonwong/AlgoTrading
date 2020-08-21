import backtrader as bt
from BacktraderAPI import BTIndicator

#All bt indicators: https://www.backtrader.com/docu/indautoref/

#Mean Reversion
class SmaCrossStrategy(bt.Strategy):
    params = (("fastP", 10),
              ("slowP", 20))

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        sma1, sma2 = bt.ind.SMA(period=self.p.fastP), bt.ind.SMA(period=self.p.slowP)
        self.crossup = bt.ind.CrossUp(sma1, sma2)
        self.crossdown = bt.ind.CrossDown(sma1, sma2)


    def next(self):
        if self.crossup:
            self.buy()
            self.log('BUY CREATE, %.2f' % self.dataclose[0])

        elif self.crossdown:
            self.sell()
            self.log('SELL CREATE, %.2f' % self.dataclose[0])

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash, 2)
        print('RSI Period: {} Final PnL: {}'.format(
            self.params.slowP, pnl))

class RSIStrategy(bt.Strategy):
    params = (
        ("period", 21),
        ('upperband', 70.0),
        ('lowerband', 30.0),
             )

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.p.period)

    def next(self):
        if self.position.size == 0:
            if self.rsi < self.p.lowerband:
                self.buy()
        elif self.position.size > 0:
            if self.rsi > self.p.upperband:
                self.sell()
        elif self.position.size < 0:
            if self.rsi < self.p.lowerband:
                self.buy()

class MACrossStrategy(bt.Strategy):
    '''
    For an official backtrader blog on this topic please take a look at:
    https://www.backtrader.com/blog/posts/2017-04-09-multi-example/multi-example.html
    oneplot = Force all datas to plot on the same master.
    '''
    params = (
    ('sma1', 10),
    ('sma2', 20),
    ('oneplot', True)
    )

    def __init__(self):
        '''
        Create an dictionary of indicators so that we can dynamically add the
        indicators to the strategy using a loop. This mean the strategy will
        work with any number of data feeds.
        '''
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['sma1'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma1)
            self.inds[d]['sma2'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma2)
            self.inds[d]['cross'] = bt.indicators.CrossOver(self.inds[d]['sma1'],self.inds[d]['sma2'])

            if i > 0: #Check we are not on the first loop of data feed:
                if self.p.oneplot == True:
                    d.plotinfo.plotmaster = self.datas[0]

    def next(self):
        for i, d in enumerate(self.datas): #looping through the data feeds one by one
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:  # no market / no orders
                if self.inds[d]['cross'][0] == 1:
                    self.buy(data=d)
                elif self.inds[d]['cross'][0] == -1:
                    self.sell(data=d)
            else:
                if self.inds[d]['cross'][0] == 1:
                    self.close(data=d)
                    self.buy(data=d)
                elif self.inds[d]['cross'][0] == -1:
                    self.close(data=d)
                    self.sell(data=d)

class BBandsMeanReversionStrategy(bt.Strategy):

    #https://backtest-rookies.com/2018/02/23/backtrader-bollinger-mean-reversion-strategy/

    '''
    This is a simple mean reversion bollinger band strategy.

     Entry Critria:
      - Long:
          - Price closes below the lower band
          - Stop Order entry when price crosses back above the lower band
      - Short:
          - Price closes above the upper band
          - Stop order entry when price crosses back below the upper band
     Exit Critria
      - Long/Short: Price touching the median line
    '''

    params = (
        ("period", 20),
        ("sd", 2),
        ("exit", "median"),
        ("debug", False)
              )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.sd)
        self.lower = bt.indicators.CrossDown(self.data.close, self.boll.lines.bot, subplot = False)
        self.upper = bt.indicators.CrossUp(self.data.close, self.boll.lines.top, subplot = False)
        self.crossMid = bt.indicators.CrossOver(self.data.close, self.boll.lines.mid, subplot = False)

    def next(self):
        orders = self.broker.get_orders_open()

        if self.position.size == 0:
            if self.lower:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])
            elif self.upper:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

        else:

            if self.p.exit == "median":

                if self.position.size > 0:
                    if self.crossMid != 0:
                        self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

                elif self.position.size < 0:
                    if self.crossMid != 0:
                        self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])

            elif self.p.exit == "bbands":

                if self.position.size > 0:
                    if self.upper:
                        self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

                elif self.position.size < 0:
                    if self.lower:
                        self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])

        # # Cancel open orders so we can track the median line
        # if orders:
        #     for order in orders:
        #         self.broker.cancel(order)

        if self.p.debug:
            self.debug()

class MACDCrossStrategy(bt.Strategy):
    '''
    This strategy is loosely based on some of the examples from the Van
    K. Tharp book: *Trade Your Way To Financial Freedom*. The logic:

      - Enter the market if:
        - The MACD.macd line crosses the MACD.signal line to the upside
        - The Simple Moving Average has a negative direction in the last x
          periods (actual value below value x periods ago)

     - Set a stop price x times the ATR value away from the close

     - If in the market:

       - Check if the current close has gone below the stop price. If yes,
         exit.
       - If not, update the stop price if the new stop price would be higher
         than the current
    '''

    params = (
        # Standard MACD Parameters
        ('macdFast', 12),
        ('macdSlow', 26),
        ('difPeriod', 9),
    )
    #     ('atrperiod', 14),  # ATR Period (standard)
    #     ('atrdist', 3.0),   # ATR distance for stop price
    #     ('smaperiod', 30),  # SMA Period (pretty standard)
    #     ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    # )

    # def notify_order(self, order):
    #     if order.status == order.Completed:
    #         pass
    #
    #     if not order.alive():
    #         self.order = None  # indicate no order is pending

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macdFast,
                                       period_me2=self.p.macdSlow,
                                       period_signal=self.p.difPeriod, subplot=False)

        self.macdHistogram = BTIndicator.MACDHistogram(period_me1=self.p.macdFast, period_me2=self.p.macdSlow, period_signal=self.p.difPeriod)

        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal, subplot= False)

    # def start(self):
    #     self.order = None  # sentinel to avoid operations on pending order

    def next(self):
        # if self.order:
        #     return  # pending order execution

        if self.position.size == 0:  # not in the market
            if self.mcross == 1:
                self.buy()
            if self.mcross == -1:
                self.sell()

        elif self.position.size != 0:
            if self.mcross == -1 or self.mcross == 1:
                self.close()

        # else:  # in the market
        #     pclose = self.data.close[0]
        #     pstop = self.pstop
        #
        #     if pclose < pstop:
        #         self.close()  # stop met - get out
        #     else:
        #         pdist = self.atr[0] * self.p.atrdist
        #         # Update only if greater than
        #         self.pstop = max(pstop, pclose - pdist)

class WilliamsRStrategy(bt.Strategy):

    '''
    Entry Criteria:
      - Long:
          - Price close crosses down lowerband
      - Short:
          - Price close crosses up upperband
     Exit Criteria:
      - Long/Short:  Price close crosses up upperband / down lowerband
    '''

    params = (
        ('period', 14),
        ('upperband', -20),
        ('lowerband', -80),
        ("debug", False)
             )

    def __init__(self):
        self.williamsR = bt.indicators.WilliamsR(self.data,
                                                 period=self.p.period,
                                                 upperband=self.p.upperband,
                                                 lowerband=self.p.lowerband,
                                                 )
        self.crossLowerBand = bt.indicators.CrossOver(self.williamsR, self.p.lowerband, subplot=False)
        self.crossUpperBand = bt.indicators.CrossOver(self.williamsR, self.p.upperband, subplot=False)

    def next(self):
        orders = self.broker.get_orders_open()

        if self.position.size == 0:  # not in the market

            if self.crossLowerBand == -1:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)
            if self.crossUpperBand == 1:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:  # longing in the market

            if self.crossUpperBand == 1:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:  # shorting in the market

            if self.crossLowerBand == -1:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)

        if self.p.debug:
            self.debug()

#Trend Following
class DonchianStrategy(bt.Strategy):
    def __init__(self):
        self.donc = BTIndicator.DonchianChannels()
        self.dataclose = self.datas[0].close

    def next(self):
        if self.position.size == 0:
            if self.data > self.donc.dch:
                self.buy()

            elif self.data < self.donc.dcl:
                self.sell()

        elif self.position.size > 0:
            if self.data < self.donc.dcm:
                self.close()

        elif self.position.size < 0:
            if self.data > self.donc.dcm:
                self.close()

class CCICrossStrategy(bt.Strategy):
    params = dict(cciParameters = (26,0.015,100,5))

    def __init__(self):
        self.holding = dict()
        self.order = None
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        n, a, cciThreshold, self.hold = self.p.cciParameters
        self.upperband = cciThreshold
        self.lowerband = -cciThreshold
        self.cci = bt.ind.CommodityChannelIndex(period=n, factor=a, upperband=self.upperband, lowerband=self.lowerband)

        self.upperCrossover = bt.ind.CrossUp(self.cci, self.upperband, subplot = False)
        self.lowerCrossover = bt.ind.CrossDown(self.cci, self.lowerband, subplot = False)

    def notify_order(self, order):
        super(CCICrossStrategy, self).notify_order(order)
        if order.status in [order.Completed]:
            self.bar_executed = 0
            self.holdstart = len(self)

    def next(self):
        if self.order:
            return

        # If we are not in the market,
        if self.position.size == 0:
            if self.upperCrossover:
                self.order = self.buy()

            elif self.lowerCrossover:
                self.order = self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.hold:
                if self.cci < self.upperband:
                    self.close()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.hold:
                if self.cci > self.lowerband:
                    self.close()

class CCICrossStrategyWithSLOWKDExit(CCICrossStrategy):
    '''
    ('period', 14), ('period_dfast', 3), ('period_dslow', 3),)
    '''
    params = dict(stochParameters=(5, 3, 3))

    def __init__(self):
        super(CCICrossStrategyWithSLOWKDExit, self).__init__()
        # self.p.period, self.p.period_dfast, self.p.period_dslow = self.p.cciParameters
        self.stoch = bt.ind.StochasticFull()
        self.kCrossupD = bt.ind.CrossUp(self.stoch.percK, self.stoch.percD, subplot= False)
        self.kCrossdownD = bt.ind.CrossDown(self.stoch.percK, self.stoch.percD, subplot= False)

    def next(self):
        if self.order:
            return

        # If we are not in the market,
        if self.position.size == 0:
            if self.upperCrossover:
                self.order = self.buy()

            elif self.lowerCrossover:
                self.order = self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.hold:
                if self.kCrossupD:
                    self.close()
                    print ("kCrossupD exit: CCI:{}".format(self.cci[0]))
                    return

                if self.cci < self.upperband:
                    self.close()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.hold:
                if self.kCrossdownD:
                    self.close()
                    print ("kCrossdownD exit: CCI:{}".format(self.cci[0]))
                    return
                if self.cci > self.lowerband:
                    self.close()

class BBandsTrendFollowingStrategy(BBandsMeanReversionStrategy):
    '''
         Entry Critria:
          - Long:
              - Price closes above the upper band
          - Short:
              - Price closes below the lower band
         Exit Critria
          - Long/Short: When price crosses the mid, exit at bottom/top
        '''

    def next(self):
        orders = self.broker.get_orders_open()

        if self.position.size == 0:
            if self.lower:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])
            elif self.upper:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

        elif self.position.size > 0:
            if self.crossMid != 0:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])

        elif self.position.size < 0:
            if self.crossMid != 0:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

        # # Cancel open orders so we can track the median line
        # if orders:
        #     for order in orders:
        #         self.broker.cancel(order)

        if self.p.debug:
            self.debug()
