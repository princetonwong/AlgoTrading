from futu import *
from tqdm.contrib.concurrent import process_map
from BacktraderAPI import BTStrategy, BTKernelRun, BTScreener
from CustomAPI.Helper import Helper
from CustomAPI.YahooScraper import YahooScraper
import numpy as np


# Wrapper Function
def runScreening(allParams, strategyParams):
    btCoreRun = BTKernelRun.BTKernelRun(allParams=allParams, strategyParams=strategyParams, isOptimization=True)
    btCoreRun.setFolderName()
    btCoreRun.loadData()
    btCoreRun.strategyName = BTStrategy.EmptyStrategy
    btCoreRun.addWriter(writeCSV=True)
    btCoreRun.addBroker()
    btCoreRun.addStrategy(strategyParams)
    btCoreRun.addScreener(screener=BTScreener.MyScreener)
    btCoreRun.run()
    # self.plotBokeh()
    return btCoreRun.getScreeningResults()


def screening() -> pd.DataFrame:
    # Many Time Parameters
    all_list = []
    params_list = []

    # sp500list = YahooScraper().readSP500List().head(200)
    # for symbol in sp500list["ticker"].tolist():

    from CustomAPI.FutuAPI import FutuAPI
    HK_HSIConstituent_code = FutuAPI().getPlateStock("HK.HSI Constituent")["code"].values.tolist()
    for symbol in HK_HSIConstituent_code:

        allParams = dict(INITIALCASH=50000,
                         SYMBOL=symbol,
                         SUBTYPE=SubType.K_DAY,
                         TIMERANGE=("2020-01-05", "00:00:00", "2020-12-14", "23:59:00"),
                         REMARKS="HSICons"
                         )
        strategyParams = dict(STRATEGYNAME=BTStrategy.EmptyStrategy,
                              STRATEGYPARAMS=dict()
                              )

        all_list.append({**allParams})
        params_list.append({**strategyParams})

    results = process_map(runScreening, all_list, params_list, max_workers=os.cpu_count())

    # Results
    return prettifyScreeningResult(results)


def prettifyScreeningResult(results):
    df = pd.DataFrame(results)
    df = df[["Data Name", "Close"] + [col for col in df.columns if col != 'Data Name' and col != "Close"]]
    # df.sort_values(sortKey, ascending=False, inplace=True)
    dfRow, dfColumn = df.shape
    df.loc[dfRow] = np.repeat(-1, dfColumn)
    df.loc[dfRow + 1] = np.repeat(1, dfColumn)
    Helper().gradientAppliedXLSX(df, "Screening" + datetime.now().strftime("%Y-%m-%d %H-%M"),
                                 [col for col in df.columns if "Signal" in col])
    return df


screening()
