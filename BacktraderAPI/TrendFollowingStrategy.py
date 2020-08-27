from .BTStrategyBase import *

class DonchianStrategy(DonchianStrategyBase):
    '''
         Entry Critria:
          - Long:
              - Price closes above the upper band
          - Short:
              - Price closes below the lower band
         Exit Critria
          - Long/Short: When price crosses the mid, exit
    '''

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

class BBandsTrendFollowingStrategy(BBandsStrategyBase):
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
            if self.crossDownBollBottom:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])
            elif self.crossUpBollTop:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

        elif self.position.size > 0:
            if self.crossOverBollMid != 0:
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.bot[0])

        elif self.position.size < 0:
            if self.crossOverBollMid != 0:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.top[0])

        # # Cancel open orders so we can track the median line
        # if orders:
        #     for order in orders:
        #         self.broker.cancel(order)
