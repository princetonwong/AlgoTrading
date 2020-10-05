import backtrader as bt

class NotifyOrderShowStatus(bt.Strategy):

    def notify_order(self, order):
        super(NotifyOrderShowStatus, self).notify_order(order)
        if order.getstatusname() != "Accepted":
            print('{}: Order ref: {} / Type {} / Status {}'.format(
                self.data.datetime.date(0),
                order.ref, 'Buy' * order.isbuy() or 'Sell' * order.issell(),
                order.getstatusname()))


class NotifyOrderShowPrice(bt.Strategy):

    def notify_order(self, order):
        super(NotifyOrderShowPrice, self).notify_order(order)
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

            # Check if an order has been completed
            # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = 0
            self.holdstart = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log('Order Canceled/Margin/Rejected')
            pass

        # Write down: no pending order
        self.order = None


class NotifyTradeShowInfo(bt.Strategy):

    def notify_trade(self, trade):
        super(NotifyTradeShowInfo, self).notify_trade(trade)
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                dt,
                trade.data._name,
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2)))

            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl, 2)))
            print('--------------------------------------------------------------------')