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