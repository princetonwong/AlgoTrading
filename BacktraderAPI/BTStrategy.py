from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
from BacktraderAPI import BTIndicator
from .BTStrategyExit import *
from .BTStrategyBase import *
from .Strategy import CandleStrategy, CCIStrategy, MACDStrategy, MeanReversionStrategy, RSIStrategy, TrendFollowingStrategy, BTStrategy_Failed
import math


class EmptyStrategy(bt.Strategy):
    def __init__(self):
        super(EmptyStrategy, self).__init__()

class SICrossStrategy(ASIStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.siXZero == 1:
                self.buy()
            elif self.siXZero == -1:
                self.sell()
        elif self.position.size > 0:
            if self.siXZero == -1:
                self.sell()
        elif self.position.size < 0:
            if self.siXZero == 1:
                self.buy()

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

#Trend Changing, Stochastic Strategy
        
class StochasticStrategy(bt.Strategy):

    '''
    https://tradingstrategyguides.com/best-stochastic-trading-strategy/

    Entry Criteria:

    1. Check the daily chart and make sure the Stochastic indicator < 20 and the %K line crossed above %D line.
    2. Move Down to the 15-Minute Time Frame and Wait for the Stochastic Indicator to hit the 20 level. %K line crossed above %D line.
    3. Wait for the Stochastic %K line (blue moving average) to cross above the 20 level
    4. Wait for a Swing Low Pattern to develop on the 15-Minute Chart
    5. Entry Long When the Highest Point of the Swing Low Pattern is Broken to the Upside
    6. Use Protective Stop Loss placed below the most recent 15-minute Swing Low
    7. Take Profit at 2xSL

             - Long:
                 -
             - Short:
                 -


            Exit Criteria
             - Long/Short: Same as opposite
    '''

    params = (
        ('period', 14),
        ('period_dfast', 3),
        ('period_dslow', 3),
        ('upperband', 80.0),
        ('lowerband', 20.0),
    )

    def __init__(self):
        self.stochastic = bt.indicators.Stochastic(self.data,
                                                   period=self.p.period,
                                                   period_dfast=self.p.period_dfast,
                                                   period_dslow=self.p.period_dslow,
                                                   safediv=True
                                                   )
        self.kCrosslower = bt.indicators.CrossOver(self.stochastic.l.percK,self.p.lowerband)
        self.kCrossupper = bt.indicators.CrossOver(self.stochastic.l.percK,self.p.upperband)
        self.kCrossD = bt.indicators.CrossOver(self.stochastic.l.percK,self.stochastic.l.percD)

    def next(self):
        if self.position.size == 0:
            if self.kCrosslower == 1 and self.kCrossD == 1:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)
            if self.kCrossupper == -1 and self.kCrossD == -1:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:
            if self.kCrossupper == -1 and self.kCrossD == -1:
                self.close(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:
            if self.kCrosslower == 1 and self.kCrossD == 1:
                self.close(exectype=bt.Order.Stop, price=self.data.close)

class ASOCrossStrategy(ASOStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.ashXLower == 1:
                self.buy()
            elif self.ashXUpper == -1:
                self.sell()
        elif self.position.size > 0:
            if self.ashXUpper == -1:
                self.sell()
        elif self.position.size < 0:
            if self.ashXLower == 1:
                self.buy()


#Channel Strategy

class KeltnerChannelStrategy(KeltnerChannelStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.cxKChanTop == 1:
                self.order = self.buy()

            elif self.cxKChanBot == -1:
                self.order = self.sell()


        elif self.position.size > 0:
            if self.cxKChanTop == -1:
                self.sell()

        elif self.position.size < 0:
            if self.cxKChanBot == 1:
                self.buy()

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


#Strength of Trend Strategy

class AroonCrossStrategy(AroonStrategyBase,EMAStrategyBase):

    '''
        - Long:
        - close is above 200 EMA
        - Aroon Long touches upper & Short touches lower

        - Short:
        - close is below 200 EMA
        - Aroon Short touches upper & Long touches lower

        - Exit Criteria:
        - Long: Close Buy when Aroon Long crosses below Aroon Short below 50
        - Short: Close Sell when Aroon Short crosses below Aroon Long below 50
    '''

    def next(self):
        orders = self.broker.get_orders_open()

        if self.position.size == 0:  # not in the market
            if self.data.close > self.ema:
                if self.aroonCross == 1 and self.aroon.aroondown < self.aroonMidBand:
                # if self.aroon.aroonup == self.p.aroonUpBand and self.aroon.aroondown == self.p.aroonLowBand:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)
            if self.data.close < self.ema:
                if self.aroonCross == -1 and self.aroon.aroonup < self.aroonMidBand:
                # if self.aroon.aroondown == self.p.aroonUpBand and self.aroon.aroonup == self.p.aroonLowBand:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:  # longing in the market
            if self.aroonCross == -1 and self.aroon.aroonup < self.aroonMidBand:
                self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:  # shorting in the market
            if self.aroonCross == 1 and self.aroon.aroondown < self.aroonMidBand:
                self.buy(exectype=bt.Order.Stop, price=self.data.close)

class DMICrossStrategy(DMIStrategyBase):

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

    def next(self):

        orders = self.broker.get_orders_open()

        if self.dmi.adx > self.p.adxBenchmark:

            if self.position.size == 0:  # not in the market

                if self.plusDIXminusDI == 1:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)
                if self.plusDIXminusDI == -1:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size > 0:  # longing in the market

                if self.plusDIXminusDI == -1:
                    self.sell(exectype=bt.Order.Stop, price=self.data.close)

            elif self.position.size < 0:  # shorting in the market

                if self.plusDIXminusDI == 1:
                    self.buy(exectype=bt.Order.Stop, price=self.data.close)

class IchimokuCloudxDMIStrategy(IchimokuCloudStrategyBase, DMIStrategyBase):
    '''
             Kijun Sen (blue line, confirm future trends): standard line/base line, averaging highest high and lowest low for past 26 periods
             Tenkan Sen (red line, confirm trending/ranging): turning line, averaging highest high and lowest low for past 9 periods
             Chikou Span (green line, confirm future trends): lagging line, today’s closing price plotted 26 periods behind
             Senkou Span (red/green band, support and resistance levels):
             - first Senkou line (fast): averaging Tenkan Sen and Kijun Sen, plotted 26 periods ahead
             - second Senkou line (slow): averaging highest high and lowest low over past 52 periods, plotted 26 periods ahead

             Entry Criteria:

              - Long:
                  - The price above the green cloud (price > 1st Senkou line > 2nd Senkou line) (Trend)
                  - Tenkan Sen crosses above Kijun Sen (momentum)
                  - Price crosses above Kijun Sen (momentum)
                  optional: Chikou Span crossing above the price
              - Short:
                  - The price below the red cloud (price < 1st Senkou line < 2nd Senkou line) (Trend)
                  - Tenkan Sen crosses below Kijun Sen (momentum)
                  - Price crosses below Kijun Sen (momentum)
                  Optional: Chikou Span crossing down the price


             Exit Criteria
              - Long/Short: Same as opposite

     Failed: DMIcx

     '''

    def next(self):

        orders = self.broker.get_orders_open()

        if self.position.size == 0:  # not in the market

            if self.data.close > self.ichimoku.l.senkou_span_a > self.ichimoku.l.senkou_span_b:
                if self.tKCross == 1 and self.priceKCross == 1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.buy(exectype=bt.Order.Stop, price=self.data.close)

            if self.data.close < self.ichimoku.l.senkou_span_a < self.ichimoku.l.senkou_span_b:
                if self.tKCross == -1 and self.priceKCross == -1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:  # longing in the market

            if self.data.close < self.ichimoku.l.senkou_span_a < self.ichimoku.l.senkou_span_b:
                if self.tKCross == -1 and self.priceKCross == -1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.close(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:  # shorting in the market

            if self.data.close > self.ichimoku.l.senkou_span_a > self.ichimoku.l.senkou_span_b:
                if self.tKCross == 1 and self.priceKCross == 1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.close(exectype=bt.Order.Stop, price=self.data.close)

class TTFStrategy(TTFStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.ttfCxUpper == -1:
                self.sell()
            elif self.ttfCxLower == 1:
                self.buy()
        elif self.position.size > 0:
            if self.ttfCxUpper == 1:
                self.sell()
        elif self.position.size < 0:
            if self.ttfCxLower == -1:
                self.buy()

class StochasticTTFStrategy(StochasticTTFStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.kCxd == -1:
                self.buy()

            elif self.kCxd == 1:
                self.sell()

        elif self.position.size > 0:
            if self.stochTTF.k <= -100:
                self.sell()

        elif self.position.size < 0:
            if self.stochTTF.k >= 100:
                self.buy()

class TTFwithStopTrail(TTFStrategyBase):
    params = dict(stoptype=bt.Order.StopTrail, trailamount=0.0,trailpercent=0.0)

    def __init__(self):
        super(TTFwithStopTrail, self).__init__()
        self.order = None

    def next(self):
        if self.position.size > 0:
            if self.ttfCxUpper == 1:
                self.sell()
        elif self.position.size < 0:
            if self.ttfCxLower == -1:
                self.buy()
        elif self.position.size == 0:
            if self.ttfCxUpper == -1:
                # self.sell_bracket(stopprice= self.p.trailamount)
                self.sell()
            elif self.ttfCxLower == 1:
                # self.buy_bracket(stopprice=self.data.close[0] - self.p.trailamount)
                self.buy()


        if self.order is None:
            if self.position.size > 0:
                self.order = self.sell(exectype=self.p.stoptype,
                                       trailamount=self.p.trailamount,
                                       trailpercent=self.p.trailpercent)
            elif self.position.size < 0:
                self.order = self.buy(exectype=self.p.stoptype,
                                       trailamount=self.p.trailamount,
                                       trailpercent=self.p.trailpercent)


            if self.p.trailamount != 0:
                tcheck = self.data.close - self.p.trailamount
            else:
                tcheck = self.data.close * (1.0 - self.p.trailpercent)
            # print(','.join(
            #     map(str, [self.datetime.date(), self.data.close[0],
            #               self.order.created.price, tcheck])
            #     )
            # )
        else:
            if self.p.trailamount != 0:
                tcheck = self.data.close - self.p.trailamount
            else:
                tcheck = self.data.close * (1.0 - self.p.trailpercent)
            # print(','.join(
            #     map(str, [self.datetime.date(), self.data.close[0],
            #               self.order.created.price, tcheck])
            #     )
            # )

class TTFHOLD(TTFStrategyBase, HoldStrategyExit):
    params = (('risk', 0.1),  # risk 10%
              ('stop_dist', 200))  # stoploss distance 5%

    def __init__(self):
        super(EmptyStrategy, self).__init__()

    def next(self):
        cash = self.broker.get_cash()
        stop_price = (self.data.close[0] - self.p.stop_dist)
        if self.position.size > 0:
            if self.ttfCxUpper == 1:
                if (len(self) - self.holdstart) >= self.p.hold:
                    self.order = self.sell()
        elif self.position.size < 0:
            if self.ttfCxLower == -1:
                if (len(self) - self.holdstart) >= self.p.hold:
                    self.order = self.buy()
        elif self.position.size == 0:
            if self.ttfCxUpper == -1:
                # self.sell_bracket(stopprice= self.p.trailamount)
                self.order = self.sell()
                self.order = self.buy(exectype=bt.Order.Stop, price=stop_price)
            elif self.ttfCxLower == 1:
                # self.buy_bracket(stopprice=self.data.close[0] - self.p.trailamount)
                self.order = self.buy()
                self.order = self.sell(exectype=bt.Order.Stop, price=stop_price)

                # qty = math.floor((cash * self.p.risk) / (self.data.close[0] - stop_price))