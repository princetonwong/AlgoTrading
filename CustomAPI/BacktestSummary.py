import pandas as pd
import numpy as np
from datetime import datetime
from CustomAPI.Helper import Helper
import matplotlib.pyplot as plt

# field = "close"
field = "open"

class BacktestSummary():

    def __init__(self, backtest, feePerOrder):
        # self.summary = pd.DataFrame(
        #     columns=["Symbol", "KLineSubType", "Number of Orders", "Profit", "Slippage", "Total Fee"])
        self.orders = pd.DataFrame()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.filename = backtest.filename
        self.feePerOrder = feePerOrder

        self.backtest = backtest
        self.data = backtest.model.data
        self.n = backtest.cciParameters[0]
        self.analytics = pd.DataFrame()
        # self.analytics = pd.DataFrame(
        #     columns=["Symbol", "KLineSubType", "Number of Orders", "Profit", "Slippage", "Total Fee",
        #              "CumulativeReturn", "DailyWinRate", "MaxDrawdown", "SharpeRatio",
        #              "MACDParameters", "SlowKDParameters", "CCIParameters"])
        self.run()

    def runFromCSV(self, filename, feePerOrder):
        df = pd.read_csv(filename)
        self.run(df)

    def run(self):

        def calculateReturn():
            ret = self.n * [0]
            data = self.data
            data['index_ret'] = np.concatenate(
                ([np.nan], np.array(data[field][1:]) / np.array(data[field][:-1]))) - 1

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
            maximumDrawDown = -np.min(cumulativeReturn / max_nv - 1)
            return maximumDrawDown

        def computeProfitPerOrder(orderPlacedDf):
            field2 = orderPlacedDf[field].values
            orderPlacedDf["profitPerOrder"] = pd.Series()
            profitPerOrder = orderPlacedDf["profitPerOrder"].values
            orderPlaced = orderPlacedDf["orderPlaced"].values
            for i in range(numberOfOrders):
                if i%2 == 0:
                    pass
                elif i%2 == 1:
                    profitPerOrder[i] = (field2[i-1] - field2[i]) * orderPlaced[i]


        longOrderDf = self.data[self.data["orderPlaced"] == 1]
        shortOrderDf = self.data[self.data["orderPlaced"] == -1]

        long = longOrderDf[field].sum()   #TODO: last_close or close or open
        short = shortOrderDf[field].sum()   #TODO: last_close or close or open
        orderPlacedDf = pd.concat([longOrderDf, shortOrderDf])

        numberOfOrders = len(orderPlacedDf)

        profit = short - long
        totalFee = self.feePerOrder * numberOfOrders
        slippage = totalFee / profit

        dailyReturn = calculateReturn()
        self.data["DailyReturn"] = dailyReturn
        cumulativeReturn = calculateCumulativeReturn(dailyReturn)
        self.data["CumulativeReturn"] = cumulativeReturn

        analytics_dict = {}
        analytics_dict["Symbol"] = self.backtest.symbol
        analytics_dict["KLineSubType"] = self.backtest.kLineSubType
        analytics_dict["Number of Orders"] = [numberOfOrders]
        analytics_dict["ProfitBeforeFee"] = [profit]
        analytics_dict["Slippage"] = [slippage]
        analytics_dict["Total Fee"] = [totalFee]
        analytics_dict["MACDParameters"] = Helper().serializeTuple(self.backtest.macdParameters)
        analytics_dict["slowKDParameters"] = Helper().serializeTuple(self.backtest.slowkdParameters)
        analytics_dict["CCIParameters"] = Helper().serializeTuple(self.backtest.cciParameters)
        analytics_dict['CumulativeReturn'] = cumulativeReturn[-1] - 1
        analytics_dict['DailyWinRate'] = len(dailyReturn[dailyReturn > 0]) / (
                    len(dailyReturn[dailyReturn > 0]) + len(dailyReturn[dailyReturn < 0]))
        analytics_dict['MaxDrawdown'] = maximumDrawdown(cumulativeReturn)
        analytics_dict['SharpeRatio'] = dailyReturn.mean() / dailyReturn.std() * np.sqrt(240)

        self.analytics = pd.DataFrame(analytics_dict, index=[0])
        self.orders = orderPlacedDf.sort_values("time_key")
        computeProfitPerOrder(self.orders)