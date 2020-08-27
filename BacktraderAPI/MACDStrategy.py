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

class MACDxDMIxBBandsStrategy(MACDStrategyBase, BBandsStrategyBase, DMIStrategyBase, SMAStrategyBase):

    '''
             Entry Critria:
              - Long:
                  1. Price close > MA
                  2. +DI > -DI
                  3. ADX > Benchmark
                  4. Price crosses above the upper BBand
              - Short:
                  1. Price close < MA
                  2. +DI < -DI
                  3. ADX > Benchmark
                  4. Price crosses below the lower BBand

             Exit Critria
              - Long/Short: Same as opposite
    '''
    dict(macdFast=12, macdSlow=26, diffPeriod=9)
    dict(movAvPeriod=20, bBandSD=2, bBandExit="median",)
    dict(dmiperiod=14, adxBenchmark=30)
    dict(SMAFastPeriod=10, SMASlowPeriod=20)

    def next(self):

        orders = self.broker.get_orders_open()

        if self.dmi.adx > self.p.adxBenchmark:

            if self.position.size == 0:  # not in the market
                if self.dmi.plusDI > self.dmi.minusDI and self.data.close > self.sma2 and self.mcross == 1:
                    if self.crossUpBollTop:
                        self.buy(exectype=bt.Order.Stop, price=self.data.close)
                if self.dmi.plusDI < self.dmi.minusDI and self.data.close < self.sma2 and self.mcross == -1:
                    if self.crossDownBollBottom:
                        self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size > 0:  # longing in the market
                if self.dmi.plusDI < self.dmi.minusDI and self.data.close < self.sma2 and self.mcross == -1:
                    if self.crossDownBollBottom:
                        self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size < 0:  # shorting in the market
                if self.dmi.plusDI > self.dmi.minusDI and self.data.close > self.sma2 and self.mcross == 1:
                    if self.crossUpBollTop:
                        self.buy(exectype=bt.Order.Stop, price=self.data.close)