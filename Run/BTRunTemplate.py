from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator, BTObserver, BTCommInfo
import copy
from typing import Dict, Union
from tqdm.contrib.concurrent import process_map

helper = Helper()

INITIALCASH = 50000
OUTPUTSETTINGS = dict(bokeh=True,plot=False,observer=True,analyzer=True, optimization=False, quantstats=True)

# SYMBOL_LIST = ["SPY"]  #AlphaVantage, Yahoo
# SYMBOL = SYMBOL_LIST[0]
# SYMBOL = "BAC"      #HDFWiki
SYMBOL = "HK.MHImain"   #Futu
SUBTYPE = SubType.K_15M

TIMERANGE = ("2020-07-17", "00:00:00", "2020-09-18", "23:59:00") #TODO: Create CSV Writer to store Stock Info
# TIMERANGE = None

STRATEGY = BTStrategy.ASOCrossStrategyWithSqueezePercCCI
PARAMS = dict(period=8, smoothing=16, rsiFactor=30, asoThreshold= 10, squeezeThreshold= 0, cciThreshold = 100)

STRATEGY = BTStrategy.TTFStrategy
PARAMS = dict(lookback=19, upperband=100, lowerband=-100)

STRATEGY = BTStrategy.TTFwithStopTrail2
PARAMS = dict(lookback=19, upperband=100, lowerband=-100, stoptype=bt.Order.StopTrail, trailpercent = 0.05)

STRATEGY = BTStrategy.TTFHOLD
PARAMS = dict(hold = 10)

STRATEGY = BTStrategy.CCIStrategy.CCICrossHoldStopTrail
PARAMS = dict(cciPeriod=20, cciFactor=0.015, cciThreshold=100, hold = 6, takeProfitAmount= 100, stopLossAmount= 20)

STRATEGY = BTStrategy.IchimokuStrategy
PARAMS = dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold= 1, stopLossPerc= 0.016)
# PARAMS = dict(trailHold= 3, stopLossPerc= 0.011)

STRATEGY = BTStrategy.AOStrategy
PARAMS = dict(stopLossAmount= 100, trailHold=3, takeProfitPerc= 0.1)
PARAMS = dict(takeProfitPerc= 0.1)

STRATEGY = BTStrategy.PSARStrategy
PARAMS = dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold= 1, stopLossPerc= 0.016)

CUSTOM = "WithStopLoss"
FOLDERNAME = helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, PARAMS, CUSTOM)

# DATA0 = BTDataFeed.getHDFWikiPriceDataFeed([SYMBOL], startYear= "2016")
# DATA0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)
# DATA0 = BTDataFeed.getAlphaVantageDataFeeds(SYMBOL_LIST, compact=False, debug=False, fromdate=datetime(2019, 9, 10), todate=datetime(2019, 9, 18))[0]
DATA0 = BTDataFeed.getYahooDataFeeds(SYMBOL_LIST, SUBTYPE, TIMERANGE, period="1d", folderName=None)
COMMISSIONSCHEME = COMMISSION, MARGIN, MULT = (5, 0, 1)
COMMISSIONSCHEME = COMMISSION, MARGIN, MULT = (10.6, 25000, 10)

def run_strategy(params= {**PARAMS}, outputsettings={**OUTPUTSETTINGS}) -> pd.DataFrame:
    print (params)
    # if outputsettings["optimization"] is False:
    #     helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, PARAMS, CUSTOM)

    #Init
    cerebro = bt.Cerebro()
    cerebro.adddata(DATA0, name=SYMBOL)

    if outputsettings["optimization"] is False:
        cerebro.addwriter(bt.WriterFile, csv=False, out=helper.generateFilePath("BackTraderData", ".csv"), rounding=3)
    else:
        cerebro.addwriter(bt.WriterFile, rounding=3)

    # Multi-data feeds
    # data1 = copy.deepcopy(DATA0)
    # # data1.plotinfo.plotmaster = DATA0
    # cerebro.adddata(data1, name="HKA")

    #Data Filter
    # data1.addfilter(bt.filters.HeikinAshi(data1))

    #Sizer
    cerebro.addsizer(BTSizer.FixedSizer)

    #Broker
    cerebro.broker.setcash(INITIALCASH)
    cerebro.broker.setcommission(commission=COMMISSION, margin=MARGIN, mult=MULT)
    # cerebro.broker.addcommissioninfo(BTCommInfo.FixedCommisionScheme(commission=2))
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #Strategy
    cerebro.addstrategy(STRATEGY, **params)

    #Analyzer
    if outputsettings["analyzer"]:
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                            annualize=True, _name="sharperatio")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(BTAnalyzer.Kelly, _name="kelly")
        cerebro.addanalyzer(bt.analyzers.VWR, _name="vwr")
        cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
        cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Minutes, _name="timereturn")


    if outputsettings["observer"]:
        cerebro.addobserver(bt.observers.DrawDown)
        cerebro.addobserver(bt.observers.Trades)
        cerebro.addobserver(bt.observers.Broker)
        cerebro.addobserver(BTObserver.BuySellStop)
        cerebro.addobserver(bt.observers.BuySell, barplot= True, bardist= 0.01)
        # cerebro.addobserver(BTObserver.SLTPTracking)
        cerebro.addobserver(bt.observers.TimeReturn)

    #Run
    results = cerebro.run(stdstats=False, runonce=False)
    finalPortfolioValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % finalPortfolioValue)

    #Bokeh Optimization
    # from backtrader_plotting import Bokeh, OptBrowser
    # from backtrader_plotting.schemes import Tradimo
    # b = Bokeh(style='bar', scheme=Tradimo())
    # browser = OptBrowser(b, results)
    # browser.start()

    if outputsettings["bokeh"]:
        from backtrader_plotting import Bokeh
        from backtrader_plotting.schemes import Tradimo
        b = Bokeh(filename=helper.generateFilePath("Report", ".html"), style='bar', plot_mode='single', scheme=Tradimo())
        fig = cerebro.plot(b, iplot=False)

    if outputsettings["plot"]:
        figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1, show=False)

        if outputsettings["optimization"] is False:
            helper.saveFig(figs)

    if outputsettings["analyzer"]:
        strategy = results[0]
        taAnalyzer = strategy.analyzers.ta.get_analysis()
        sharpeRatioAnalyzer = strategy.analyzers.sharperatio.get_analysis()
        drawdownAnalyzer = strategy.analyzers.drawdown.get_analysis()
        sqnAnalyzer = strategy.analyzers.sqn.get_analysis()
        returnAnalyzer = strategy.analyzers.returns.get_analysis()
        vwrAnalyzer = strategy.analyzers.vwr.get_analysis()
        transactionsAnalyzer = strategy.analyzers.transactions.get_analysis()
        timeReturnAnalyzer = strategy.analyzers.timereturn.get_analysis()

        taAnalyzerDF = BTAnalyzer.getTradeAnalysisDf(taAnalyzer)
        sqnDF = BTAnalyzer.getSQNDf(sqnAnalyzer)
        drawdownDF = BTAnalyzer.getDrawDownDf(drawdownAnalyzer)
        sharpeRatioDF = BTAnalyzer.getSharpeRatioDf(sharpeRatioAnalyzer)
        vwrDF = BTAnalyzer.getVWRDf(vwrAnalyzer)
        returnDF = BTAnalyzer.getReturnDf(returnAnalyzer)
        cashDF = pd.Series([INITIALCASH, finalPortfolioValue], index=["Initial Cash", "Final Portfolio Value"])
        kellyDF = pd.Series([strategy.analyzers.kelly.get_analysis().kellyPercent], index=["Kelly Percent"])
        transactionsDF = BTAnalyzer.getTransactionsDf(transactionsAnalyzer)
        timeReturnDF = BTAnalyzer.getTimeReturnDf(timeReturnAnalyzer)

        statsDF = pd.concat([taAnalyzerDF,
                             cashDF,
                             returnDF,
                             sqnDF,
                             sharpeRatioDF,
                             vwrDF,
                             drawdownDF,
                             kellyDF,
                             ])

        if outputsettings["optimization"] is False:
            helper.outputXLSX(statsDF, "Statistics")
            helper.outputXLSX(transactionsDF, "Transactions")
            helper.outputXLSX(timeReturnDF, "TimeReturn")

        if outputsettings["quantstats"]:
            import quantstats as qs
            qs.extend_pandas()
            qs.stats.sharpe(timeReturnDF)
            # qs.plots.snapshot(timeReturnDF, title='Facebook Performance')
            qs.reports.html(timeReturnDF, output="qs.html")
        #     stock.sharpe()


        stats = {
            "Symbol": SYMBOL,
            "SubType": SUBTYPE,
            'Sharpe Ratio': statsDF['Sharpe Ratio'],
            'Average Return': statsDF['Average Return'],
            'Annualized Return%': statsDF['Annualized Return%'],
            'Max DrawDown': statsDF['Max DrawDown'],
            "Total Open" : statsDF["Total Open"],
            "Total Closed" : statsDF["Total Closed"],
            "Total Won" : statsDF["Total Won"],
            "Total Lost" : statsDF["Total Lost"],
            "Win Streak" : statsDF["Win Streak"],
            "Lose Streak" : statsDF["Losing Streak"],
            "PnL Net" : statsDF["PnL Net"],
            "Strike Rate" : statsDF["Strike Rate"],
            "SQN": statsDF["SQN"],
            "VWR": statsDF["VWR"],
            "Kelly Percent": statsDF["Kelly Percent"]
        }
        return  {**params, **stats}

    return  {**params}

def grid_search(sortKey: str) -> pd.DataFrame:
    global optimizationParams
    params_list = []
    outputsettings_list = []

    for a in range(1, 20, 1):
        # for y in range(2, 8, 1):
        #     for z in range(1, 8, 1):
        #         if x > y:
        x=6
        y=3
        z=3
        stopLoss = a / 1000
        outputsettings = dict(bokeh=False,plot=False,observer=True,analyzer=True, optimization=True, quantstats=False)
        optimizationParams = dict(kijun=6, tenkan=3, chikou=6, senkou=12, senkou_lead=6, trailHold= 1, stopLossPerc= stopLoss)

        params_list.append({**optimizationParams})
        outputsettings_list.append({**outputsettings})

    helper.folderName = "[Opt]" + helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, optimizationParams, CUSTOM)
    stats = process_map(run_strategy, params_list, outputsettings_list, max_workers=os.cpu_count())

    df = pd.DataFrame(stats)
    df.sort_values(sortKey, ascending=False, inplace=True)
    helper.gradientAppliedXLSX(df, "Optimization",
                               ["Kelly Percent", "Max DrawDown", "PnL Net", "SQN", "Sharpe Ratio", "VWR", "Strike Rate"])
    return df

# df = grid_search(sortKey = ["VWR"])
df= run_strategy()
