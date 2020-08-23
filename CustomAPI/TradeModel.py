import pandas as pd
import talib as tl
import numpy as np
import CustomAPI.Helper as helper


# field = Helper().field

class TradeModel():
    
    def __init__(self):
        self.data = pd.DataFrame()

    def processDataAfterDownload(self, count):
        self.data = self.data.iloc[0 - count:]
        t = range(count)
        self.data["holding"] = pd.Series(0, index=self.data.index.values)
        self.data["orderPlaced"] = pd.Series()
        self.data['t'] = pd.Series(t, index=self.data.index)
        self.data = self.data.set_index('t')
        self.data['index_ret'] = np.concatenate(([np.nan], np.array(self.data["close"][1:]) / np.array(self.data["close"][:-1]))) - 1

    # Overlap Studies (Lagging indicator)
    # MACD -

    def prepareMACD (self, macdParameters):
        self.macdParameters = macdParameters
        diff, dea, macd = self.macdParameters
        diff, dea, macd = tl.MACD(self.data["close"].values, diff, dea, macd)

        self.data['diff'] = pd.Series(diff, index=self.data.index.values)
        self.data['dea'] = pd.Series(dea, index=self.data.index.values)
        self.data['macd'] = pd.Series(macd * 2.0, index=self.data.index.values)
        self.data["macdThreshold"] = pd.Series(0)
        self.data["macdScore"] = pd.Series()

    def calculateMACDThreshold(self, tIndex):
        macd = self.data['macd'].values
        macdDIFF = self.data['diff'].values
        macdDEA = self.data['dea'].values
        macdThreshold = self.data["macdThreshold"].values

        for i in range(4, len(macd)):
            if macdDIFF[i - 1] < macdDEA[i - 1] and macdDIFF[i] > macdDEA[i]:
                macdThreshold[i] = macdDEA[i]

            elif macdDIFF[i - 1] > macdDEA[i - 1] and macdDIFF[i] < macdDEA[i]:
                macdThreshold[i] = -macdDEA[i]

            if macdThreshold[i] == None:
                macdThreshold[i] = 0

            macdThreshold[i] = np.nanmax(macdThreshold)

        ls = np.unique(macdThreshold)
        ls = sorted(np.nan_to_num(ls).tolist())
        self.macdThreshold =  ls[tIndex]
        return self.macdThreshold

    def computeMACDScore (self):
        macd = self.data['macd'].values
        macdDIFF = self.data['diff'].values
        macdDEA = self.data['dea'].values
        macdScore = self.data["macdScore"].values

        for i in range(4, len(macd)):
            if macdDIFF[i - 1] < macdDEA[i - 1] and macdDIFF[i] > macdDEA[i] and macdDEA[i] < -self.macdThreshold:
                macdScore[i] = 1

            elif macdDIFF[i - 1] > macdDEA[i - 1] and macdDIFF[i] < macdDEA[i] and macdDEA[i] > self.macdThreshold:
                macdScore[i] = -1
            else:
                macdScore[i] = 0
        return macdScore

    def prepareSLOWKD(self, slowkdParameters):
        self.slowkdParameters = slowkdParameters
        fastKPeriod, slowKPeriod, slowDPeriod = self.slowkdParameters
        high = self.data['high'].values
        low = self.data['low'].values
        close = self.data['close'].values
        self.data["slowkdScore"] = pd.Series(0)

        slowk, slowd = tl.STOCH(high, low, close, fastk_period=fastKPeriod, slowk_period=slowKPeriod, slowk_matype=0, slowd_period=slowDPeriod,
                                slowd_matype=0)
        self.data['slowk'] = pd.Series(slowk, index=self.data.index.values)
        self.data['slowd'] = pd.Series(slowd, index=self.data.index.values)

    def calculateSLOWKDThreshold(self): #TODO: implement this threshold to BT
        self.slowkdThreshold = 40
        return self.slowkdThreshold

    def computeSLOWKDScore(self):
            slowk = self.data['slowk'].values
            slowd = self.data['slowd'].values
            slowkdScore = self.data["slowkdScore"].values

            for i in range(4, len(slowk)):
                if slowk[i - 1] < slowd[i - 1] and slowk[i] > slowd[i] and slowk[i] < 50 - self.slowkdThreshold:
                    slowkdScore[i] = 1

                elif slowk[i - 1] > slowd[i - 1] and slowk[i] < slowd[i] and slowk[i] > 50 + self.slowkdThreshold:
                    slowkdScore[i] = -1

                else:
                    slowkdScore[i] = 0

    # momentum
    def prepareCCI(self, cciParameters):
        self.cciParameters = cciParameters
        n, a, cciThreshold, m = cciParameters

        def cal_meandev(tp, matp):
            mean_dev = (n - 1) * [np.nan]
            for i in range(len(tp) - n + 1):
                mean_dev.append(np.mean(abs(tp[i:i + n] - matp[i + n - 1])))
            return np.array(mean_dev)

        self.data['tp'] = (self.data['close'] + self.data['high'] + self.data['low']) / 3
        self.data['matp'] = self.data['tp'].rolling(n).mean()
        self.data['mean_dev'] = cal_meandev(self.data['tp'], self.data['matp'])
        self.data['CCI'] = (self.data['tp'] - self.data['matp']) / (a * self.data['mean_dev'])
        self.data["CCIScore"] = pd.Series(0)

    def computeCCIScore_2(self):
        n, _, cciThreshold, m = self.cciParameters
        cci = self.data['CCI'].values
        cciScore = self.data["CCIScore"].values
        up_list = [0]
        down_list = [0]
        for i in range(n, len(cci)):
            if cci[i] > cciThreshold and cci[i - 1] < cciThreshold:
                cciScore[i] = 1
                up_list.append(i)

            elif cci[i] < -cciThreshold and cci[i - 1] > -cciThreshold:
                cciScore[i] = -1
                down_list.append(i)

            elif cci[i] < cciThreshold and i >= m + up_list[-1] and up_list[-1] > down_list[
                -1]:  # when cci downward cross 100
                cciScore[i] = -0.5  # 0.5 is a full exit
                # print ("{}: up_list{}, m{}".format(i, up_list,m))

            elif cci[i] > -cciThreshold and i >= m + down_list[-1] and down_list[-1] > up_list[-1]:
                cciScore[i] = 0.5
                # print("{}: down_list{}, m{}".format(i, down_list, m))

            # elif cci[i] < cciThreshold and cci[i] > 0:
            #     try:
            #         lastLongIndex = up_list[-1]
            #         if i < m + lastLongIndex:
            #             cciScore[i] = -0.01
            #
            #         elif i == m + lastLongIndex:
            #             cciScore[i] = -0.5
            #         else:
            #             cciScore[i] = 0
            #     except:
            #         cciScore[i] = 0
            #
            # elif cci[i] > -cciThreshold and cci[i] < 0:
            #     try:
            #         lastShortIndex = down_list[-1]
            #         if i < m + lastShortIndex:
            #             cciScore[i] = 0.01
            #
            #         elif i == m + lastShortIndex:
            #             cciScore[i] = 0.5
            #         else:
            #             cciScore[i] = 0
            #     except:
            #         cciScore[i] = 0

            else:
                cciScore[i] = 0

    def setupMA (self, maParameters):
        for i in maParameters:
            self.data["ma" + str(i)] = pd.Series(tl.MA(self.data['close'].values, i), index=self.data.index.values)

    def setupBBANDS (self, bbandsParameters):
        close = self.data["close"].values
        timeperiod, nbdevup, nbdevdn = bbandsParameters
        upperband, middleband, lowerband =tl.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype=0)
        standardDeviation = (upperband - middleband) / nbdevup
        zScore = (close - middleband) / standardDeviation
        self.data["UpperBand"] = pd.Series(upperband, index=self.data.index.values)
        self.data["LowerBand"] = pd.Series(lowerband, index=self.data.index.values)
        self.data["MiddleBand"] = pd.Series(middleband, index=self.data.index.values)
        self.data["ZScore"] = pd.Series(zScore, index=self.data.index.values)


    def orderByMACD (self):
        holding = self.data["holding"].values
        orderPlaced = self.data["orderPlaced"].values
        macd = self.data['macd'].values
        macdScore = self.data["macdScore"].values
        for i in range(4, len(macd)):
            if holding[i - 1] == 0:
                if macdScore[i] >= 1:
                    # long
                    holding[i] += 1
                    orderPlaced[i] = 1

                elif macdScore[i] <= -1:
                    # short
                    holding[i] -= 1
                    orderPlaced[i] = -1
                else:
                    self.defaultHolding(holding, i)

            elif holding[i - 1] == 1 and macd[i] < 0:
                holding[i] == 0
                orderPlaced[i] = -1

            elif holding[i - 1] == -1 and macd[i] > 0:
                holding[i] == 0
                orderPlaced[i] = 1
            else:
                self.defaultHolding(holding, i)

    @staticmethod
    def defaultHolding(holding, i):
            holding[i] = holding[i - 1]

    def orderBySLOWKD (self):
        holding = self.data["holding"].values
        orderPlaced = self.data["orderPlaced"].values
        slowkdScore = self.data["slowkdScore"].values
        slowk = self.data['slowk'].values
        self.data["orderSlowk"] = pd.Series(0, index= self.data.index)
        orderSlowk = self.data["orderSlowk"].values
        for i in range(1, len(slowk)):
            if holding[i-1] == 0:
                if slowkdScore[i] >= 1:
                    # place long order
                    orderPlaced[i] = 1
                    holding[i] += 1

                elif slowkdScore[i] <= -1:
                    # place short order
                    orderPlaced[i] = -1
                    holding[i] -= 1

                else:
                    self.defaultHolding(holding, i)

            elif holding[i-1] == 1 and (slowk[i] > 50 + (self.slowkdThreshold - 5) or slowk[i] <= orderSlowk[i-1]):
                # exit long position
                orderPlaced[i] = -1
                holding[i] == 0

            elif holding[i-1] == -1 and (slowk[i] < 50 - (self.slowkdThreshold - 5) or slowk[i] >= orderSlowk[i-1]):
                # exit short position
                holding[i] == 0
                orderPlaced[i] = 1
            else:
                self.defaultHolding(holding, i)

            if slowk[i-1] == None:
                slowk[i] = 0

            if holding[i-1] != holding[i]:
                orderSlowk[i] = slowk[i]
            else:
                orderSlowk[i] = orderSlowk[i-1]

    def orderByCCI (self):
        holding = self.data["holding"].values
        orderPlaced = self.data["orderPlaced"].values
        cci = self.data['CCI'].values
        cciScore = self.data["CCIScore"].values
        slowkdScore = self.data["slowkdScore"].values
        for i in range(1, len(cci)):
            if holding[i - 1] == 0:
                if cciScore[i] >= 1 and slowkdScore[i] != -1:
                    # long
                    holding[i] += 1
                    orderPlaced[i] = 1

                elif cciScore[i] <= -1 and slowkdScore[i] != 1:
                    # short
                    holding[i] -= 1
                    orderPlaced[i] = -1
                else:
                    self.defaultHolding(holding, i)

            elif holding[i - 1] == 1 and cciScore[i] <= -0.5:
                holding[i] == 0
                orderPlaced[i] = -1

            elif holding[i - 1] == -1 and cciScore[i] >= 0.5:
                holding[i] == 0
                orderPlaced[i] = 1
            else:
                self.defaultHolding(holding, i)


