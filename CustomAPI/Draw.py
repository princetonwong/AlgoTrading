import matplotlib.pyplot as pyplot

class Draw():
    longColor = "#00ff00"
    shortColor = "#ff0000"

    def markLongSignal(self, axis, x, y) -> None:
        axis.scatter(x, y, color=None, marker='^', edgecolors= self.longColor, s=300, linewidths=3)

    def markShortSignal(self, axis, x, y) -> None:
        axis.scatter(x, y, color=None, marker='v', edgecolors= self.shortColor, s=300, linewidths=3)

    def KLine(self, dataFrame, axis):
        # onAxis.set_xlim(0, count)
        # line.set_axis_off()
        axis.xaxis.set_major_locator(pyplot.NullLocator())
        axis.yaxis.set_major_locator(pyplot.NullLocator())

        # t = range(len(dataFrame))
        #
        # o = list(dataFrame['open'].values)
        # h = list(dataFrame['high'].values)
        # l = list(dataFrame['low'].values)
        # c = list(dataFrame['close'].values)
        # quotes = zip(t, o, h, l, c)
        #
        # # 画K线
        # mpf.plot(onAxis, quotes, width=0.5, colorup='r', colordown='g')
        # mpf.plot(dataFrame, type = "candle")
        axis.plot(dataFrame['close'], 'b')
        axis.set_label("KLine")

    def MA(slef, dataFrame, axis):
        dataFrame[['ma5', 'ma10', 'ma20', 'ma60']].plot(ax=axis, legend=True)

    def BBANDS(self, dataFrame, axis):
        axis.xaxis.set_major_locator(pyplot.NullLocator())
        axis.yaxis.set_major_locator(pyplot.NullLocator())
        dataFrame[['UpperBand', 'MiddleBand', 'LowerBand']].plot(ax=axis, legend=True)

    def MACDCrossOnKLine(self, dataFrame, macdThreshold, axis):
        macd = dataFrame['macd'].values
        macdDIFF = dataFrame['diff'].values
        macdDEA = dataFrame['dea'].values
        close = dataFrame['close'].values

        for i in range(4, len(macd)):
            if macdDIFF[i - 1] < macdDEA[i - 1] and macdDIFF[i] > macdDEA[i] and macdDIFF[i] < -macdThreshold:
                self.markLongSignal(axis, i, close[i])

            elif macdDIFF[i - 1] > macdDEA[i - 1] and macdDIFF[i] < macdDEA[i] and macdDIFF[i] > macdThreshold:
                self.markShortSignal(axis, i, close[i])

    def MACD(self, dataFrame, axis):
        macd = dataFrame['macd'].values

        axis.xaxis.set_major_locator(pyplot.NullLocator())
        axis.yaxis.set_major_locator(pyplot.NullLocator())

        axis.plot(dataFrame['diff'], 'b', label="DIFF")
        axis.plot(dataFrame['dea'], 'y', label="DEA")

        t = range(len(dataFrame))
        for i in t:
            axis.bar(i, macd[i], color='r' if macd[i] > 0 else 'g')

    def MACDCross(self, dataFrame, axis):
        macdDEA = dataFrame['dea'].values
        macdScore = dataFrame["macdScore"].values

        for i in range(4, len(macdDEA)):
            if macdScore[i] == 1:
                self.markLongSignal(axis, i, macdDEA[i])

            elif macdScore[i] == -1:
                self.markShortSignal(axis, i, macdDEA[i])

    def Volume(self, dataFrame, axis):
        axis.xaxis.set_major_locator(pyplot.NullLocator())
        axis.yaxis.set_major_locator(pyplot.NullLocator())

        v = list(dataFrame['volume'].values)

        t = range(len(dataFrame))

        # o = list(df['open'].values)
        # h = list(df['high'].values)
        # l = list(df['low'].values)
        # c = list(df['close'].values)
        #
        barlist = axis.bar(t, v, width=0.5)
        #
        # color = 'r'
        # for i in t:
        #     if o[i] < c[i]:
        #         color = 'r'
        #     else:
        #         color = 'g'

        # barlist[i].set_color(color)

    def SLOWKD(self, dataFrame, axis):
        # ax.set_axis_off()
        axis.xaxis.set_major_locator(pyplot.NullLocator())
        axis.yaxis.set_major_locator(pyplot.NullLocator())

        axis.plot(dataFrame['slowk'], 'b')
        axis.plot(dataFrame['slowd'], 'y')

    def SLOWKDCross(self, dataFrame, axis):
        slowk = dataFrame['slowk'].values
        slowkdScore = dataFrame["slowkdScore"].values

        for i in range(4, len(slowk)):
            if slowkdScore[i] == 1:
                self.markLongSignal(axis, i, slowk[i])

            elif slowkdScore[i] == -1:
                self.markShortSignal(axis, i, slowk[i])

    def CCI(self, dataFrame, axis):
        axis.xaxis.set_major_locator(pyplot.NullLocator())
        axis.yaxis.set_major_locator(pyplot.NullLocator())
        axis.plot(dataFrame['CCI'], 'b')

    def CCICross(self, dataFrame, axis):
        cci = dataFrame['CCI'].values
        cciScore = dataFrame["CCIScore"].values

        for i in range(4, len(cci)):
            if cciScore[i] == 1:
                self.markLongSignal(axis, i, cci[i])

            elif cciScore[i] == -1:
                self.markShortSignal(axis, i, cci[i])

    def OrderPlaced (self, df, axis):
        orderPlaced = df["orderPlaced"].values
        close = df["close"].values

        for i in range(4, len(close)):
            if orderPlaced[i] == 1:
                self.markLongSignal(axis, i, close[i])

            elif orderPlaced[i] == -1:
                self.markShortSignal(axis, i, close[i])

