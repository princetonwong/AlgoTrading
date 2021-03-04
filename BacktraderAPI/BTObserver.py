import backtrader as bt

class SLTPTracking(bt.Observer):

    lines = ('stop', 'take')

    plotinfo = dict(plot=True, subplot=False)

    plotlines = dict(stop=dict(ls='-', linewidth=1.5),
                     take=dict(ls=':', linewidth=1.5))

    def next(self):
        if self._owner.sl_price != 0.0:
            self.lines.stop[0] = self._owner.sl_price

        if self._owner.tp_price != 0.0:
            self.lines.take[0] = self._owner.tp_price

class BuySellStop(bt.observers.BuySell):
    lines = ('buy','sell','stop')

    plotlines = dict(
        buy=dict(marker='^', markersize=8.0,fillstyle="full"),
        sell=dict(marker='v', markersize=8.0,fillstyle="full"),
        stop=dict(marker='o', markersize=8.0,color='blue',
                  fillstyle='full',ls='')
    )

    def next(self):
        super(BuySellStop,self).next()
        owner = self._owner
        for o in owner._orderspending:
            order = o
            if order.exectype in [bt.Order.Stop,bt.Order.StopLimit,
                                  bt.Order.StopTrail,bt.Order.StopTrailLimit]:
                self.lines.stop[0] = order.created.price