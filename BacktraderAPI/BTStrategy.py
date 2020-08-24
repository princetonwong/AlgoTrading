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
            self.inds[d]['cross'] = bt.indicators.CrossOver(self.inds[d]['sma1'],self.inds[d]['sma2'], subplot = False)

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
        self.macd.csv = True

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
    params = dict(period=26, factor=0.015, threshold=100, hold=5)

    def __init__(self):
        self.holding = dict()
        self.order = None
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        self.upperband = self.p.threshold
        self.lowerband = -self.p.threshold
        self.cci = BTIndicator.talibCCI(period=self.p.period, factor=self.p.factor, upperband=self.upperband, lowerband=self.lowerband)
        self.cci.csv= True

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
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.cci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.cci > self.lowerband:
                    self.buy()

class CCICrossStrategyWithSLOWKDExit(CCICrossStrategy):

    params = dict(period=5, period_dfast=3, period_dslow=3)

    def __init__(self):
        super(CCICrossStrategyWithSLOWKDExit, self).__init__()
        # self.p.period, self.p.period_dfast, self.p.period_dslow = self.p.cciParameters
        self.stoch = bt.ind.StochasticFull(period= self.p.period, period_dfast= self.p.period_dfast, period_dslow= self.p.period_dslow, safediv=True)
        self.kCrossupD = bt.ind.CrossUp(self.stoch.percK, self.stoch.percD, subplot= False)
        self.kCrossdownD = bt.ind.CrossDown(self.stoch.percK, self.stoch.percD, subplot= False)

    def next(self):
        if self.order:
            return

        # If we are not in the market,
        if self.position.size == 0:
            if self.upperCrossover:
                self.order = self.buy(data= self.data0, exectype=bt.Order.Limit ,price = self.data0.close[0])

            elif self.lowerCrossover:
                self.order = self.sell(data= self.data0, exectype=bt.Order.Limit ,price = self.data0.close[0])

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.kCrossupD:
                    self.close(data= self.data0, exectype=bt.Order.Limit ,price = self.data0.close[0])
                    print ("kCrossupD exit: CCI:{}".format(self.cci[0]))
                    return

                if self.cci < self.upperband:
                    self.close(data= self.data0, exectype=bt.Order.Limit ,price = self.data0.close[0])

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.kCrossdownD:
                    self.close(data= self.data0, exectype=bt.Order.Limit ,price = self.data0.close[0])
                    print ("kCrossdownD exit: CCI:{}".format(self.cci[0]))
                    return
                if self.cci > self.lowerband:
                    self.close(data= self.data0, exectype=bt.Order.Limit ,price = self.data0.close[0])

class CCICrossStrategyWithSLOWKDExitHeikinAshi(CCICrossStrategyWithSLOWKDExit):
    def __init__(self):
        super(CCICrossStrategyWithSLOWKDExitHeikinAshi, self).__init__()
        # self.heiKinAshi = bt.ind.HeikinAshi(subplot=False)
        self.stoch = BTIndicator.HeiKinAshiStochasticFull()
        self.stoch.csv = True
        self.kCrossupD = bt.ind.CrossUp(self.stoch.percK, self.stoch.percD, subplot=False)
        self.kCrossdownD = bt.ind.CrossDown(self.stoch.percK, self.stoch.percD, subplot=False)

class ASOCrossStrategy(bt.Strategy):
    params = (
        ("period", 9),
        ('smoothing', 70.0),
        ('rsiFactor', 30.0),
    )

    def __init__(self):
        self.aso = BTIndicator.AbsoluteStrengthOscilator(period=self.p.period,
                                                         smoothing=self.p.smoothing,
                                                         rsifactor=self.p.rsiFactor)
        self.crossover = bt.ind.CrossOver(self.aso.bulls, self.aso.bears, subplot=False)

    def next(self):
        if self.position.size == 0:
            if self.crossover == 1:
                self.buy()
            elif self.crossover == -1:
                self.sell()
        elif self.position.size > 0:
            if self.crossover == -1:
                self.close()
        elif self.position.size < 0:
            if self.crossover == 1:
                self.close()


class ClenowTrendFollowingStrategy(bt.Strategy):
    """The trend following strategy from the book "Following the trend" by Andreas Clenow."""
    alias = ('ClenowTrendFollowing',)

    params = (
        ('trend_filter_fast_period', 50),
        ('trend_filter_slow_period', 100),
        ('fast_donchian_channel_period', 25),
        ('slow_donchian_channel_period', 50),
        ('trailing_stop_atr_period', 100),
        ('trailing_stop_atr_count', 3),
        ('risk_factor', 0.002)
    )

    def __init__(self):
        self.trend_filter_fast = bt.indicators.EMA(period=self.params.trend_filter_fast_period)
        self.trend_filter_slow = bt.indicators.EMA(period=self.params.trend_filter_slow_period)
        self.dc_fast = BTIndicator.DonchianChannels(period=self.params.fast_donchian_channel_period)
        self.dc_slow = BTIndicator.DonchianChannels(period=self.params.slow_donchian_channel_period)
        self.atr = bt.indicators.ATR(period=self.params.trailing_stop_atr_period)
        self.order = None  # the pending order
        # For trailing stop loss
        self.sl_order = None  # trailing stop order
        self.sl_price = None
        self.max_price = None  # track the highest price after opening long positions
        self.min_price = None  # track the lowest price after opening short positions

    def next(self):
        # self.dc_slow.dcl <= self.dc_fast.dcl <= self.dc_fast.dch <= self.dc_slow.dch
        assert self.dc_slow.dcl <= self.dc_fast.dcl
        assert self.dc_fast.dcl <= self.dc_fast.dch
        assert self.dc_fast.dch <= self.dc_slow.dch

        if not self.position:  # Entry rules
            assert self.position.size == 0

            # Position size rule
            max_loss = self.broker.get_cash() * self.p.risk_factor  # cash you afford to loss
            position_size = max_loss / self.atr[0]

            if self.data.close > self.dc_slow.dch:
                if self.trend_filter_fast > self.trend_filter_slow:  # trend filter
                    if self.order:
                        self.broker.cancel(self.order)
                    else:
                        # Entry rule 1
                        self.order = self.buy(price=self.data.close[0], size=position_size, exectype=bt.Order.Limit)
                        self.max_price = self.data.close[0]
            elif self.data.close < self.dc_slow.dcl:
                if self.trend_filter_fast < self.trend_filter_slow:  # trend filter
                    if self.order:
                        self.broker.cancel(self.order)
                    else:
                        # Entry rule 2
                        self.order = self.sell(price=self.data.close[0], size=position_size, exectype=bt.Order.Limit)
                        self.min_price = self.data.close[0]
        else:
            assert self.position.size
            # assert self.order is None

            # Exit rules
            if self.position.size > 0:
                # Exit rule 1
                if self.data.close < self.dc_fast.dcl:
                    self.order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.data.close[0])
                    return
            else:
                # Exit rule 2
                if self.data.close > self.dc_fast.dch:
                    self.order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.data.close[0])
                    return

            # Trailing stop loss
            trail_amount = self.atr[0] * self.p.trailing_stop_atr_count
            if self.position.size > 0:
                self.max_price = self.data.close[0] if self.max_price is None else max(self.max_price,
                                                                                       self.data.close[0])
                if self.sl_price is None or self.sl_price < self.max_price - trail_amount:
                    self.sl_price = self.max_price - trail_amount  # increase trailing price
                    if self.sl_order:
                        self.broker.cancel(self.sl_order)
                    else:
                        self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)
            elif self.position.size < 0:
                self.min_price = self.data.close[0] if self.min_price is None else min(self.min_price,
                                                                                       self.data.close[0])
                if self.sl_price is None or self.sl_price > self.min_price + trail_amount:
                    self.sl_price = self.min_price + trail_amount  # decrease trailing price
                    if self.sl_order:
                        self.broker.cancel(self.sl_order)
                    else:
                        self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)

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

class DMIStrategy(bt.Strategy):

    '''
         Entry Critria:
          - Long:
              - +DI > -DI
              - ADX > Benchmark
          - Short:
              - +DI < -DI
              - ADX > Benchmark

         Exit Critria
          - Long/Short: Same as opposite
    '''

    params = (("period", 14),
              ("adxBenchmark", 30),
              ("debug", False)
             )

    def __init__(self):
        self.dmi = bt.indicators.DirectionalMovementIndex(self.data, period=self.p.period)
        self.dicross = bt.indicators.CrossOver(self.dmi.plusDI, self.dmi.minusDI, subplot=True)

    def next(self):

        orders = self.broker.get_orders_open()

        if self.dmi.adx > self.p.adxBenchmark:

            if self.position.size == 0:  # not in the market

                if self.dicross == 1:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)
                if self.dicross == -1:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size > 0:  # longing in the market

                if self.dicross == -1:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size < 0:  # shorting in the market

                if self.dicross == 1:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)

            if self.p.debug:
                self.debug()

