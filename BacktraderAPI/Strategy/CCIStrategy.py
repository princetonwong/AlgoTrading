from BacktraderAPI.BTStrategyBase import *
from BacktraderAPI.BTStrategyExit import *

class CCICrossHoldStrategy(CCIStrategyBase, HoldStrategyExit, ZeroLagMACDStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.cciXUpperband:
                self.order = self.buy()

            elif self.cciXLowerband:
                self.order = self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.cci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.cci > self.lowerband:
                    self.buy()

class CCICrossStrategyWithChandelierExit(CCICrossHoldStrategy, ChandelierStrategyExit):
    def next(self):
        if self.position.size == 0:
            if self.cciXUpperband:
                self.order = self.buy(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

            elif self.cciXLowerband:
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

class CCICrossStrategyWithStochasticExit(CCICrossHoldStrategy, StochasticStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.cciXUpperband:
                self.order = self.buy(data=self.data0, exectype=bt.Order.Limit, price=self.data0.close[0])

            elif self.cciXLowerband:
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

class CCICrossStrategyWithBBandKChanExit(CCICrossHoldStrategy, HoldStrategyExit, BBandsKChanSqueezeStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.squeeze.squeeze > 0:
                if self.cciXUpperband:
                    self.order = self.buy()

                elif self.cciXLowerband:
                    self.order = self.sell()


        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.cci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.cci > self.lowerband:
                    self.buy()

class CCICrossHoldHKAStrategy(HoldStrategyExit, BBandsKChanSqueezeStrategyBase, CCIHeikinAshiStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.hkacciXUpperband:
                self.buy()

            elif self.hkacciXLowerband:
                self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:  # HOLD FOR AT LEAST FEW BARS
                if self.hkacci < self.upperband:
                    self.sell()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.hkacci > self.lowerband:
                    self.buy()

