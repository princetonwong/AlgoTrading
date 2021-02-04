from futu import *
from BacktraderAPI import BTStrategy
from CustomAPI.YahooScraper import YahooScraper
from BacktraderAPI.BTKernelRunWrapper import BTKernelRunWrapper
from CustomAPI.FutuAPI import FutuAPI

#Access
# SP500 = YahooScraper().readSP500List().head()["ticker"].tolist()
# HK_HSIConstituent_code = FutuAPI().getPlateStock("HK.HSI Constituent")["code"].values.tolist()

# INPUT HERE
INITIALCASH = 50000
SYMBOLS = ["AAPL"]
SUBTYPE = SubType.K_DAY
TIMERANGE = ("2020-10-01", "00:00:00", "2021-02-03", "00:39:00")
REMARKS = ""

## Change this for ONE strategy
sameStrategyParameters = [dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                               STRATEGYPARAMS=dict(kijun=6, tenkan=3, chikou=6, senkou=12,
                                                   senkou_lead=6, trailHold=1,stopLossPerc=0.016)
                               )]

## Change this for MANY strategies
differentStrategyParametersList = list()
for a in range(6, 8, 1):
    strategyParameters = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                              STRATEGYPARAMS=dict(kijun=a, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold=1,
                                                  stopLossPerc=0.016))
    differentStrategyParametersList.append({**strategyParameters})

sameDataParametersList = [dict(INITIALCASH=INITIALCASH,
                               SYMBOL=SYMBOLS[0],
                               SUBTYPE=SUBTYPE,
                               TIMERANGE=TIMERANGE,
                               REMARKS=REMARKS
                               )]
differentDataParametersList = list()
sameStrategyParametersList = list()
for symbol in SYMBOLS:
    differentDataParameters = dict(INITIALCASH=INITIALCASH,
                                   SYMBOL=symbol,
                                   SUBTYPE=SUBTYPE,
                                   TIMERANGE=TIMERANGE,
                                   REMARKS=REMARKS
                                   )

    differentDataParametersList.append({**differentDataParameters})
    sameStrategyParametersList.append({**sameStrategyParameters[0]})
#61.239.99.154

if __name__ == "__main__":
    BTKernelRunWrapper(sameDataParametersList, sameStrategyParameters)\
        .runOneTime(bokeh=False, iPython=False, quantStats=True)
    # BTKernelRunWrapper(sameDataParametersList, differentStrategyParametersList).runOptimizationWithSameData(sortKey="VWR")
    # BTKernelRunWrapper(differentDataParametersList, sameStrategyParameters).runOptimizationWithDifferentData(sortKey="VWR")
    # BTKernelRunWrapper(differentDataParametersList, sameStrategyParameters).runScreening()