from futu import *
from BacktraderAPI import BTStrategy, BTKernelRun

allParams = dict(INITIALCASH= 50000,
                         SYMBOL= "TSLA",
                         SUBTYPE= SubType.K_5M,
                         TIMERANGE= ("2020-08-01", "00:00:00", "2020-09-27", "23:59:00"),
                         REMARKS= ""
                         )
strategyParams = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                              STRATEGYPARAMS=dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold= 1, stopLossPerc= 0.016)
                              )
coreRun = BTKernelRun.BTCoreRun(allParams= allParams, strategyParams=strategyParams)
coreRun.runOneStrategy(strategyParams=strategyParams)