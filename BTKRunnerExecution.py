from futu import *
from BacktraderAPI import BTStrategy
from CustomAPI.YahooScraper import YahooScraper
from BacktraderAPI.BTKernelRunWrapper import BTKernelRunWrapper
from CustomAPI.FutuAPI import FutuAPI
from BacktraderAPI.Strategy import TrendFollowingStrategy

#Access
# SP500 = YahooScraper().readSP500List().head()["ticker"].tolist()
# HK_HSIConstituent_code = FutuAPI().getPlateStock("HK.HSI Constituent")["code"].values.tolist()

# INPUT HERE
INITIALCASH = 100000
SYMBOLS = ["HK.HSImain"]
SUBTYPE = SubType.K_30M
TIMERANGE = ("2020-08-01", "09:30:00", "2021-02-03", "16:15:00")
REMARKS = ""

STRATEGYNAME = BTStrategy.IchimokuStrategy

## Change this for ONE strategy
sameStrategyParameters = [dict(STRATEGYNAME= STRATEGYNAME,
                               STRATEGYPARAMS=dict()
                               )]

## Change this for MANY strategies
differentStrategyParametersList = list()
for a in range(5, 30, 2):
    strategyParameters = dict(STRATEGYNAME=STRATEGYNAME,
                              STRATEGYPARAMS=dict(kijun=a, tenkan=9, chikou=26, senkou=52, senkou_lead=26))
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
    # BTKernelRunWrapper(sameDataParametersList, sameStrategyParameters).runOneTime(bokeh=False, iPython=False, quantStats=True)
    BTKernelRunWrapper(sameDataParametersList, differentStrategyParametersList).runOptimizationWithSameData(sortKey="VWR")
    # BTKernelRunWrapper(differentDataParametersList, sameStrategyParameters).runOptimizationWithDifferentData(sortKey="VWR")
    # BTKernelRunWrapper(differentDataParametersList, sameStrategyParameters).runScreening()