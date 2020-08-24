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

class DMICrossMACDCrossBBandsStrategy(bt.Strategy):

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

    params = (("maperiod", 20),
              ("dmiperiod", 14),
              ("adxBenchmark", 30),
              ('macdFast', 12),
              ('macdSlow', 26),
              ('difPeriod', 9),
              ("bbandperiod", 20),
              ("sd", 2),
              ("debug", False)
              )

    def __init__(self):
        self.ma = bt.indicators.MovingAverageSimple(self.p.maperiod)

        self.dmi = bt.indicators.DirectionalMovementIndex(self.data, period=self.p.dmiperiod)
        self.dicross = bt.indicators.CrossOver(self.dmi.plusDI, self.dmi.minusDI, subplot=True)

        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macdFast,
                                       period_me2=self.p.macdSlow,
                                       period_signal=self.p.difPeriod, subplot=False)
        self.macdcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal, subplot=True)

        self.boll = bt.indicators.BollingerBands(period=self.p.bbandperiod, devfactor=self.p.sd, subplot=True)
        self.bbandlower = bt.indicators.CrossDown(self.data.close, self.boll.lines.bot, subplot=False)
        self.bbandupper = bt.indicators.CrossUp(self.data.close, self.boll.lines.top, subplot=False)


    def next(self):

        orders = self.broker.get_orders_open()

        if self.dmi.adx > self.p.adxBenchmark:

            if self.position.size == 0:  # not in the market

                if self.self.dmi.plusDI > self.dmi.minusDI and self.data.close > self.ma.sma and self.macdcross == 1:
                    if self.bbandupper:
                        self.buy(exectype=bt.Order.Stop, price=self.data.close)
                if self.self.dmi.plusDI < self.dmi.minusDI and self.data.close < self.ma.sma and self.macdcross == -1:
                    if self.bbandlower:
                        self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size > 0:  # longing in the market

                if self.self.dmi.plusDI < self.dmi.minusDI and self.data.close < self.ma.sma and self.macdcross == -1:
                    if self.bbandlower:
                        self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size < 0:  # shorting in the market

                if self.self.dmi.plusDI > self.dmi.minusDI and self.data.close > self.ma.sma and self.macdcross == 1:
                    if self.bbandupper:
                        self.buy(exectype=bt.Order.Stop, price=self.data.close)

            elif self.p.debug:
                self.debug()
