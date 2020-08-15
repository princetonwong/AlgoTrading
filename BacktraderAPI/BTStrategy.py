import backtrader as bt
from BacktraderAPI.BTIndicator import *

class BuyWhenCloseLessThanTwoPreviousStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.stochrsi = StochRSI(self.data)

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[-2] < self.dataclose[-1]:
            # current close less than previous close

            if self.dataclose[-4] < self.dataclose[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()
        if self.dataclose[-2] > self.dataclose[-1]:
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.sell()

class SmaCrossStrategy(bt.SignalStrategy):
    params = (("fastP", 5),
              ("slowP", 20))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        sma1, sma2 = bt.ind.SMA(period=self.p.fastP), bt.ind.SMA(period=self.p.slowP)
        self.crossover = bt.ind.CrossOver(sma1, sma2)


    def next(self):
        if self.crossover:
            self.buy()

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash, 2)
        print('RSI Period: {} Final PnL: {}'.format(
            self.params.slowP, pnl))

class DonchianStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.myind = DonchianChannels()
        self.dataclose = self.datas[0].close

    def next(self):
        if self.data[0] > self.myind.dch[0]:
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.buy()
        elif self.data[0] < self.myind.dcl[0]:
            self.sell()

class CCICrossStrategy(bt.SignalStrategy):
    params = dict(cciParameters = (20,0.015,100,7)
                  )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('CCI: %s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.holding = dict()
        self.order = None
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        n, a, cciThreshold, self.hold = self.p.cciParameters
        self.upperband = cciThreshold
        self.lowerband = -cciThreshold
        self.cci = bt.ind.CommodityChannelIndex(period=n, factor=a, upperband=self.upperband, lowerband=self.lowerband)

        self.upperCrossover = bt.ind.CrossUp(self.cci, self.upperband)
        self.signal_add(bt.SIGNAL_LONG, self.upperCrossover)
        #
        self.lowerCrossover = bt.ind.CrossDown(self.cci, self.lowerband)
        self.signal_add(bt.SIGNAL_SHORT, self.lowerCrossover)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.8f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.8f' % order.executed.price)

            self.bar_executed = 0
            self.holdstart = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.8f, NET %.f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        if self.order:
            return

        # If we are not in the market,
        if not self.position:
            if self.upperCrossover:
                self.log('BUY CREATE, %.8f' % self.dataclose[0])
                self.order = self.buy(price=self.dataclose[0])

                # self.log('BUY CREATE, %.8f' % self.dataopen[0])
                # self.order = self.buy(price=self.dataopen[0])
                # self.order = self.buy()

            else:
                if self.lowerCrossover:
                    self.log('SELL CREATE, %.8f' % self.dataclose[0])
                    self.order = self.sell(price=self.dataclose[0])

                    # self.log('SELL CREATE, %.8f' % self.dataopen[0])
                    # self.order = self.sell(price=self.dataopen[0])

                    # self.order = self.sell()

        # If we are in the market,
        elif self.position:
            if (len(self) - self.holdstart) >= self.hold:
                if self.cci < self.upperband:
                    self.close()
                    self.log('BUY POSITION CLOSED, exectype Close, price %.2f' %
                             self.data.close[0])
                elif self.cci > self.lowerband:
                    self.close()
                    self.log('SELL POSITION CLOSED, exectype Close, price %.2f' %
                             self.data.close[0])

class firstStrategy(bt.Strategy):
    params = (
        ('period',21),
        )

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.rsi = bt.indicators.RSI_SMA(self.datas[0].close, period=self.params.period)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        print('RSI Period: {} Final PnL: {}'.format(
            self.params.period, pnl))

class RSIStrategy(bt.Strategy):
    params = (
        ('upperband', 70.0),
        ('lowerband', 30.0),
             )
    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < self.p.lowerband:
                self.buy(size=1)
        else:
            if self.rsi > self.p.upperband:
                self.sell(size=1)
            elif self.rsi < self.p.lowerband:
                self.buy(size=1)


class BOLLStrategy(bt.Strategy):
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
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        # self.sx = bt.indicators.CrossDown(self.data.close, self.boll.lines.top)
        # self.lx = bt.indicators.CrossUp(self.data.close, self.boll.lines.bot)

    def next(self):

        orders = self.broker.get_orders_open()

        # Cancel open orders so we can track the median line
        if orders:
            for order in orders:
                self.broker.cancel(order)

        if not self.position:

            if self.data.close > self.boll.lines.top:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0], size=self.p.size)

            if self.data.close < self.boll.lines.bot:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0], size=self.p.size)


        else:

            if self.position.size > 0:
                self.sell(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)

            else:
                self.buy(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)

        if self.p.debug:
            print('---------------------------- NEXT ----------------------------------')
            print("1: Data Name:                            {}".format(data._name))
            print("2: Bar Num:                              {}".format(len(data)))
            print("3: Current date:                         {}".format(data.datetime.datetime()))
            print('4: Open:                                 {}'.format(data.open[0]))
            print('5: High:                                 {}'.format(data.high[0]))
            print('6: Low:                                  {}'.format(data.low[0]))
            print('7: Close:                                {}'.format(data.close[0]))
            print('8: Volume:                               {}'.format(data.volume[0]))
            print('9: Position Size:                       {}'.format(self.position.size))
            print('--------------------------------------------------------------------')

    def notify_trade(self, trade):
        if trade.isclosed:
            dt = self.data.datetime.date()

            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl, 2)))
            print('--------------------------------------------------------------------')