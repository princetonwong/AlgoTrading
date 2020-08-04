from pipeline_live.data.alpaca.factors import AverageDollarVolume
from pipeline_live.data.alpaca.pricing import USEquityPricing
from zipline.pipeline import Pipeline
from logbook import Logger
from futu import *

log = Logger('pipeline-example-logger')
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

# Parameters
BUY_AMOUNT = 1
short_periods = 5
long_periods = 35
PRICE = 4000

def initialize(context):
    top10 = AverageDollarVolume(window_length=20).top(10)
    context.pipe = Pipeline({
        'close': USEquityPricing.close.latest,
        'open' : USEquityPricing.open.latest,
        'high' : USEquityPricing.high.latest,
        'low' : USEquityPricing.low.latest,
        'volume' : USEquityPricing.volume.latest
        },screen = top10)
    context.attach_pipeline(context.pipe, "pipe")

def before_trading_start(context, data):
    context.output = context.pipeline_output('pipe')

    filename = 'output' + datetime.now().strftime("%H-%M-%S") + ".csv"
    context.output.to_csv(filename)
    print(context.output)

# def handle_data(context, data):

    # for asset in context.portfolio.positions:
    #     macd = MACD(asset, data)
    #
    #     if macd < -0.1:
    #         order_id = futuAPI.placeUSOrder(price= 0, quantity= BUY_AMOUNT, code= "US." + asset.symbol,
    #                                 tradeSide= TrdSide.SELL, orderType= OrderType.NORMAL)
    #         if order_id[0] != -1:
    #             log.info("MACD: " + str(macd))
    #             log.info(order_id[1])
    #             log.info("Closed position for {}".format(asset.symbol))
    #
    # for asset in context.output.index:
    #     macd = MACD(asset, data)
    #
    #     if macd > 0.1:
    #         order_id = futuAPI.placeUSOrder(price= PRICE, quantity=BUY_AMOUNT, code="US." + asset.symbol,
    #                                 tradeSide=TrdSide.BUY, orderType=OrderType.NORMAL)
    #         if order_id[0] != -1:
    #             log.info("MACD: " + str(macd))
    #             log.info(order_id[1])
    #             log.info("Bought {} shares of {}".format(BUY_AMOUNT, asset.symbol))