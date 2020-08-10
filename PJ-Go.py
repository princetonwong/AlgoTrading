from CustomAPI.Execution import Execution
from futu import *
import CustomAPI.Helper as helper

# from CustomAPI.FutuAPI import FutuAPI ; HK_HSIConstituent_code = FutuAPI().getPlateStock("HK.HSI Constituent")["code"].values.tolist()
HKStockSubtypes = [SubType.K_1M, SubType.K_3M, SubType.K_5M, SubType.K_15M, SubType.K_30M, SubType.K_60M]
USOptionSubTypes = [SubType.K_DAY, SubType.K_1M, SubType.K_5M, SubType.K_15M, SubType.K_60M]

#PARAMETERS
TIMERANGE = ("2019-07-01", "00:00:00", "2020-07-31", "16:31:00")
# TIMERANGE = None
SYMBOLS = ["HK.MHImain"]
SUBTYPES= [SubType.K_DAY]

timeNow = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
helper.projectName = "close, trade by cci" + "{}-{}-{}-{}".format(SYMBOLS[0:2], SUBTYPES[0:2], TIMERANGE, timeNow)

execution = Execution(SYMBOLS, SUBTYPES, TIMERANGE)
execution.runBatchTests(cciParameters=(26, 0.015, 100, 5))
execution.runSummary(feePerOrder= 10.6)

# execution.plotTimeSeries()
execution.plotCumulativeReturn()
execution.plotDailyReturnHistogram()

execution.outputAnalyticsXLSX()
execution.outputOrdersXLSX()
execution.outputModelDataXLSX()