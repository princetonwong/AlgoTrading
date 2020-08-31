from BacktraderAPI.BTStrategyBase import *
from BacktraderAPI.BTStrategyExit import *

class StochRSIStrategy(StochRSIStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.stochRSIKXD == -1 and self.stochRSI.stochRSIK >= self.p.upperband:
                self.sell()
            elif self.stochRSIKXD == 1 and self.stochRSI.stochRSIK <= self.p.lowerband:
                self.buy()
        elif self.position.size < 0:
            if self.stochRSIKXD == 1:
                self.close()
        elif self.position.size > 0:
            if self.stochRSIKXD == -1:
                self.close()

class DTOStrategy(DTOStrategyBase, StochRSIStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.dtoCxUpper == 1:
                self.buy()
            elif self.dtoCxLower == -1:
                self.sell()
        elif self.position.size > 0:
            if self.dtoCxUpper == -1:
                self.sell()
        elif self.position.size < 0:
            if self.dtoCxLower == 1:
                self.buy()
