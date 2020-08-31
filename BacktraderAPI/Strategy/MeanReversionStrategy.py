from BacktraderAPI.BTStrategyBase import *
from BacktraderAPI.BTStrategyExit import *

class SMAReversionStrategy(SMAStrategyBase):
    def next(self):
        if self.smaFastCrossoverSlow == 1:
            self.buy()

        elif self.smaFastCrossoverSlow == -1:
            self.sell()

class RSIReversionStrategy(RSIStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.rsi < self.p.rsiLowerband:
                self.buy()
        elif self.position.size > 0:
            if self.rsi > self.p.rsiUpperband:
                self.sell()
        elif self.position.size < 0:
            if self.rsi < self.p.rsiLowerband:
                self.buy()

class BBandsMeanReversionStrategy(BBandsStrategyBase):

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
    def next(self):
        orders = self.broker.get_orders_open()

        if self.position.size == 0:
            if self.lower:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])
            elif self.upper:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

        else:
            if self.p.bBandExit == "median":
                if self.position.size > 0:
                    if self.crossOverBollMid != 0:
                        self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

                elif self.position.size < 0:
                    if self.crossOverBollMid != 0:
                        self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])

            elif self.p.bBandExit == "bbands":
                if self.position.size > 0:
                    if self.crossUpBollTop:
                        self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

                elif self.position.size < 0:
                    if self.crossDownBollBottom:
                        self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])

        # # Cancel open orders so we can track the median line
        # if orders:
        #     for order in orders:
        #         self.broker.cancel(order)

class WilliamsRStrategy(WillamsRStrategyBase):

    '''
    Entry Criteria:
      - Long:
          - Price close crosses down lowerband
      - Short:
          - Price close crosses up upperband
     Exit Criteria:
      - Long/Short:  Price close crosses up upperband / down lowerband
    '''

    def next(self):
        orders = self.broker.get_orders_open()

        if self.position.size == 0:  # not in the market
            if self.willRCrossoverLow == -1:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)
            if self.willRCrossoverUp == 1:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:  # longing in the market
            if self.willRCrossoverUp == 1:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:  # shorting in the market
            if self.willRCrossoverLow == -1:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)

#TODO: Multiple data feeds
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
                    self.sell(data=d)
                    self.close(data=d)