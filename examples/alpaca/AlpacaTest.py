from pipeline_live.engine import LivePipelineEngine
from pipeline_live.data.sources.iex import list_symbols
from pipeline_live.data.alpaca.pricing import USEquityPricing
from pipeline_live.data.alpaca.factors import AverageDollarVolume
from zipline.pipeline import Pipeline
from pylivetrader.api import *

list = ["AAPL","AA"]
eng = LivePipelineEngine(list)
top5 = AverageDollarVolume(window_length=20).top(5)
pipe = Pipeline({
    'close': USEquityPricing.close.latest,
    # 'marketcap': PolygonCompany.marketcap.latest,
}, screen=(["AAPL"])

df = eng.run_pipeline(pipe)
df.to_csv("df.csv")