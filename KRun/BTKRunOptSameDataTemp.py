from futu import *
from tqdm.contrib.concurrent import process_map
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTObserver, BTCommInfo, BTKernelRun
from CustomAPI.Helper import Helper

def optimizationWithSameData(sortKey: str) -> pd.DataFrame:

    #One Time Parameters
    allParams = dict(INITIALCASH=50000,
                     SYMBOL="AAPL",
                     SUBTYPE=SubType.K_5M,
                     TIMERANGE=("2020-08-01", "00:00:00", "2020-09-27", "23:59:00"),
                     REMARKS=""
                     )

    #Many Time Parameters
    params_list = []
    for a in range(6, 8, 1):
        strategyParams = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                              STRATEGYPARAMS=dict(kijun=a, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold=1,
                                                  stopLossPerc=0.016))
        params_list.append({**strategyParams})

    #Run One Time
    btCoreRun = BTKernelRun.BTCoreRun(allParams=allParams, strategyParams=strategyParams, isOptimization=True)
    btCoreRun.setFolderName()
    btCoreRun.loadData()
    stats = process_map(btCoreRun.runOptimizationWithSameData, params_list, max_workers=os.cpu_count())

    #Results
    df = pd.DataFrame(stats)
    df.sort_values(sortKey, ascending=False, inplace=True)
    btCoreRun.helper.gradientAppliedXLSX(df, "Optimization",
                                    ["Kelly Percent", "Max DrawDown", "PnL Net", "SQN", "Sharpe Ratio", "VWR",
                                     "Strike Rate"])
    return df

optimizationWithSameData(sortKey= "VWR")