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
        self.chandelier = BTIndicator.ChandelierExit(period=self.p.chandelierPeriod, multiplier=self.p.multiplier)
        self.xChandLong = bt.ind.CrossOver(self.data, self.chandelier.chandLong, plot=False)
        self.xChandLong.csv = True
        self.xChandShort = bt.ind.CrossOver(self.data, self.chandelier.chandShort, plot=False)
        self.xChandShort.csv = True

class StopTrailStrategyBase(HoldStrategyExit):
    params = dict(trailHold=5, takeProfitPerc= 0.06, stopLossPerc= 0.002, takeProfitAmount= None, stopLossAmount= None)

    def __init__(self):
        print (self.params)
        super(StopTrailStrategyBase, self).__init__()
        # init stop loss and take profit order variables
        self.sl_order, self.tp_order = None, None
        self.sl_price = 0.0
        self.tp_price = 0.0
        self.holding = dict()

    def notify_order(self, order):
        super(StopTrailStrategyBase, self).notify_order(order)
        if order.status in [order.Completed]:  # HOLD FOR AT LEAST FEW BARS
            self.bar_executed = 0
            self.holdstart = len(self)

    def notify_trade(self, trade):
        super(StopTrailStrategyBase, self).notify_trade(trade, debug= False)
        if trade.isclosed:
            # clear stop loss and take profit order variables for no position state
            if self.sl_order:
                self.broker.cancel(self.sl_order)
                self.sl_order = None

            if self.tp_order:
                self.broker.cancel(self.tp_order)
                self.tp_order = None

    def next(self):
        super(StopTrailStrategyBase, self).next()
        # process stop loss and take profit signals
        if self.position:
            # set stop loss and take profit prices
            # in case of trailing stops stop loss prices can be assigned based on current indicator value
            if self.p.takeProfitAmount != None:
                price_takeProfit_long = self.position.price + self.p.takeProfitAmount
                price_takeProfit_short = self.position.price - self.p.takeProfitAmount
            else:
                price_takeProfit_long = self.position.price * (1 + self.p.takeProfitPerc)
                price_takeProfit_short = self.position.price * (1 - self.p.takeProfitPerc)

            if self.p.stopLossAmount != None:
                price_stopLoss_long = self.position.price - self.p.stopLossAmount
                price_stopLoss_short = self.position.price + self.p.stopLossAmount
            else:
                price_stopLoss_long = self.position.price * (1 - self.p.stopLossPerc)
                price_stopLoss_short = self.position.price * (1 + self.p.stopLossPerc)


            # cancel existing stop loss and take profit orders
            if self.sl_order:
                self.broker.cancel(self.sl_order)

            if self.tp_order:
                self.broker.cancel(self.tp_order)

            # check & update stop loss order
            self.sl_price = 0.0
            if self.position.size > 0 and price_stopLoss_long != 0: self.sl_price = price_stopLoss_long
            if self.position.size < 0 and price_stopLoss_short != 0: self.sl_price = price_stopLoss_short

            if self.sl_price != 0.0:
                if (len(self) - self.holdstart) >= self.p.trailHold:
                    print ("stop loss triggered")
                    self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)

            # check & update take profit order
            self.tp_price = 0.0
            if self.position.size > 0 and price_takeProfit_long != 0: self.tp_price = price_takeProfit_long
            if self.position.size < 0 and price_takeProfit_short != 0: self.tp_price = price_takeProfit_short

            if self.tp_price != 0.0:
                if (len(self) - self.holdstart) >= self.p.trailHold:
                    self.tp_order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.tp_price)