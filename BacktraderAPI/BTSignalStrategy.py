import backtrader as bt
from BacktraderAPI import BTIndicator 

class DonchianSignalStrategy(bt.SignalStrategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.donc = BTIndicator.DonchianChannels()
        self.dataclose = self.datas[0].close

    def next(self):
        if not self.position:
            self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossUp(self.dataclose, self.donc.dch))
            self.log('BUY CREATE, %.2f' % self.dataclose[0])

            # self.signal_add(bt.SIGNAL_SHORT, bt.ind.CrossDown(self.dataclose, self.donc.dcl))
            # self.log('SELL CREATE, %.2f' % self.dataclose[0])

        else:
            self.signal_add(bt.SIGNAL_LONGEXIT, bt.ind.CrossDown(self.dataclose, self.donc.dcm))
            self.log('LONG EXIT, %.2f' % self.dataclose[0])

            # self.signal_add(bt.SIGNAL_SHORTEXIT, bt.ind.CrossUp(self.dataclose, self.donc.dcm))
            # self.log('SHORT EXIT, %.2f' % self.dataclose[0])

class RSISignalStrategy(bt.SignalStrategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('CCI: %s, %s' % (dt.isoformat(), txt))

    params = dict(rsi_per=14, rsi_upper=65.0, rsi_lower=35.0, rsi_out=50.0,
                  warmup=35)

    def notify_order(self, order):
        super(RSISignalStrategy, self).notify_order(order)
        if order.status == order.Completed:
            print('%s: Size: %d @ Price %f' %
                  ('buy' if order.isbuy() else 'sell',
                   order.executed.size, order.executed.price))

            d = order.data
            print('Close[-1]: %f - Open[0]: %f' % (d.close[-1], d.open[0]))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.8f, NET %.f' % (trade.pnl, trade.pnlcomm))

    def __init__(self):
        # Original code needs artificial warmup phase - hidden sma to replic
        if self.p.warmup:
            bt.indicators.SMA(period=self.p.warmup, plot=False)

        rsi = bt.indicators.RSI(period=self.p.rsi_per,
                                upperband=self.p.rsi_upper,
                                lowerband=self.p.rsi_lower)

        crossup = bt.ind.CrossUp(rsi, self.p.rsi_lower)
        self.order = self.order_target_percent(data=self.data0,
                                               target=1,
                                               exectype=bt.Order.Limit,
                                               price=self.data0.open[1])
        self.signal_add(bt.SIGNAL_LONG, crossup)
        self.signal_add(bt.SIGNAL_LONGEXIT, -(rsi > self.p.rsi_out))

        crossdown = bt.ind.CrossDown(rsi, self.p.rsi_upper)
        self.signal_add(bt.SIGNAL_SHORT, -crossdown)
        self.signal_add(bt.SIGNAL_SHORTEXIT, rsi < self.p.rsi_out)