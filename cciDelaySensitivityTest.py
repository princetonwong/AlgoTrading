from CustomAPI.Execution import Execution
from futu import *
import CustomAPI.Helper as helper

TIMERANGE = None
SYMBOLS = ["HK.MHImain", "HK.00700"]
SUBTYPES= [SubType.K_30M]

timeNow = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
helper.projectName = "close, trade by cci" + "{}-{}-{}-{}".format(SYMBOLS[0:2], SUBTYPES[0:2], TIMERANGE, timeNow)

import copy
import matplotlib.pyplot as plt

sharpeList = []
ns = range(4,10)
execution2 = Execution(SYMBOLS, SUBTYPES, TIMERANGE)

for i in range(4,10):
    execution = copy.deepcopy(execution2)
    execution.runBatchTests(cciParameters=(26, 0.015, 100, i))
    summaries = execution.runSummary(feePerOrder= 10.6)
    ratio = summaries[0].analytics["SharpeRatio"][0]
    print (summaries[0].analytics)
    sharpeList.append(ratio)

plt.figure(figsize=(15, 8))
plt.plot(ns,sharpeList)
plt.title("{}-{}".format(SYMBOLS[0:2], SUBTYPES[0:2]))
plt.show()
# plt.savefig(SYMBOLS + "-" + SUBTYPES + ".png", dpi=100)
    # execution.plotTimeSeries()
    # execution.plotCumulativeReturn()
    # execution.outputAnalyticsXLSX()
    # execution.outputOrdersXLSX()
    # execution.outputModelDatasXLSX()