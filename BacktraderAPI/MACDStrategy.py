from .BTStrategyBase import *
from .BTStrategyExit import *

#TODO: Update to Strategy Base and Strategy Exit
class MACDStrategyWithATRExit(MACDStrategyBase, ATRDistanceStrategyExit):
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

class ZeroLagMACDStrategy(ZeroLagMACDStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.macdHistoXZero == 1:
                self.buy()
            elif self.macdHistoXZero == -1:
                self.sell()
        elif self.position.size > 0:
            if self.macdHistoXZero == -1:
                self.sell()
        elif self.position.size < 0:
            if self.macdHistoXZero == 1:
                self.buy()