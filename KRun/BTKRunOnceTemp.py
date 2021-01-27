from futu import *
from BacktraderAPI import BTStrategy, BTSizer
from BacktraderAPI.BTKernelRun import BTKernelRun

parameters = dict(INITIALCASH=50000,
                  SYMBOL="TSLA",
                  SUBTYPE=SubType.K_DAY,
                  TIMERANGE=("2019-09-01", "00:00:00", "2020-12-28", "23:59:00"),
                  REMARKS=""
                  )
strategy = dict(STRATEGYNAME=BTStrategy.IchimokuStrategy,
                STRATEGYPARAMS=dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold=1,
                                    stopLossPerc=0.016)
                )


class BTKernelRunOneStrategy(BTKernelRun):
    def run(self):
        # Run One Time
        self.setFolderName()
        self.loadData()
        self.addWriter(writeCSV=True)
        self.addSizer(sizer=BTSizer.FixedSizer)
        self.addBroker()
        self.addStrategy()
        self.addAnalyzer()
        self.addObserver(SLTP=False)
        self.run()
        self.plotBokeh()
        self.plotIPython()
        self.getAnalysisResults(quantStats=True)
        return


# Run One Time
BTKernelRunOneStrategy(allParams=parameters, strategyParams=strategy).run()
