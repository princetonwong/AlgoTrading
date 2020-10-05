import backtrader as bt
import datetime

class BracketBuying(bt.Strategy):
    params = dict(
        limit=0.005,        #TODO: What is this?
        limdays=3,
        limdays2=1000,
        limdays3=1000,
        limdays4=10,
        stopLossTrailPercent=0.02,
        takeProfitPercent=0.1,
    )

    def __init__(self):
        super(BracketBuying, self).__init__()
        self.bb1, self.bb2, self.bb3, self.bb4 = None, None, None, None
        self.sb1, self.sb2, self.sb3, self.sb4 = None, None, None, None

    def closeBuyBracket(self):
        p4 = self.data.close[0]
        valid4 = datetime.timedelta(self.p.limdays4)
        self.broker.cancel(self.bb2)
        self.bb4 = self.sell(exectype=bt.Order.Market,
                             price=p4,
                             valid=valid4,
                             size=self.bb1.size)
        print('{}: Sell at {}'.format(self.datetime.date(), p4))

    def closeSellBracket(self):
        p4 = self.data.close[0]
        valid4 = datetime.timedelta(self.p.limdays4)
        self.broker.cancel(self.sb2)
        self.sb4 = self.buy(exectype=bt.Order.Market,
                            price=p4,
                            valid=valid4,
                            size=self.sb1.size)
        print('{}: Buy at {}'.format(self.datetime.date(), p4))

    def sellWithBracket(self):
        p1 = self.data.close[0]
        p3 = p1 * (1 - self.p.takeProfitPercent)
        valid1 = datetime.timedelta(self.p.limdays)
        valid2 = datetime.timedelta(self.p.limdays2)
        valid3 = datetime.timedelta(self.p.limdays3)

        self.sb1 = self.sell(exectype=bt.Order.Market,
                             price=p1,
                             valid=valid1,
                             transmit=False)
        print('{}: Oref {} / Sell at {}'.format(self.datetime.date(), self.sb1.ref, p1))

        self.sb2 = self.buy(exectype=bt.Order.StopTrail,
                            trailpercent=self.p.stopLossTrailPercent,
                            valid=valid2,
                            parent=self.sb1,
                            size=self.sb1.size,
                            transmit=False)
        print('{}: Oref {} / Buy StopTrail at {}'.format(self.datetime.date(), self.sb2.ref,
                                                         self.data.close[0] * (1 + self.p.trailpercent)))

        self.sb3 = self.buy(exectype=bt.Order.Limit,
                            price=p3,
                            valid=valid3,
                            parent=self.sb1,
                            size=self.sb1.size,
                            transmit=True)
        print('{}: Oref {} / Buy Limit at {}'.format(self.datetime.date(), self.sb3.ref, p3))

    def buyWithBracket(self):
        p1 = self.data.close[0]
        p3 = p1 * (1 + self.p.takeProfitPercent)
        valid1 = datetime.timedelta(self.p.limdays)
        valid2 = datetime.timedelta(self.p.limdays2)
        valid3 = datetime.timedelta(self.p.limdays3)
        self.bb1 = self.buy(exectype=bt.Order.Market,
                            price=p1,
                            valid=valid1,
                            transmit=False)
        print('{}: Oref {} / Buy at {}'.format(self.datetime.date(), self.bb1.ref, p1))

        self.bb2 = self.sell(exectype=bt.Order.StopTrail,
                             trailpercent=self.p.stopLossTrailPercent,
                             valid=valid2,
                             parent=self.bb1,
                             size=self.bb1.size,
                             transmit=False)
        print('{}: Oref {} / Sell StopTrail at {}'.format(self.datetime.date(), self.bb2.ref,
                                                          self.data.close[0] * (1 - self.p.trailpercent)))

        self.bb3 = self.sell(exectype=bt.Order.Limit,
                             price=p3,
                             valid=valid3,
                             parent=self.bb1,
                             size=self.bb1.size,
                             transmit=True)
        print('{}: Oref {} / Sell Limit at {}'.format(self.datetime.date(), self.bb3.ref, p3))