from futu import *
from tqdm.contrib.concurrent import process_map
from BacktraderAPI import BTStrategy, BTKernelRun
from CustomAPI.Helper import Helper
from CustomAPI.YahooScraper import YahooScraper

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
    sp500list = YahooScraper().readSP500List().head(1)

    for symbol in sp500list["ticker"].tolist():
        allParams = dict(INITIALCASH=50000,
                         SYMBOL= symbol,
                         SUBTYPE=SubType.K_5M,
                         TIMERANGE=("2020-09-05", "00:00:00", "2020-09-27", "23:59:00"),
                         REMARKS=""
                         )
        strategyParams = dict(STRATEGYNAME=BTStrategy.EmptyStrategy,
                              STRATEGYPARAMS=dict()
                              )

        all_list.append({**allParams})
        params_list.append({**strategyParams})

    stats = process_map(runScreening, all_list, params_list, max_workers=os.cpu_count())

    #Results
    df = pd.DataFrame(stats)
    # df.sort_values(sortKey, ascending=False, inplace=True)
    Helper().gradientAppliedXLSX(df, "Screening" + datetime.now().strftime("%Y-%m-%d"),[])
    return df

screening()