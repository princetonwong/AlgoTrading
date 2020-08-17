import backtrader as bt

'''
Default sizer:
    cerebro.addsizer(BTSizer.xxxxxx)
    
Apply sizer specific to Strategy:
    idx = cerebro.addstrategy(MyStrategy, myparam=myvalue)
    cerebro.addsizer_byidx(idx, bt.sizers.SizerFix, stake=5)

only applies to Strategies with self.buy(size=None)
'''


class LongOnlySizer(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
      if isbuy:
          return self.p.stake

      # Sell situation
      position = self.broker.getposition(data)
      if not position.size:
          return 0  # do not sell if nothing is open

      return self.p.stake

class ShortOnlySizer(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
      if not isbuy:
          return self.p.stake

      # Buy situation
      position = self.broker.getposition(data)
      if position.size:
          return 0  # do not sell if nothing is open

      return self.p.stake

class FixedSizer(bt.Sizer):
    """
    state the parameter when using the functions
    """

    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.p.stake

class FixedRerverserSizer(bt.SizerFix):

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        size = self.p.stake * (1 + (position.size != 0))
        return size

class PercentSizer(bt.Sizer):
    '''This sizer return percents of available cash

    Params:
      - ``percents`` (default: ``20``)
    '''

    params = (
        ('percents', 20),
        ('retint', False),  # return an int size or rather the float value
    )

    def __init__(self):
        pass

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if not position:
            size = cash / data.close[0] * (self.params.percents / 100)
        else:
            size = position.size

        if self.p.retint:
            size = int(size)

        return size

class AllInSizer(PercentSizer):
    '''This sizer return all available cash of broker

     Params:
       - ``percents`` (default: ``100``)
     '''
    params = (
        ('percents', 100),
    )