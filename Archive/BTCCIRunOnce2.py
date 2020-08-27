from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator
import copy
from typing import Dict, Union
from tqdm.contrib.concurrent import process_map

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_15M
# TIMERANGE = ("2020-04-01", "00:00:00", "2020-08-21", "23:59:00")
TIMERANGE = None

# SYMBOL = "AAPL"
# DATA0 = BTDataFeed.getHDFWikiPriceDataFeed([SYMBOL], startYear= "2015")

INITIALCASH = 50000

STRATEGY = BTStrategy.CCICrossStrategy
PARAMS={"period": 21, "hold": 7, }
helper = Helper()
FOLDERNAME = helper.initializeFolderName(SYMBOL, SUBTYPE, TIMERANGE, STRATEGY, PARAMS)

DATA0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)

def runStrategyOnce(plot=False, bokeh=False, analyzer=True,
        params: Dict[str, Union[float, int]] = {
            'period': 20,
            'hold': 5,
        }
):
    #Init
    cerebro = bt.Cerebro()
    cerebro.addwriter(bt.WriterFile, csv=True, out=helper.generateFilePath("Data", ".csv"), rounding=2)
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
    cerebro.addstrategy(STRATEGY, period=params['period'], hold=params['hold'])
    
    if analyzer:
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                            annualize=True, _name="sharperatio")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
        cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
        # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
        # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=DATA0, _name='buyandhold')
    
    #Observers
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.DrawDownLength)
    
    #Run
    results = cerebro.run(stdstats=True)
    assert len(results) == 1
    finalPortfolioValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % finalPortfolioValue)
    
    if bokeh:
        from backtrader_plotting import Bokeh
        from backtrader_plotting.schemes import Tradimo
        b = Bokeh(filename= helper.generateFilePath("Report", ".html"),style='bar', plot_mode='single', scheme=Tradimo())
        fig = cerebro.plot(b, iplot=False)
    
    if plot:
        figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1, show= False)
        helper.saveFig(figs=figs)
    
    if analyzer:
        strategy = results[0]
        taAnalyzer = strategy.analyzers.ta.get_analysis()
        sharpeRatioAnalyzer = strategy.analyzers.sharperatio.get_analysis()
        drawdownAnalyzer = strategy.analyzers.drawdown.get_analysis()
        sqnAnalyzer = strategy.analyzers.sqn.get_analysis()
        taAnalyzerDF = BTAnalyzer.getTradeAnalysisDf(taAnalyzer)
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

        stats = {
            # 'PnL': list(results[0].analyzers.timereturn.get_analysis().values())[0],
            "Symbol": SYMBOL,
            "SubType": SUBTYPE,
            # 'BuyAndHold': list(results[0].analyzers.buyandhold.get_analysis().values())[0],
            'Sharpe Ratio': results[0].analyzers.sharperatio.get_analysis()['sharperatio'],
            'CARG': results[0].analyzers.returns.get_analysis()['ravg'],
            'Max Drawdown': results[0].analyzers.drawdown.get_analysis().max.drawdown / 100,
            "total Open": taAnalyzer.total.open,
            "total Closed": taAnalyzer.total.closed,
            "total Won": taAnalyzer.won.total,
            "total Lost": taAnalyzer.lost.total,
            "win Streak": taAnalyzer.streak.won.longest,
            "lose Streak": taAnalyzer.streak.lost.longest,
            "pnlNet": round(taAnalyzer.pnl.net.total, 2),
            "strike Rate": round(((taAnalyzer.won.total / taAnalyzer.total.closed) * 100), 2),
            "SQN": results[0].analyzers.sqn.get_analysis().sqn
        }
        
        helper.outputXLSX(statsDF, "Analyzers")
        
    return {**params, **stats}


def gridSearch() -> pd.DataFrame:
    paramsList = []

    for period in range(20, 27):
        for hold in range(6, 11):
            params = {
                'period': period,
                'hold': hold,
            }
            paramsList.append(params)

    stats = process_map(runStrategyOnce, paramsList, max_workers=os.cpu_count())

    df = pd.DataFrame(stats)
    print (df.head())
    df.sort_values('Sharpe Ratio', ascending=False, inplace=True)
    return df

# df = runStrategyOnce(params=PARAMS, bokeh=True)
df = gridSearch()
helper.outputXLSX(df, "Optimized")