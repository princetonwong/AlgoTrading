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
FOLDERNAME = "{}-{} {} {}".format(SYMBOL, SUBTYPE, Helper().get_timestamp(),"CCI")

DATA0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE, FOLDERNAME)

def run_strategy(
        params: Dict[str, Union[float, int]] = {
            'period': 20,
            'hold': 5,
        }
):
    #Init
    cerebro = bt.Cerebro()
    cerebro.addwriter(bt.WriterFile, csv=True, out=Helper().getWriterOutputPath(FOLDERNAME), rounding=2)
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
    cerebro.addstrategy(BTStrategy.CCICrossStrategyWithSLOWKDExit,
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
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=DATA0, _name='buyandhold')

    #Run
    results = cerebro.run()
    assert len(results) == 1
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #Bokeh Optimization
    # from backtrader_plotting import Bokeh, OptBrowser
    # from backtrader_plotting.schemes import Tradimo
    # b = Bokeh(style='bar', scheme=Tradimo())
    # browser = OptBrowser(b, results)
    # browser.start()

    # Plotting
    figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1)
    Helper().saveFig(figs, FOLDERNAME)

    # #Bokeh Plotting
    from backtrader_plotting import Bokeh
    from backtrader_plotting.schemes import Tradimo
    b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    fig = cerebro.plot(b, iplot=False)

    #Analyzer methods
    strategy = results[0]
    df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), FOLDERNAME)
    df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), FOLDERNAME)
    df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), FOLDERNAME)
    df4 = BTAnalyzer.get(strategy.analyzers.drawdown.get_analysis(), FOLDERNAME)

    taAnalyzer = results[0].analyzers.ta.get_analysis()
    stats = {
        # 'PnL': list(results[0].analyzers.timereturn.get_analysis().values())[0],
        "Symbol": SYMBOL,
        "SubType": SUBTYPE,
        'BuyAndHold': list(results[0].analyzers.buyandhold.get_analysis().values())[0],
        'Sharpe Ratio': results[0].analyzers.sharperatio.get_analysis()['sharperatio'],
        'CARG': results[0].analyzers.returns.get_analysis()['ravg'],
        'Max Drawdown': results[0].analyzers.drawdown.get_analysis().max.drawdown / 100,
        "total Open" : taAnalyzer.total.open,
        "total Closed" : taAnalyzer.total.closed,
        "total Won" : taAnalyzer.won.total,
        "total Lost" : taAnalyzer.lost.total,
        "win Streak" : taAnalyzer.streak.won.longest,
        "lose Streak" : taAnalyzer.streak.lost.longest,
        "pnlNet" : round(taAnalyzer.pnl.net.total, 2),
        "strike Rate" : round(((taAnalyzer.won.total / taAnalyzer.total.closed) * 100), 2),
        "SQN": results[0].analyzers.sqn.get_analysis().sqn
    }

    # strategies = [x[0][0] for x in results]
    # for strategy in enumerate(strategies):
    #     df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), folderName)
    #     df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), folderName)
    #     df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), folderName)

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

    #     with ProgressBar(): # Backtrader is not compatible with Dask ???
    #         stats = db.from_sequence(params_list).map(run_strategy).compute()

    #     with multiprocessing.Pool(os.cpu_count()) as p:
    #         stats = p.map(run_strategy, params_list)
    stats = process_map(run_strategy, params_list, max_workers=os.cpu_count())

    df = pd.DataFrame(stats)
    df.sort_values('Sharpe Ratio', ascending=False, inplace=True)
    return df

# df = grid_search()
# Helper().outputXLSX(df, FOLDERNAME, "Optimized-{}.xlsx".format(SUBTYPE))

df= run_strategy(params={"period": 21, "hold": 7,})
