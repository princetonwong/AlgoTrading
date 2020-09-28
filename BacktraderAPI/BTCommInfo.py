import backtrader as bt

class FixedCommisionScheme(bt.CommInfoBase):
    '''
    This is a simple fixed commission scheme
    '''
    params = (
        ('commission', 5),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission

class FutuHKIMainCommInfo(bt.CommInfoBase):
    params = dict(commission=10.6, margin=25000, mult=10.0)