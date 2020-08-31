import backtrader as bt
from BacktraderAPI import BTIndicator

class HoldStrategyExit(bt.Strategy):
    params = dict(hold= 5)

    def __init__(self):
        super(HoldStrategyExit, self).__init__()
        self.holding = dict()

    def notify_order(self, order):
        super(HoldStrategyExit, self).notify_order(order)
        if order.status in [order.Completed]:  # HOLD FOR AT LEAST FEW BARS
            self.bar_executed = 0
            self.holdstart = len(self)
            
class ATRDistanceStrategyExit(bt.Strategy):
    '''
     - Set a stop price x times the ATR value away from the close

     - If in the market:
       - Check if the current close has gone below the stop price. If yes,
         exit.
       - If not, update the stop price if the new stop price would be higher
         than the current
    '''
    
    params = dict(atrPeriod=14, atrDistance=3, smaPeriod=30, lookback=10)
    
    def __init__(self):
        super(ATRDistanceStrategyExit, self).__init__()
        self.atr = bt.ind.ATR(period=self.p.atrPeriod)
    
    def next(self): #TODO:
        pclose = self.data.close[0]
        pstop = self.pstop

        if pclose < pstop:
            self.close()  # stop met - get out
        else:
            pdist = self.atr[0] * self.p.atrDistance
            # Update only if greater than
            self.pstop = max(pstop, pclose - pdist)

class ChandelierStrategyExit(bt.Strategy):
    params = dict(chandelierPeriod=22, multiplier=3)

    def __init__(self):
        super(ChandelierStrategyExit, self).__init__()
        self.chandelier = BTIndicator.ChandelierExit(period=self.p.chandelierPeriod, multip=self.p.multiplier)
        self.crossOverChandelierLong = bt.ind.CrossOver(self.data, self.chandelier.long, plot=False)
        self.crossOverChandelierLong.csv = True
        self.crossOverChandelierShort = bt.ind.CrossOver(self.data, self.chandelier.short, plot=False)
        self.crossOverChandelierShort.csv = True