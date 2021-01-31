from futu import *
from tqdm.contrib.concurrent import process_map
from BacktraderAPI import BTKernelRun, BTSizer, BTStrategy, BTScreener
from BacktraderAPI.BTKernelRun import BTKernelRun
from CustomAPI.Helper import Helper; h = Helper()
import numpy as np

class BTKernelRunWrapper(object):
    def __init__(self, dataParameters: list, strategyParameters: list):
        self.dataParametersList = dataParameters
        self.strategyParametersList = strategyParameters
        self.isOptimization = False
        self.isScreening = False
        self.isDifferentData = False

    def setFolderName(self):
        if self.isOptimization:
            prefix = "Optimization"
        elif self.isScreening:
            prefix = "Screen"
            self.strategyName = BTStrategy.EmptyStrategy
        else:
            prefix = "RunOnce"

        if self.isDifferentData:
            prefix = prefix + ",DiffData"
        else:
            prefix = prefix + ",SameData"

        self.folderName = h.initializeFolderName(self.dataParametersList[0]["SYMBOL"],
                                                 self.dataParametersList[0]["SUBTYPE"],
                                                 self.dataParametersList[0]["TIMERANGE"],
                                                 self.strategyParametersList[0]["STRATEGYNAME"],
                                                 self.strategyParametersList[0]["STRATEGYPARAMS"],
                                                 self.dataParametersList[0]["REMARKS"],
                                                 prefix=prefix)
        return self.folderName

    def _outputOptimizationResultsXLSX(self, df, sortKey):
        df.sort_values(sortKey, ascending=False, inplace=True)
        h.gradientAppliedXLSX(df, self.folderName,
                                        ["Kelly Percent", "Max DrawDown", "PnL Net", "SQN", "Sharpe Ratio", "VWR",
                                         "Strike Rate"])
        return df

    @staticmethod
    def _runThisManyTimes_SameData(btCoreRun, strategyParams):
        btCoreRun.addSizer(sizer=BTSizer.FixedSizer)
        btCoreRun.addBroker()
        btCoreRun.addStrategy(strategyParams)
        btCoreRun.addAnalyzer()
        btCoreRun.addObserver(SLTP=False)
        btCoreRun.run()
        return btCoreRun.getAnalysisResults(quantStats=False)

    def _runThisManyTimes_DifferentData(self, dataParameters):
        btCoreRun = BTKernelRun(allParams=dataParameters, strategyParams=self.strategyParametersList[0],
                                isOptimization=True)
        btCoreRun.folderName = self.folderName
        btCoreRun.loadData()
        btCoreRun.addSizer(sizer=BTSizer.FixedSizer)
        btCoreRun.addBroker()
        btCoreRun.addStrategy(self.strategyParametersList[0])
        btCoreRun.addAnalyzer()
        btCoreRun.addObserver(SLTP=False)
        btCoreRun.run()
        return btCoreRun.getAnalysisResults(quantStats=False)

    def _runThisManyTimes_Screening(self, dataParameters):
        btCoreRun = BTKernelRun(allParams=dataParameters, strategyParams=self.strategyParametersList[0],
                                isOptimization=True)
        btCoreRun.folderName = self.folderName
        btCoreRun.loadData()
        btCoreRun.strategyName = BTStrategy.EmptyStrategy
        btCoreRun.addWriter(writeCSV=True)
        btCoreRun.addBroker()
        btCoreRun.addStrategy(self.strategyParametersList[0])
        btCoreRun.addScreener(BTScreener.MyScreener)
        btCoreRun.run()
        return btCoreRun.getScreeningResults()

    def runOptimizationWithSameData(self, sortKey="VWR") -> pd.DataFrame:
        # Run One Time
        self.isOptimization = True
        self.setFolderName()
        btCoreRun = BTKernelRun(allParams=self.dataParametersList[0], strategyParams=self.strategyParametersList[0],
                                isOptimization=True)
        btCoreRun.folderName = self.folderName
        btCoreRun.loadData()
        btCoreRunList = [btCoreRun for _ in range(len(self.strategyParametersList))]

        # Run Many Times
        results = process_map(self._runThisManyTimes_SameData, btCoreRunList, self.strategyParametersList, max_workers=os.cpu_count())

        # Results
        df = pd.DataFrame(results)

        return self._outputOptimizationResultsXLSX(df, sortKey)

    def runOptimizationWithDifferentData(self, sortKey="VWR") -> pd.DataFrame:
        # Run One Time
        self.isOptimization = True
        self.setFolderName()

        # Run Many Times
        stats = process_map(self._runThisManyTimes_DifferentData, self.dataParametersList, max_workers=os.cpu_count())

        # Results
        df = pd.DataFrame(stats)

        return self._outputOptimizationResultsXLSX(df, sortKey)

    def runOneTime(self):
        btCoreRun = BTKernelRun(self.dataParametersList[0], self.strategyParametersList[0])
        self.setFolderName()
        btCoreRun.folderName = self.folderName
        btCoreRun.loadData()
        btCoreRun.addWriter(writeCSV=True)
        btCoreRun.addSizer(sizer=BTSizer.FixedSizer)
        btCoreRun.addBroker()
        btCoreRun.addStrategy(self.strategyParametersList[0])
        btCoreRun.addAnalyzer()
        btCoreRun.addObserver(SLTP=False)
        btCoreRun.run()
        btCoreRun.plotBokeh()
        # btCoreRun.plotIPython()
        btCoreRun.getAnalysisResults(quantStats=True)
        return

    def runScreening(self) -> pd.DataFrame:
        def prettifyScreeningOutput(results):
            df = pd.DataFrame(results)
            df = df[["Data Name", "Close"] + [col for col in df.columns if col != 'Data Name' and col != "Close"]]
            # df.sort_values(sortKey, ascending=False, inplace=True)
            dfRow, dfColumn = df.shape
            df.loc[dfRow] = np.repeat(-1, dfColumn)
            df.loc[dfRow + 1] = np.repeat(1, dfColumn)
            Helper().gradientAppliedXLSX(df, "Screening" + datetime.now().strftime("%Y-%m-%d %H-%M"),
                                         [col for col in df.columns if "Signal" in col])
            return df

        # Run One Time
        self.isScreening = True
        self.setFolderName()
        # Run Many Times
        results = process_map(self._runThisManyTimes_Screening, self.dataParametersList, max_workers=os.cpu_count())

        # Results
        df = prettifyScreeningOutput(results)

        return df