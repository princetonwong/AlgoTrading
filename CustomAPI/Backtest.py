from CustomAPI.FutuAPI import FutuAPI
from CustomAPI.TradeModel import TradeModel
from CustomAPI.Helper import Helper

class Backtest():
    def __init__(self, symbol: str, kLineSubType: str, count: int = 999):
        self.count = count
        self.symbol = symbol
        self.kLineSubType = kLineSubType
        self.model = TradeModel()
        self.filename = self.symbol + "---" + self.kLineSubType

    def obtainDataFromFutu(self, timeRange):
        if timeRange is None:
            self.model.data = FutuAPI().getRealTimeKLine(symbol=self.symbol, num=self.count, subtype=self.kLineSubType)

        else:
            self.model.data = FutuAPI().getKLineFromDate(self.symbol, timeRange, self.kLineSubType)
            self.count = self.model.data.shape[0]
            self.filename = self.symbol + "---" + self.kLineSubType + "---" + timeRange

        self.model.processDataAfterDownload(count=self.count)
        return self.model.data

    def orderBy(self, MACD = False, SLOWKD = False, CCI = False):
        if MACD:
            self.model.orderByMACD()
        if SLOWKD:
            self.model.orderBySLOWKD()
        if CCI:
            self.model.orderByCCI()

    def runBBANDS(self, bbandsParameters):
        self.bbandsParameters = bbandsParameters
        self.model.setupBBANDS(bbandsParameters)

    def runMA(self, maParameters):
        self.maParameters = maParameters
        self.model.setupMA(maParameters)

    def runMACD(self, macdParameters, tIndex= -2):
        self.macdParameters = macdParameters
        self.model.prepareMACD(macdParameters)
        self.macdThreshold = self.model.calculateMACDThreshold(tIndex)
        self.model.computeMACDScore()

    def runSLOWKD(self, slowkdParameters):
        self.slowkdParameters = slowkdParameters
        self.model.prepareSLOWKD(slowkdParameters)
        self.slowkdThreshold = self.model.calculateSLOWKDThreshold()
        self.model.computeSLOWKDScore()

    def runCCI(self, cciParameters):
        self.cciParameters = cciParameters
        self.model.prepareCCI(cciParameters)
        self.cciThreshold = cciParameters[3]
        self.model.computeCCIScore_2()




