from .BTStrategyBase import *
from .BTStrategyExit import *

class PiercingCandleHoldingStrategy (PiercingCandleStrategyBase, HoldStrategyExit):
    def next(self):
        if self.position.size == 0:
            if self.trend == 1 and self.piercingCandle:
                self.buy()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                self.sell()

        elif self.position.size < 0:
                pass