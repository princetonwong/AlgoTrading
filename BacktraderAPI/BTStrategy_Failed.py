import backtrader as bt
from BacktraderAPI import BTIndicator

#All bt indicators: https://www.backtrader.com/docu/indautoref/

#Mean Reversion

#Trend Following

class AroonWithEMAStrategy(bt.Strategy):


    '''

        Failed:

              - Long:
                - close is above 200 EMA
                - Aroon Long crosses above 30

              - Short:
                - close is below 200 EMA
                - Aroon Short crosses above 30

              - Exit Criteria:
                - Long: Close Buy when Aroon Long crosses below 70
                - Short: Close Sell when Aroon Short crosses below 70


    '''

    params = (
                ("period", 25),
                ("upperband", 100),
                ("lowerband", 0),
                ("debug", False)
              )

    def __init__(self):
        self.aroon = bt.indicators.AroonUpDownOscillator(self.data, period=self.p.period)
        self.arooncross = bt.indicators.CrossOver(self.aroon.aroonup, self.aroon.aroondown, subplot=True)
        self.aroon.csv=True

    def next(self):

        orders = self.broker.get_orders_open()

        if self.position.size == 0:  # not in the market

            if self.aroon.aroonup == self.p.upperband and self.aroon.aroondown == self.p.lowerband:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)
            if self.aroon.aroondown == self.p.upperband and self.aroon.aroonup == self.p.lowerband:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:  # longing in the market

            if self.aroon.aroondown == self.p.upperband and self.aroon.aroonup == self.p.lowerband:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:  # shorting in the market

            if self.aroon.aroonup == self.p.upperband and self.aroon.aroondown == self.p.lowerband:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)

        if self.p.debug:
            self.debug()


