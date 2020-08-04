import numpy as np
import pandas as pd

class Analytics():

    def __init__(self, backtest):
        self.backtest = backtest
        self.data = backtest.model.data
        self.n = backtest.cciParameters[0]
        self.analytics = pd.DataFrame(
            columns=["CumulativeReturn", "DailyWinRate", "MaxDrawdown", "SharpeRatio",
                     "MACDParameters", "SlowKDParameters", "CCIParameters"])

    def run(self, backtests):
        def serializeTuple(tuple):
            return ",".join(str(x) for x in tuple)

        def calculateReturn():
            ret = self.n * [0]
            data = self.data
            data['index_ret'] = np.concatenate(
                ([np.nan], np.array(data['close'][1:]) / np.array(data['close'][:-1]))) - 1

            for i in range(self.n, len(data)):
                ret.append(data['holding'][i - 1] * data['index_ret'][i])

            return np.array(ret)

        def calculateCumulativeReturn(ret):
            cum_ret = [1]

            for i in range(len(ret) - 1):
                cum_ret.append(cum_ret[-1] * (1 + ret[i]))

            return np.array(cum_ret)

        def maximumDrawdown(cumulativeReturn):
            max_nv = np.maximum.accumulate(cumulativeReturn)
            mdd = -np.min(cumulativeReturn / max_nv - 1)
            return mdd

        dailyReturn = calculateReturn()
        self.data["DailyReturn"] = dailyReturn
        cumulativeReturn = calculateCumulativeReturn(dailyReturn)
        self.data["CumulativeReturn"] = cumulativeReturn

        analytics_dict = {}
        analytics_dict["MACDParameters"] = serializeTuple(self.backtest.macdParameters)
        analytics_dict["slowKDParameters"] = serializeTuple(self.backtest.slowkdParameters)
        analytics_dict["CCIParameters"] = serializeTuple(self.backtest.cciParameters)
        analytics_dict['CumulativeReturn'] = cumulativeReturn[-1] - 1
        analytics_dict['DailyWinRate'] = len(dailyReturn[dailyReturn > 0]) / (len(dailyReturn[dailyReturn > 0]) + len(dailyReturn[dailyReturn < 0]))
        analytics_dict['MaxDrawdown'] = maximumDrawdown(cumulativeReturn)
        analytics_dict['SharpeRatio'] = dailyReturn.mean() / dailyReturn.std() * np.sqrt(240)
        self.analytics = pd.DataFrame(analytics_dict, index=[0])

