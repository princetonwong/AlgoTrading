from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
from BacktraderAPI import BTIndicator
from .MeanReversionStrategy import *
from .TrendFollowingStrategy import *
from .MACDStrategy import *
from .CCIStrategy import *
from .BTStrategyBase import *
from .BTStrategyExit import *

class ASOCrossStrategy(bt.Strategy):
    params = (
        ("period", 9),
        ('smoothing', 70.0),
        ('rsiFactor', 30.0),
    )

    def __init__(self):
        self.aso = BTIndicator.AbsoluteStrengthOscilator(period=self.p.period,
                                                         smoothing=self.p.smoothing,
                                                         rsifactor=self.p.rsiFactor)
        self.crossover = bt.ind.CrossOver(self.aso.bulls, self.aso.bears, subplot=False)

    def next(self):
        if self.position.size == 0:
            if self.crossover == 1:
                self.buy()
            elif self.crossover == -1:
                self.sell()
        elif self.position.size > 0:
            if self.crossover == -1:
                self.close()
        elif self.position.size < 0:
            if self.crossover == 1:
                self.close()

class ClenowTrendFollowingStrategy(bt.Strategy):
    """The trend following strategy from the book "Following the trend" by Andreas Clenow."""
    alias = ('ClenowTrendFollowing',)

    params = (
        ('trend_filter_fast_period', 50),
        ('trend_filter_slow_period', 100),
        ('fast_donchian_channel_period', 25),
        ('slow_donchian_channel_period', 50),
        ('trailing_stop_atr_period', 100),
        ('trailing_stop_atr_count', 3),
        ('risk_factor', 0.002)
    )

    def __init__(self):
        self.trend_filter_fast = bt.indicators.EMA(period=self.params.trend_filter_fast_period)
        self.trend_filter_slow = bt.indicators.EMA(period=self.params.trend_filter_slow_period)
        self.dc_fast = BTIndicator.DonchianChannels(period=self.params.fast_donchian_channel_period)
        self.dc_slow = BTIndicator.DonchianChannels(period=self.params.slow_donchian_channel_period)
        self.atr = bt.indicators.ATR(period=self.params.trailing_stop_atr_period)
        self.order = None  # the pending order
        # For trailing stop loss
        self.sl_order = None  # trailing stop order
        self.sl_price = None
        self.max_price = None  # track the highest price after opening long positions
        self.min_price = None  # track the lowest price after opening short positions

    def next(self):
        # self.dc_slow.dcl <= self.dc_fast.dcl <= self.dc_fast.dch <= self.dc_slow.dch
        assert self.dc_slow.dcl <= self.dc_fast.dcl
        assert self.dc_fast.dcl <= self.dc_fast.dch
        assert self.dc_fast.dch <= self.dc_slow.dch

        if not self.position:  # Entry rules
            assert self.position.size == 0

            # Position size rule
            max_loss = self.broker.get_cash() * self.p.risk_factor  # cash you afford to loss
            position_size = max_loss / self.atr[0]

            if self.data.close > self.dc_slow.dch:
                if self.trend_filter_fast > self.trend_filter_slow:  # trend filter
                    if self.order:
                        self.broker.cancel(self.order)
                    else:
                        # Entry rule 1
                        self.order = self.buy(price=self.data.close[0], size=position_size, exectype=bt.Order.Limit)
                        self.max_price = self.data.close[0]
            elif self.data.close < self.dc_slow.dcl:
                if self.trend_filter_fast < self.trend_filter_slow:  # trend filter
                    if self.order:
                        self.broker.cancel(self.order)
                    else:
                        # Entry rule 2
                        self.order = self.sell(price=self.data.close[0], size=position_size, exectype=bt.Order.Limit)
                        self.min_price = self.data.close[0]
        else:
            assert self.position.size
            # assert self.order is None

            # Exit rules
            if self.position.size > 0:
                # Exit rule 1
                if self.data.close < self.dc_fast.dcl:
                    self.order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.data.close[0])
                    return
            else:
                # Exit rule 2
                if self.data.close > self.dc_fast.dch:
                    self.order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.data.close[0])
                    return

            # Trailing stop loss
            trail_amount = self.atr[0] * self.p.trailing_stop_atr_count
            if self.position.size > 0:
                self.max_price = self.data.close[0] if self.max_price is None else max(self.max_price,
                                                                                       self.data.close[0])
                if self.sl_price is None or self.sl_price < self.max_price - trail_amount:
                    self.sl_price = self.max_price - trail_amount  # increase trailing price
                    if self.sl_order:
                        self.broker.cancel(self.sl_order)
                    else:
                        self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)
            elif self.position.size < 0:
                self.min_price = self.data.close[0] if self.min_price is None else min(self.min_price,
                                                                                       self.data.close[0])
                if self.sl_price is None or self.sl_price > self.min_price + trail_amount:
                    self.sl_price = self.min_price + trail_amount  # decrease trailing price
                    if self.sl_order:
                        self.broker.cancel(self.sl_order)
                    else:
                        self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)

class DMIStrategy(bt.Strategy):

    '''
         Entry Critria:
          - Long:
              - +DI > -DI
              - ADX > Benchmark
          - Short:
              - +DI < -DI
              - ADX > Benchmark

         Exit Critria
          - Long/Short: Same as opposite
    '''

    params = (("period", 14),
              ("adxBenchmark", 20),
              ("debug", False)
             )

    def __init__(self):
        self.dmi = bt.indicators.DirectionalMovementIndex(self.data, period=self.p.period)
        self.dicross = bt.indicators.CrossOver(self.dmi.plusDI, self.dmi.minusDI, subplot=True)

    def next(self):

        orders = self.broker.get_orders_open()

        if self.dmi.adx > self.p.adxBenchmark:

            if self.position.size == 0:  # not in the market

                if self.dicross == 1:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)
                if self.dicross == -1:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size > 0:  # longing in the market

                if self.dicross == -1:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size < 0:  # shorting in the market

                if self.dicross == 1:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)

            if self.p.debug:
                self.debug()

class ChandelierStrategy(bt.Strategy):
    params = dict(period=22, multip=3)

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.chandelier = BTIndicator.ChandelierExit(period= self.p.period, multip = self.p.multip, subplot=False)
        self.chandelier.csv = True

        self.crossUpLong = bt.ind.CrossUp(self.dataclose, self.chandelier.long, subplot=False)
        self.crossUpShort = bt.ind.CrossUp(self.dataclose, self.chandelier.short, subplot=False)
        self.crossDownLong = bt.ind.CrossDown(self.dataclose, self.chandelier.long, subplot=False)
        self.crossDownShort = bt.ind.CrossDown(self.dataclose, self.chandelier.short, subplot=False)

        self.longGreaterThanShort = self.chandelier.long > self.chandelier.short
        self.shortGreaterThanLong = self.chandelier.short > self.chandelier.long

        self.closeHighest = bt.ind.And(self.dataclose > self.chandelier.long, self.dataclose > self.chandelier.short, subplot=False)
        self.closeLowest = bt.ind.And(self.dataclose < self.chandelier.short, self.dataclose < self.chandelier.long, subplot=False)
        # self.closeBetweenLongAndShort = bt.ind.Or(self.longCloseShort, self.shortCloseLong, subplot=False)
        # self.closeBetweenLongAndShort = (self.chandelier.long > self.dataclose and self.dataclose > self.chandelier.short) or (self.chandelier.short > self.dataclose, self.dataclose > self.chandelier.long)

        self.crossUp = bt.ind.Or(self.crossUpLong, self.crossUpShort, subplot=False)
        self.crossDown = bt.ind.Or(self.crossDownLong, self.crossDownShort, subplot=False)


        self.upperBand = bt.ind.Max(self.chandelier.long, self.chandelier.short)
        self.lowerBand = bt.ind.Min(self.chandelier.long, self.chandelier.short)
        self.crossUpperBand = bt.ind.CrossOver(self.dataclose, self.upperBand, subplot=False)
        self.crossLowerBand = bt.ind.CrossOver(self.dataclose, self.lowerBand, subplot=False)

        self.cross = bt.ind.CrossOver(self.chandelier.long, self.chandelier.short, subplot=False)


    def next(self):
        #entry option 1
        # if self.position.size == 0:
        #     if self.closeBetweenLongAndShort == 0:
        #         if self.crossUp:
        #             self.buy()
        #         elif self.crossDown:
        #             self.sell()

        # entry option2
        if self.position.size == 0:
            if self.closeHighest:
                self.buy()
            elif self.closeLowest:
                self.sell()

        # entry option3
        # if self.position.size == 0:
        #     if self.crossUpperBand == 1:
        #         self.buy()
        #     elif self.crossLowerBand == -1:
        #         self.sell()

        #exit option1
        # elif self.position.size > 0:
        #     if self.closeBetweenLongAndShort == 1 or self.crossDown == 1:
        #             self.sell()
        # elif self.position.size < 0:
        #     if self.closeBetweenLongAndShort == 1 or self.crossUp == 1:
        #             self.buy()

        #exit option2
        # elif self.position.size != 0:
        #     if self.closeBetweenLongAndShort == 1:
        #         self.close()

        # exit option3
        elif self.position.size > 0:
            if self.crossUpperBand == -1:
                self.sell()
        elif self.position.size < 0:
            if self.crossLowerBand == 1:
                self.buy()

        # strategy:
        if self.position.size == 0:
            if self.cross == 1:
                self.buy()

        elif self.position.size != 0:
            if self.cross == -1:
                self.sell()

class CCICrossStrategyWithSLOWKDExitHeikinAshi(CCICrossStrategyWithStochasticExit):
    def __init__(self):
        super(CCICrossStrategyWithSLOWKDExitHeikinAshi, self).__init__()
        # self.heiKinAshi = bt.ind.HeikinAshi(subplot=False)
        self.stoch = BTIndicator.HeiKinAshiStochasticFull()
        self.stoch.csv = True
        self.kCrossupD = bt.ind.CrossUp(self.stoch.percK, self.stoch.percD, subplot=False)
        self.kCrossdownD = bt.ind.CrossDown(self.stoch.percK, self.stoch.percD, subplot=False)