import backtrader as bt
from BacktraderAPI import BTIndicator

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
        # self.signal_add(bt.SIGNAL_LONG, self.upperCrossover)

        self.lowerCrossover = bt.ind.CrossDown(self.cci, self.lowerband)
        # self.signal_add(bt.SIGNAL_SHORT, self.lowerCrossover)

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

class maCross(bt.Strategy):
    '''
    For an official backtrader blog on this topic please take a look at:

    https://www.backtrader.com/blog/posts/2017-04-09-multi-example/multi-example.html

    oneplot = Force all datas to plot on the same master.
    '''
    params = (
    ('sma1', 50),
    ('sma2', 250),
    ('oneplot', True)
    )

    def __init__(self):
        '''
        Create an dictionary of indicators so that we can dynamically add the
        indicators to the strategy using a loop. This mean the strategy will
        work with any numner of data feeds.
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
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:  # no market / no orders
                if self.inds[d]['cross'][0] == 1:
                    self.buy(data=d, size=10)
                elif self.inds[d]['cross'][0] == -1:
                    self.sell(data=d, size=10)
            else:
                if self.inds[d]['cross'][0] == 1:
                    self.close(data=d)
                    self.buy(data=d, size=10)
                elif self.inds[d]['cross'][0] == -1:
                    self.close(data=d)
                    self.sell(data=d, size=10)

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
