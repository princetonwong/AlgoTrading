from BacktraderAPI.BTStrategyBase import *
from BacktraderAPI.BTStrategyExit import *

class CCICrossStrategy(CCIStrategyBase, HoldStrategyExit, BBandsKChanSqueezeStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.cciCrossUpperband:
                self.order = self.buy()

            elif self.cciCrossLowerband:
                self.order = self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.cci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.cci > self.lowerband:
                    self.buy()

class CCICrossStrategyWithChandelierExit(CCICrossStrategy, ChandelierStrategyExit):
    def next(self):
        if self.position.size == 0:
            if self.cciCrossUpperband:
                self.order = self.buy(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

            elif self.cciCrossLowerband:
                self.order = self.sell(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.crossOverChandelierLong == -1 or self.crossOverChandelierShort == -1:
                    self.sell()

                elif self.cci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.crossOverChandelierLong == 1 or self.crossOverChandelierShort == 1:
                    self.buy()
                elif self.cci > self.lowerband:
                    self.buy()

class CCICrossStrategyWithStochasticExit(CCICrossStrategy, StochasticStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.cciCrossUpperband:
                self.order = self.buy(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

            elif self.cciCrossLowerband:
                self.order = self.sell(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.kCrossOverD == 1:
                    self.close(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

                elif self.cci < self.upperband:
                    self.close(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.kCrossOverD == -1:
                    self.close(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

                elif self.cci > self.lowerband:
                    self.close(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

class CCICrossStrategyWithBBandKChanExit(CCICrossStrategy, HoldStrategyExit, BBandsKChanSqueezeStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.squeeze.squeeze > 0:
                if self.cciCrossUpperband:
                    self.order = self.buy()

                elif self.cciCrossLowerband:
                    self.order = self.sell()


        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.cci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.cci > self.lowerband:
                    self.buy()