from pylivetrader.api import order_target
import pandas as pd
from pipeline_live.data.alpaca.factors import AverageDollarVolume
from pipeline_live.data.alpaca.pricing import USEquityPricing
from zipline.pipeline import Pipeline
from logbook import Logger

log = Logger('pipeline-example-logger')
BUY_AMOUNT = 10


def initialize(context):
    top5 = AverageDollarVolume(window_length=20).top(5)
    context.pipe = Pipeline({
        'close':     USEquityPricing.close.latest}, screen=top5)
    context.attach_pipeline(context.pipe, "pipe")


def before_trading_start(context, data):
    context.output = context.pipeline_output('pipe')
    print(context.output)


def handle_data(context, data):
    short_periods = 12
    long_periods = 26

    for asset in context.portfolio.positions:
        short_data = data.history(
            asset, 'price', bar_count=short_periods, frequency="1m")
        short_ema = pd.Series.ewm(short_data, span=short_periods).mean().iloc[-1]
        long_data = data.history(
            asset, 'price', bar_count=long_periods, frequency="1m")
        long_ema = pd.Series.ewm(long_data, span=long_periods).mean().iloc[-1]

        macd = short_ema - long_ema

        if macd < 0:
            order_id = order_target(asset, 0)
            if order_id:
                log.info("Closed position for {}".format(asset.symbol))
    # step 2
    for asset in context.output.index:
        short_data = data.history(
            asset, 'price', bar_count=short_periods, frequency="1m")
        short_ema = pd.Series.ewm(short_data, span=short_periods).mean().iloc[-1]
        # Calculate long-term EMA (using data from the past 26 minutes.)
        long_data = data.history(
              asset, 'price', bar_count=long_periods, frequency="1m")
        long_ema = pd.Series.ewm(long_data, span=long_periods).mean().iloc[-1]

        macd = short_ema - long_ema

        # Trading logic
        if macd > 0:
            # order_target allocates a specified target shares
            # to a long position in a given asset.
            order_id = order_target(asset, -BUY_AMOUNT)
            if order_id:
                log.info("Bought {} shares of {}".format(BUY_AMOUNT,asset.symbol))
                # log.info("Closed position for {}".format(asset.symbol))

