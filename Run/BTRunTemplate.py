from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator
import copy
from typing import Dict, Union
from tqdm.contrib.concurrent import process_map

helper = Helper()
SYMBOL = "BAC"
SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_15M
TIMERANGE = ("2018-03-29", "00:00:00", "2020-08-25", "23:59:00") #TODO: Create CSV Writer to store Stock Info
TIMERANGE = None
# DATA0 = BTDataFeed.getHDFWikiPriceDataFeed([SYMBOL], startYear= "2016")

INITIALCASH = 60000
OUTPUTSETTINGS = dict(bokeh=True,plot=False,observer=True,analyzer=True, optimization=False)

STRATEGY = BTStrategy.TTFStrategy
PARAMS = dict(lookback=19, upperband=100, lowerband=-100)
# PARAMS = dict()

FOLDERNAME = helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, PARAMS)
DATA0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)

def run_strategy(params= {**PARAMS}, outputsettings={**OUTPUTSETTINGS}) -> pd.DataFrame:
    print (params)
    if outputsettings["optimization"] is False:
        helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, PARAMS)

    #Init
    cerebro = bt.Cerebro()
    cerebro.adddata(DATA0, name=SYMBOL)

    if outputsettings["optimization"] is False:
        cerebro.addwriter(bt.WriterFile, csv=True, out=helper.generateFilePath("BackTraderData", ".csv"), rounding=3)
    else:
        cerebro.addwriter(bt.WriterFile, rounding=3)

    #Multi-data feeds
    # data1 = copy.deepcopy(data0)
    # data1.plotinfo.plotmaster = data0
    # cerebro.adddata(data1, name="TRADE")

    #Data Filter
    # DATA0.addfilter(bt.filters.HeikinAshi(DATA0))

    #Sizer
    cerebro.addsizer(BTSizer.FixedSizer)

    #Broker
    cerebro.broker.setcash(INITIALCASH)
    cerebro.broker.setcommission(commission=10.6, margin=26000.0, mult=10.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #Strategy
    cerebro.addstrategy(STRATEGY, **params)
    # cerebro.addindicator(BTIndicator.KeltnerChannel)
    # cerebro.addindicator(BTIndicator.KeltnerChannelBBSqueeze)
    # cerebro.addindicator(BTIndicator.VolumeWeightedAveragePrice)

    #Analyzer
    if outputsettings["analyzer"]:
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                            annualize=True, _name="sharperatio")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
        cerebro.addanalyzer(bt.analyzers.VWR, _name="vwr")
        cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
        cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
        cerebro.addanalyzer(BTAnalyzer.Kelly, _name="kelly")

    if outputsettings["observer"]:
        cerebro.addobserver(bt.observers.DrawDown)
        cerebro.addobserver(bt.observers.Trades)
        cerebro.addobserver(bt.observers.Broker)
        cerebro.addobserver(bt.observers.BuySell, barplot= True, bardist= 0.01)

    #Run
    results = cerebro.run(stdstats=False)
    assert len(results) == 1
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

        taAnalyzerDF = BTAnalyzer.getTradeAnalysisDf(taAnalyzer)
        sqnDF = BTAnalyzer.getSQNDf(sqnAnalyzer)
        drawdownDF = BTAnalyzer.getDrawDownDf(drawdownAnalyzer)
        sharpeRatioDF = BTAnalyzer.getSharpeRatioDf(sharpeRatioAnalyzer)
        vwrDF = BTAnalyzer.getVWRDf(vwrAnalyzer)
        returnDF = BTAnalyzer.getReturnDf(returnAnalyzer)
        cashDF = pd.Series([INITIALCASH, finalPortfolioValue], index=["Initial Cash", "Final Portfolio Value"])
        kellyDF = pd.Series([strategy.analyzers.kelly.get_analysis().kellyPercent], index=["Kelly Percent"])
        transactionsDF = BTAnalyzer.getTransactionsDf(transactionsAnalyzer)

        statsDF = pd.concat([taAnalyzerDF,
                             cashDF,
                             returnDF,
                             sqnDF,
                             sharpeRatioDF,
                             vwrDF,
                             drawdownDF,
                             kellyDF
                             ])

        if outputsettings["optimization"] is False:
            helper.outputXLSX(statsDF, "Statistics")
            helper.outputXLSX(transactionsDF, "Transactions")

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

def grid_search(sortKey: str) -> pd.DataFrame:
    global optimizationParams
    params_list = []
    outputsettings_list = []

    for x in range(5, 30, 1):
        y=100
        outputsettings = dict(bokeh=False,plot=False,observer=True,analyzer=True, optimization=True)
        optimizationParams = dict(lookback=x, upperband=y, lowerband=-y)

        params_list.append({**optimizationParams})
        outputsettings_list.append({**outputsettings})

    helper.folderName = "[Opt]" + helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, optimizationParams)
    stats = process_map(run_strategy, params_list, outputsettings_list, max_workers=os.cpu_count())

    df = pd.DataFrame(stats)
    df.sort_values(sortKey, ascending=False, inplace=True)
    helper.gradientAppliedXLSX(df, "Optimization",
                               ["Kelly Percent", "Max DrawDown", "PnL Net", "SQN", "Sharpe Ratio", "VWR"])
    return df

# df = grid_search(sortKey = ["VWR"])
df= run_strategy()
