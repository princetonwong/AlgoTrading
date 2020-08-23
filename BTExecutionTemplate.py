from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator, BTFilter
import copy
from typing import Dict, Union
from tqdm.contrib.concurrent import process_map

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_15M
# TIMERANGE = ("2019-01-01", "00:00:00", "2019-12-31", "23:59:00")
TIMERANGE = None

# SYMBOL = "AAPL"
# DATA0 = BTDataFeed.getHDFWikiPriceDataFeed([SYMBOL], startYear= "2015")

INITIALCASH = 50000
STRATEGY = BTStrategy.CCICrossStrategy
PARAMS={"period": 19, "hold": 8, }
helper = Helper()
OPTIMIZATION = None
FOLDERNAME = helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, PARAMS)

DATA0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)

def run_strategy(
        params: Dict[str, Union[float, int]] = {
            'period': 20,
            'hold': 5,
        }
):
    #Init
    cerebro = bt.Cerebro()
    cerebro.addwriter(bt.WriterFile, csv=True, out=Helper().generateFilePath("Data", ".csv"), rounding=2)
    cerebro.adddata(DATA0, name=SYMBOL)

    # data1 = copy.deepcopy(data0)
    # data1.plotinfo.plotmaster = data0
    # cerebro.adddata(data1, name="TRADE")

    #Data Filter
    # data1.addfilter(bt.filters.HeikinAshi(data1))

    #Sizer
    cerebro.addsizer(BTSizer.FixedSizer)

    #Broker
    cerebro.broker.setcash(INITIALCASH)
    cerebro.broker.setcommission(commission=10.6, margin=26000.0, mult=10.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #Strategy
    cerebro.addstrategy(STRATEGY,
                        period=params['period'],
                        hold=params['hold'],
                        )

    #Analyzer
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                        annualize=True, _name="sharperatio")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")

    cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
    # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
    # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=DATA0, _name='buyandhold')

    # Observers
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.DrawDownLength)

    #Run
    results = cerebro.run(stdstats=True)
    assert len(results) == 1
    finalPortfolioValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % finalPortfolioValue)

    #Bokeh Optimization
    # from backtrader_plotting import Bokeh, OptBrowser
    # from backtrader_plotting.schemes import Tradimo
    # b = Bokeh(style='bar', scheme=Tradimo())
    # browser = OptBrowser(b, results)
    # browser.start()

    # #Bokeh Plotting
    # from backtrader_plotting import Bokeh
    # from backtrader_plotting.schemes import Tradimo
    # b = Bokeh(filename=helper.generateFilePath("Report", ".html"), style='bar', plot_mode='single', scheme=Tradimo())
    # fig = cerebro.plot(b, iplot=False)

    # Plotting
    # figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1, show=False)
    # helper.saveFig(figs)

    #Analyzer methods
    strategy = results[0]
    taAnalyzer = strategy.analyzers.ta.get_analysis()
    sharpeRatioAnalyzer = strategy.analyzers.sharperatio.get_analysis()
    drawdownAnalyzer = strategy.analyzers.drawdown.get_analysis()
    sqnAnalyzer = strategy.analyzers.sqn.get_analysis()
    returnAnalyzer = strategy.analyzers.returns.get_analysis()

    taAnalyzerDF = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis())
    sqnDF = BTAnalyzer.getSQNDf(sqnAnalyzer)
    transactionsDF = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis())
    drawdownDF = BTAnalyzer.getDrawDownDf(drawdownAnalyzer)
    sharpeRatioDF = BTAnalyzer.getSharpeRatioDf(sharpeRatioAnalyzer)

    statsDF = pd.concat([taAnalyzerDF,
                         pd.Series([INITIALCASH, finalPortfolioValue], index=["Initial Cash", "Final Portfolio Value"]),
                         sqnDF,
                         sharpeRatioDF,
                         drawdownDF,
                         transactionsDF]
                        )

    helper.outputXLSX(statsDF, "Statistics")

    stats = {
        "Symbol": SYMBOL,
        "SubType": SUBTYPE,
        'Sharpe Ratio': sharpeRatioDF['Sharpe Ratio'],
        'CARG': returnAnalyzer['ravg'],
        'Max DrawDown': drawdownDF['Max DrawDown'],
        "Total Open" : taAnalyzerDF["Total Open"],
        "Total Closed" : taAnalyzerDF["Total Closed"],
        "Total Won" : taAnalyzerDF["Total Won"],
        "Total Lost" : taAnalyzerDF["Total Lost"],
        "Win Streak" : taAnalyzerDF["Win Streak"],
        "Lose Streak" : taAnalyzerDF["Losing Streak"],
        "PnL Net" : taAnalyzerDF["PnL Net"],
        "Strike Rate" : taAnalyzerDF["Strike Rate"],
        "SQN": sqnDF["SQN"]
    }

    return {**params, **stats}

def grid_search() -> pd.DataFrame:
    params_list = []

    for period in range(20, 27):
        for hold in range(6, 11):
            params = {
                'period': period,
                'hold': hold,
            }
            params_list.append(params)

    stats = process_map(run_strategy, params_list, max_workers=os.cpu_count())

    df = pd.DataFrame(stats)
    df.sort_values('Sharpe Ratio', ascending=False, inplace=True)
    return df

# df = grid_search()
# Helper().outputXLSX(df, "Optimized")

df= run_strategy(params=PARAMS)
