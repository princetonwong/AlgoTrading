from futu import *
from tqdm.contrib.concurrent import process_map
from BacktraderAPI import BTStrategy, BTKernelRun, BTSizer, BTStrategy
from BacktraderAPI.BTKernelRun import BTKernelRun
from CustomAPI.Helper import Helper
from CustomAPI.YahooScraper import YahooScraper

#Access
SP500 = YahooScraper().readSP500List().head()["ticker"].tolist()

# INPUT HERE
INITIALCASH = 50000
SYMBOLS = SP500
SUBTYPE = SubType.K_5M
TIMERANGE = ("2020-09-01", "00:00:00", "2020-09-27", "23:59:00")
REMARKS = ""

##
sameStrategyParameters = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                              STRATEGYPARAMS=dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6,
                                                  trailHold=1,
                                                  stopLossPerc=0.016)
                              )
##
differentStrategyParametersList = list()
for a in range(6, 8, 1):
    strategyParameters = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                              STRATEGYPARAMS=dict(kijun=a, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold=1,
                                                  stopLossPerc=0.016))
    differentStrategyParametersList.append({**strategyParameters})

##
sameDataParameters = dict(INITIALCASH=INITIALCASH,
                          SYMBOL=SYMBOLS[0],
                          SUBTYPE=SUBTYPE,
                          TIMERANGE=TIMERANGE,
                          REMARKS=REMARKS
                          )

##
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
    sameStrategyParametersList.append({**sameStrategyParameters})


class BTKernelRunner(BTKernelRun):

    def _runThisManyTimes_Same(self, strategyParams):
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy(strategyParams)
        self.addAnalyzer()
        self.addObserver(SLTP=False)
        self.run()
        return self.getAnalysisResults(quantStats=False)

    def _runThisManyTimes_Different(self, dataParameters):  # TODO
        btCoreRun = BTKernelRun.BTKernelRun(allParams=dataParameters, strategyParams=sameStrategyParameters,
                                            isOptimization=True)
        btCoreRun.folderName = self.folderName
        btCoreRun.loadData()
        btCoreRun.addSizer(sizer=BTSizer.FixedSizer)
        btCoreRun.addBroker()
        btCoreRun.addStrategy(sameStrategyParameters)
        btCoreRun.addAnalyzer()
        btCoreRun.addObserver(SLTP=False)
        btCoreRun.run()
        return btCoreRun.getAnalysisResults(quantStats=False)

    def outputOptimizationResultsXLSX(self, df, sortKey):
        df.sort_values(sortKey, ascending=False, inplace=True)
        self.helper.gradientAppliedXLSX(df, self.folderName,
                                        ["Kelly Percent", "Max DrawDown", "PnL Net", "SQN", "Sharpe Ratio", "VWR",
                                         "Strike Rate"])
        return df

    def runOptimizationWithSameData(self, sortKey="VWR") -> pd.DataFrame:
        # Run One Time
        self.isOptimization = True
        self.folderName = self.helper.initializeFolderName(self.symbol, self.subType,
                                                           self.timerange, self.strategyName,
                                                           self.strategyParams, self.remarks, prefix="SameData")
        self.loadData()

        # Run Many Times
        results = process_map(self._runThisManyTimes_Same, differentStrategyParametersList, max_workers=os.cpu_count())

        # Results
        df = pd.DataFrame(results)

        return self.outputOptimizationResultsXLSX(df, sortKey)

    def runOptimizationWithDifferentData(self, sortKey="VWR") -> pd.DataFrame:
        # Run One Time
        self.isOptimization = True
        self.folderName = self.helper.initializeFolderName(SYMBOLS[0:2], self.subType,
                                                           self.timerange, self.strategyName,
                                                           self.strategyParams, self.remarks, prefix="DiffData")

        # Run Many Times
        stats = process_map(self._runThisManyTimes_Different, differentDataParametersList, max_workers=os.cpu_count())

        # Results
        df = pd.DataFrame(stats)

        return self.outputOptimizationResultsXLSX(df, sortKey)

    def runOneTime(self):
        self.setFolderName()
        self.loadData()
        self.addWriter(writeCSV=True)
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy(sameStrategyParameters)
        self.addAnalyzer()
        self.addObserver(SLTP=False)
        self.run()
        self.plotBokeh()
        # self.plotIPython()
        self.getAnalysisResults(quantStats=True)
        return

    def _runThisManyTimes_Screening(self, dataParameters):
        btCoreRun = BTKernelRun.BTKernelRun(allParams=dataParameters, strategyParams=sameStrategyParameters, isOptimization=True)
        btCoreRun.folderName = self.folderName
        btCoreRun.loadData()
        btCoreRun.strategyName = BTStrategy.EmptyStrategy
        btCoreRun.addWriter(writeCSV=True)
        btCoreRun.addBroker()
        btCoreRun.addStrategy(sameStrategyParameters)
        btCoreRun.addScreener()
        btCoreRun.run()
        return btCoreRun.getScreeningResults()

    def runScreening(self) -> pd.DataFrame:
        # Run One Time
        self.isScreening = True
        self.folderName = self.helper.initializeFolderName(SYMBOLS[0:2], self.subType,
                                                           self.timerange, BTStrategy.EmptyStrategy,
                                                           dict(s=0), self.remarks, prefix="Screening")

        # Run Many Times
        results = process_map(self._runThisManyTimes_Screening, differentDataParametersList, max_workers=os.cpu_count())

        # Results
        df = pd.DataFrame(results)
        # df.sort_values(sortKey, ascending=False, inplace=True)
        self.helper.gradientAppliedXLSX(df, self.folderName, [])
        return df

## Examples
# BTKernelRunner(sameDataParameters, sameStrategyParameters).runOneTime()
# BTKernelRunner(sameDataParameters, differentStrategyParametersList[0]).runOptimizationWithSameData(sortKey="VWR")
# BTKernelRunner(differentDataParametersList[0], sameStrategyParameters).runOptimizationWithDifferentData(sortKey="VWR")
# BTKernelRunner(sameDataParameters, sameStrategyParameters).runScreening()