from futu import *
from tqdm.contrib.concurrent import process_map
from BacktraderAPI import BTStrategy, BTKernelRun
from CustomAPI.Helper import Helper

#Wrapper Function
def runScreening(allParams, strategyParams):
    btCoreRun = BTKernelRun.BTCoreRun(allParams=allParams, strategyParams=strategyParams, isOptimization=True)
    btCoreRun.setFolderName()
    btCoreRun.loadData()
    return btCoreRun.runScreening(strategyParams)


def screening() -> pd.DataFrame:
    #Many Time Parameters
    all_list = []
    params_list = []
    for symbol in ["TSLA", "AAPL"]:
        allParams = dict(INITIALCASH=50000,
                         SYMBOL= symbol,
                         SUBTYPE=SubType.K_5M,
                         TIMERANGE=("2020-09-05", "00:00:00", "2020-09-27", "23:59:00"),
                         REMARKS=""
                         )
        strategyParams = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                              STRATEGYPARAMS=dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold= 1, stopLossPerc= 0.016)
                              )

        all_list.append({**allParams})
        params_list.append({**strategyParams})

    stats = process_map(runScreening, all_list, params_list, max_workers=os.cpu_count())

    #Results
    df = pd.DataFrame(stats)
    # df.sort_values(sortKey, ascending=False, inplace=True)
    Helper().gradientAppliedXLSX(df, "Screening",[])
    return df

screening()