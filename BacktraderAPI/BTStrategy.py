from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
from BacktraderAPI import BTIndicator
from .BTStrategyExit import *
from .BTStrategyBase import *
from .BTStrategyBuyType import *
from .BTStrategyDebug import *
from .Strategy import *
import math
import datetime

class EmptyStrategy(bt.Strategy):
    params = dict(period=2000)

    def __init__(self):
        bt.indicators.HurstExponent(period=self.p.period)
    pass

class KDJStrategy(StopTrailStrategyExit, KDJStrategyBase):
    def next(self):
        super(KDJStrategy, self).next()
        if self.position.size == 0:
            if self.kdj.percJ >= 150:
                self.buy()
            elif self.kdj.percJ <= -50:
                self.sell()
        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= 6:
                if self.kdj.percJ >= 100:
                    self.close()
        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= 6:
                if self.kdj.percJ <= -100:
                    self.close()


class ModifiedRSIStrategy(StopTrailStrategyExit):
    def __init__(self):
        super(ModifiedRSIStrategy, self).__init__()
        self.rsi = BTIndicator.modifiedRSI()
        self.rsiXUpper = bt.ind.CrossOver(self.rsi.modifiedRSI, 90)
        self.rsiXLower = bt.ind.CrossOver(self.rsi.modifiedRSI, 10)
        self.rsiX30 = bt.ind.CrossOver(self.rsi.modifiedRSI, 30)

    def next(self):
        super(ModifiedRSIStrategy, self).next()
        if self.position.size == 0:
            if self.rsiXLower == 1:
                self.buy()
            elif self.rsiXUpper == -1:
                self.sell()
        elif self.position.size > 0:
            if self.rsiXUpper == 1:
                self.close()
        elif self.position.size < 0:
            if self.rsiX30 == -1:
                self.close()

class AOStrategy(AwesomeOscillatorStrategyBase, StopTrailStrategyExit):
    def next(self):
        super(AOStrategy, self).next()
        if self.position.size == 0:
            if self.aoStreakXZero == 1:
                self.sell()
            elif self.aoStreakXZero == -1:
                self.buy()
        elif self.position.size > 0:
            if self.aoStreak.streak == -2:
                self.close()
        elif self.position.size < 0:
            if self.aoStreak.streak == 2:
                self.close()

class CzechStrategy(BBandsStrategyBase, VLIStrategyBase, StopTrailStrategyExit):
    def __init__(self):
        super(CzechStrategy, self).__init__()
        self.BBWcondition = bt.ind.SMA(self.bollWidth, period=10) > bt.ind.SMA(self.bollWidth, period=50)
        self.VOLcondition = bt.ind.SMA(self.data.volume, period=10) > bt.ind.SMA(self.data.volume, period=50)
        self.XOverBollTop = bt.ind.CrossOver(self.data, self.boll.top)
        self.XOverBollBot = bt.ind.CrossOver(self.data, self.boll.bot, plot=False)
        self.smaVeryFast = bt.ind.SMA(self.data, period=10)
        self.smaFast = bt.ind.SMA(self.data, period=20)
        self.smaMid = bt.ind.SMA(self.data, period=50)
        self.smaSlow = bt.ind.SMA(self.data, period=100)
        self.smaVerySlow = bt.ind.SMA(self.data, period=200)
        self.smaCrossDown = bt.ind.CrossDown(self.smaSlow, self.smaMid)
        self.waitingToShort = False

    def next(self):
        if self.position.size == 0:

            if self.XOverBollTop == -1 and self.VOLcondition:
                if self.data > self.smaFast:
                    if not self.extremeVolatiliy:
                        if not self.volatilityLevel:
                            if self.smaMid > self.smaVerySlow:
                                    self.buy()
                        elif not self.smaVerySlow > self.smaSlow > self.smaMid:
                            self.buy()
                    elif self.smaSlow > self.smaVerySlow:
                        self.buy()
                        #TODO: stop loss at low of last candle
                        #TODO: if trade profit > 3%, add stop win at 1%
            elif self.XOverBollBot == 1:
                if self.bollWidth < self.vli.slow:
                    self.waitingToShort = True

            # if self.waitingToShort:
            #     if self.smaCrossDown:  # wait for
            #         if self.bollWidth < self.vli.top:
            #             self.sell()
            #             self.waitingToShort = False

        elif self.position.size > 0:
            if self.XOverBollBot == -1 and self.VOLcondition:
                self.close()
        elif self.position.size < 0:
            if self.XOverBollTop == 1 and self.VOLcondition:
                self.close()

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

class KAMAXStrategy(KAMAStrategyBase, BBandsKChanSqueezeStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.squeeze.squeezePerc > self.p.squeezeThreshold:
                if self.kamaXsma == 1:
                    self.buy()
                # elif self.siXZero == -1:
                #     self.sell()
        elif self.position.size > 0:
            if self.kamaXsma == -1:
                self.sell()
        # elif self.position.size < 0:
            # if self.kamaXsma == 1:
            #     self.buy()

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

class ASOCrossStrategyWithSqueezePercCCI (ASOStrategyBase, BBandsKChanSqueezeStrategyBase, StochasticCCIStrategyBase, SMAStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.squeeze.squeezePerc > self.p.squeezeThreshold:
                if self.ashXLower == 1 :
                    self.buy()
                elif self.ashXUpper == -1 :
                    self.sell()
        elif self.position.size > 0:
            if self.ashXUpper == -1 :
                self.sell()
        elif self.position.size < 0 :
            if self.ashXLower == 1 :
                self.buy()

class CMOCrossStrategyWithSqueezePercCCI (StochasticCCIStrategyBase, BBandsKChanSqueezeStrategyBase):
    def next(self):
        if self.position.size == 0:
            if self.squeeze.squeezePerc > self.p.squeezeThreshold:
                if self.stochcciXUpperband == 1:
                    self.buy()
                elif self.stochcciXLowerband == -1:
                    self.sell()
        elif self.position.size > 0:
            if self.stochcciXUpperband == -1:
                self.sell()
        elif self.position.size < 0 :
            if self.stochcciXLowerband == 1:
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

class IchimokuStrategy(IchimokuCloudStrategyBase, StopTrailStrategyExit, HoldStrategyExit, AwesomeOscillatorStrategyBase, PSARStrategyBase):
    def next(self):
        cloud = self.ichimoku.senkou_span_a - self.ichimoku.senkou_span_b
        tenkanGreaterKijun = self.ichimoku.tenkan_sen - self.ichimoku.kijun_sen
        if self.position.size == 0:  # not in the market

            if tenkanGreaterKijun > 0:
               if (cloud > 0 and self.data > self.ichimoku.senkou_span_a) or (cloud < 0 and self.data > self.ichimoku.senkou_span_b):
                    if self.tenkanXKijun == 1 or self.XSenkouB == 1:
                        self.buy()

            elif tenkanGreaterKijun < 0:
                if (cloud > 0 and self.data < self.ichimoku.senkou_span_b) or (cloud < 0 and self.data < self.ichimoku.senkou_span_a):
                    if self.tenkanXKijun == -1 or self.XSenkouB == -1:
                        self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.tenkanXKijun == -1:
                    self.close()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.tenkanXKijun == 1:
                    self.close()

        super(IchimokuStrategy, self).next()

class IchimokuBracketStrategy(IchimokuCloudStrategyBase, BracketBuying, HoldStrategyExit, CCIStrategyBase, AwesomeOscillatorStrategyBase):
    def next(self):
        cloud = self.ichimoku.senkou_span_a - self.ichimoku.senkou_span_b
        tenkanGreaterKijun = self.ichimoku.tenkan_sen - self.ichimoku.kijun_sen
        if self.position.size == 0:  # not in the market

            if tenkanGreaterKijun > 0:
               if (cloud > 0 and self.data > self.ichimoku.senkou_span_a) or (cloud < 0 and self.data > self.ichimoku.senkou_span_b):
                    if self.tenkanXKijun == 1 or self.XSenkouB == 1:
                        self.buy()

            elif tenkanGreaterKijun < 0:
                if (cloud > 0 and self.data < self.ichimoku.senkou_span_b) or (cloud < 0 and self.data < self.ichimoku.senkou_span_a):
                    if self.tenkanXKijun == -1 or self.XSenkouB == -1:
                        self.sell()

        elif self.position.size > 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.tenkanXKijun == -1:
                    self.close()

        elif self.position.size < 0:
            if (len(self) - self.holdstart) >= self.p.hold:
                if self.tenkanXKijun == 1:
                    self.close()

        super(IchimokuBracketStrategy, self).next()

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
        if self.position.size == 0:  # not in the market

            if self.data.close > self.ichimoku.l.senkou_span_a > self.ichimoku.l.senkou_span_b:
                if self.tenkanXKijun == 1 and self.XKijun == 1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.buy(exectype=bt.Order.Stop, price=self.data.close)

            if self.data.close < self.ichimoku.l.senkou_span_a < self.ichimoku.l.senkou_span_b:
                if self.tenkanXKijun == -1 and self.XKijun == -1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.sell(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size > 0:  # longing in the market

            if self.data.close < self.ichimoku.l.senkou_span_a < self.ichimoku.l.senkou_span_b:
                if self.tenkanXKijun == -1 and self.XKijun == -1:
                    if self.dmi.adx > self.p.adxBenchmark:
                        self.close(exectype=bt.Order.Stop, price=self.data.close)

        elif self.position.size < 0:  # shorting in the market

            if self.data.close > self.ichimoku.l.senkou_span_a > self.ichimoku.l.senkou_span_b:
                if self.tenkanXKijun == 1 and self.XKijun == 1:
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

class TTFwithStopTrail2(TTFStrategyBase):
    params = dict(size=0,stoptype=bt.Order.StopTrail, trailamount=0.0,trailpercent=0.0)

    def __init__(self):
        super(TTFwithStopTrail2, self).__init__()
        self.order = None

    def next(self):
        if self.position.size == 0:
            if self.ttfCxUpper == -1:
                self.sell()
                self.order = None
            elif self.ttfCxLower == 1:
                self.buy()
                self.order = None
        elif self.position.size > 0:
            # assert self.order is None
            if self.ttfCxUpper == 1:
                self.close()
        elif self.position.size < 0:
            # assert self.order is None
            if self.ttfCxLower == -1:
                self.close()

        if self.order is None:
            if self.position.size > 0:
                self.order = self.close(size=1, exectype=self.p.stoptype,
                                       trailamount=self.p.trailamount)
                                       # trailpercent=self.p.trailpercent)
            if self.position.size < 0:
                self.order = self.buy(size=1, exectype=self.p.stoptype,
                                       trailamount=self.p.trailamount)
                                       # trailpercent=self.p.trailpercent)


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

class TTFwithStopTrail(TTFStrategyBase, StopTrailStrategyExit):
    params = dict()

    def next(self):
        super(TTFwithStopTrail, self).next()
        if self.position.size == 0:
            if self.ttfCxUpper == -1:
                self.sell()
                self.order = None
            elif self.ttfCxLower == 1:
                self.buy()
                self.order = None

        elif self.position.size > 0:
            if self.ttfCxUpper == 1:
                self.sell()

        elif self.position.size < 0:
            if self.ttfCxLower == -1:
                self.buy()


        # if self.order is None:
        #     if self.position.size > 0:
        #         self.order = self.sell(exectype=self.p.stoptype,
        #                                trailamount=self.p.trailamount,
        #                                trailpercent=self.p.trailpercent)
        #     elif self.position.size < 0:
        #         self.order = self.buy(exectype=self.p.stoptype,
        #                                trailamount=self.p.trailamount,
        #                                trailpercent=self.p.trailpercent)
        #
        #
        #     if self.p.trailamount != 0:
        #         tcheck = self.data.close - self.p.trailamount
        #     else:
        #         tcheck = self.data.close * (1.0 - self.p.trailpercent)
        #     # print(','.join(
        #     #     map(str, [self.datetime.date(), self.data.close[0],
        #     #               self.order.created.price, tcheck])
        #     #     )
        #     # )
        # else:
        #     if self.p.trailamount != 0:
        #         tcheck = self.data.close - self.p.trailamount
        #     else:
        #         tcheck = self.data.close * (1.0 - self.p.trailpercent)
        #     # print(','.join(
        #     #     map(str, [self.datetime.date(), self.data.close[0],
        #     #               self.order.created.price, tcheck])
        #     #     )
        #     # )

class MyStrategy(TTFStrategyBase):

    def __init__(self):
        super(MyStrategy, self).__init__()
        # init stop loss and take profit order variables
        self.sl_order, self.tp_order = None, None

    def notify_trade(self, trade):
        if trade.isclosed:
            # clear stop loss and take profit order variables for no position state
            if self.sl_order:
                self.broker.cancel(self.sl_order)
                self.sl_order = None

            if self.tp_order:
                self.broker.cancel(self.tp_order)
                self.tp_order = None

    def next(self):

        if self.position.size == 0:
            if self.ttfCxUpper == -1:
                self.sell()

        # process stop loss and take profit signals
        if self.position:

            # set stop loss and take profit prices
            # in case of trailing stops stop loss prices can be assigned based on current indicator value
            price_sl_long = self.position.price * 0.98
            price_sl_short = self.position.price * 1.02
            price_tp_long = self.position.price * 1.06
            price_tp_short = self.position.price * 0.94

            # cancel existing stop loss and take profit orders
            if self.sl_order:
                self.broker.cancel(self.sl_order)

            if self.tp_order:
                self.broker.cancel(self.tp_order)

            # check & update stop loss order
            sl_price = 0.0
            if self.position.size > 0 and price_sl_long != 0: sl_price = price_sl_long
            if self.position.size < 0 and price_sl_short != 0: sl_price = price_sl_short

            if sl_price != 0.0:
                self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=sl_price)

            # check & update take profit order
            tp_price = 0.0
            if self.position.size > 0 and price_tp_long != 0: tp_price = price_tp_long
            if self.position.size < 0 and price_tp_short != 0: tp_price = price_tp_short

            if tp_price != 0.0:
                self.tp_order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=tp_price)

class TTFwithBracket(TTFStrategyBase):

    params = dict(
                  limit=0.005,
                  limdays=3,
                  limdays2=1000,
                  limdays3=1000,
                  hold=10,
                  trailpercent=0.02,
                  usebracket=False,  # use order_target_size
                  switchp1p2=False,  # switch prices of order1 and order2
                )

    def notify_order(self, order):
        print('{}: Order ref: {} / Type {} / Status {}'.format(
            self.data.datetime.date(0),
            order.ref, 'Buy' * order.isbuy() or 'Sell' * order.issell(),
            order.getstatusname()))

        if order.status == order.Completed:
            self.holdstart = len(self)

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)

    def __init__(self):
        super(TTFwithBracket, self).__init__()
        self.orefs = list()
        self.holdstart = int()
        if self.p.usebracket:
            print('-' * 5, 'Using buy_bracket')

    def next(self):

        if self.orefs:
            return

        elif self.position.size == 0:

            if self.ttfCxLower == 1:
                close = self.data.close[0]
                p1 = close * (1.0 - self.p.limit)
                p2 = p1 - 0.02 * close
                p3 = p1 + 0.02 * close

                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = datetime.timedelta(self.p.limdays2)
                valid3 = datetime.timedelta(self.p.limdays3)

                if self.p.switchp1p2:
                    p1, p2 = p2, p1
                    valid1, valid2 = valid2, valid1

                if not self.p.usebracket:
                    o1 = self.buy(exectype=bt.Order.Limit,
                                  price=p1,
                                  valid=valid1,
                                  transmit=False)

                    print('{}: Oref {} / Buy at {}'.format(
                        self.datetime.date(), o1.ref, p1))

                    o2 = self.sell(exectype=bt.Order.StopTrail,
                                   trailpercent=0.05,
                                   valid=valid2,
                                   parent=o1,
                                   transmit=False)

                    print('{}: Oref {} / Sell StopTrail at {}'.format(
                        self.datetime.date(), o2.ref, p2))

                    o3 = self.sell(exectype=bt.Order.Limit,
                                   price=p3,
                                   valid=valid3,
                                   parent=o1,
                                   transmit=True)

                    print('{}: Oref {} / Sell Limit at {}'.format(
                        self.datetime.date(), o3.ref, p3))

                    self.orefs = [o1.ref, o2.ref, o3.ref]

                else:
                    os = self.buy_bracket(
                        price=p1, valid=valid1,
                        stopprice=p2, stopargs=dict(valid=valid2),
                        limitprice=p3, limitargs=dict(valid=valid3), )

                    self.orefs = [o.ref for o in os]

            elif self.ttfCxUpper == -1:

                close = self.data.close[0]
                p1 = close * (1.0 - self.p.limit)
                p2 = p1 + 0.02 * close
                p3 = p1 - 0.02 * close

                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = datetime.timedelta(self.p.limdays2)
                valid3 = datetime.timedelta(self.p.limdays3)

                if self.p.switchp1p2:
                    p1, p2 = p2, p1
                    valid1, valid2 = valid2, valid1

                if not self.p.usebracket:
                    o1 = self.sell(exectype=bt.Order.Limit,
                                  price=p1,
                                  valid=valid1,
                                  transmit=False)

                    print('{}: Oref {} / Sell at {}'.format(
                        self.datetime.date(), o1.ref, p1))

                    o2 = self.buy(exectype=bt.Order.StopTrail,
                                  trailpercent=0.05,
                                  valid=valid2,
                                  parent=o1,
                                  transmit=False)

                    print('{}: Oref {} / Buy StopTrail at {}'.format(
                        self.datetime.date(), o2.ref, p2))

                    o3 = self.buy(exectype=bt.Order.Limit,
                                   price=p3,
                                   valid=valid3,
                                   parent=o1,
                                   transmit=True)

                    print('{}: Oref {} / Buy Limit at {}'.format(
                        self.datetime.date(), o3.ref, p3))

                    self.orefs = [o1.ref, o2.ref, o3.ref]

                else:
                    os = self.sell_bracket(
                        price=p1, valid=valid1,
                        stopprice=p2, stopargs=dict(valid=valid2),
                        limitprice=p3, limitargs=dict(valid=valid3), )

                    self.orefs = [o.ref for o in os]

        else:  # in the market
            if (len(self) - self.holdstart) >= self.p.hold:
                pass  # do nothing in this case #TODO: Multiple data feeds#TODO: Multiple data feeds

        # elif datetime.time(2,45) < self.data.datetime.time() < datetime.time(9,0):
        #     self.close(size=self.p.size)

class TTFwithBracketandCancellation(TTFStrategyBase, BracketBuying, NotifyOrderShowStatus):

    params = dict(usebracket=False,  # use order_target_size
                  switchp1p2=False,  # switch prices of order1 and order2
    )

    def next(self):

        if self.position.size == 0:

            if self.ttfCxLower == 1:
                self.buyWithBracket()

            elif self.ttfCxUpper == -1:
                self.sellWithBracket()

        elif self.position.size < 1:

            if self.ttfCxLower == 1:
                self.closeSellBracket()

        elif self.position.size > 1:

            if self.ttfCxUpper == -1:
                self.closeBuyBracket()

#TODO: the market order cant be executed when counteracted cross indicator triggered

class TTFHOLD(TTFStrategyBase, HoldStrategyExit):
    params = (('risk', 0.1),  # risk 10%
              ('stop_dist', 200),
              ("trailamount", 100))  # stoploss distance 5%

    def __init__(self):
        super(TTFHOLD, self).__init__()

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
                self.sell_bracket(stopprice= self.p.trailamount)
                self.order = self.sell()
                self.order = self.buy(exectype=bt.Order.Stop, price=stop_price)
            elif self.ttfCxLower == 1:
                # self.buy_bracket(stopprice=self.data.close[0] - self.p.trailamount)
                self.order = self.buy()
                self.order = self.sell(exectype=bt.Order.Stop, price=stop_price)

                # qty = math.floor((cash * self.p.risk) / (self.data.close[0] - stop_price))

class HeikinAshiStrategy(bt.Strategy):
    def __init__(self):
        self.newdata = self.data1
        self.hkarsi = BTIndicator.talibCCI(self.data1.close)
        self.up = self.data1.close > self.data1.open

    def next(self):
        if self.position.size == 0:
            if self.up:
                self.buy()
            elif not self.up:
                self.sell()
        elif self.position.size > 0:
            if not self.up:
                self.sell()
        elif self.position.size < 0:
            if self.up:
                self.buy()

class PSARStrategy(IchimokuStrategy, PSARStrategyBase, KDJStrategyBase):
    pass