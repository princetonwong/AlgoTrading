from futu import *
import backtrader as bt
from CustomAPI.Helper import Helper
from BacktraderAPI import BTStrategy, BTDataFeed, BTAnalyzer, BTSizer, BTIndicator
import copy
from typing import Dict, Union

SYMBOL = "HK.MHImain"
SUBTYPE = SubType.K_30M
CCIPARAMETERS = (26, 0.015, 100 ,5)
TIMERANGE = ("2020-01-01", "00:00:00", "2020-08-20", "23:59:00")
# TIMERANGE = None
DATA0 = BTDataFeed.getFutuDataFeed(SYMBOL, SUBTYPE, TIMERANGE)

# SYMBOL = "AAPL"
# DATA0 = BTDataFeed.getHDFWikiPriceDataFeed([SYMBOL], startYear= "2015")

INITIALCASH = 50000
FOLDERNAME = "{}-{}-{}-{}".format(SYMBOL, SUBTYPE, Helper().get_timestamp(),"Donchian")



def run_strategy(
        params: Dict[str, Union[float, int]] = {
            'trend_filter_fast_period': 50,
            'trend_filter_slow_period': 100,
            'fast_donchian_channel_period': 25,
            'slow_donchian_channel_period': 50,
            'trailing_stop_atr_period': 100,
            'trailing_stop_atr_count': 3,
            'risk_factor': 0.002
        }
):
    """
    https://github.com/soulmachine/crypto-notebooks/blob/master/backtest/Clenow-trend-following.ipynb
    """

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
    # cerebro.broker.setcommission(commission=0)
    cerebro.broker.setcommission(commission=10.6, margin=26000.0, mult=10.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #Strategy
    cerebro.addstrategy(BTStrategy.ClenowTrendFollowingStrategy,
                        trend_filter_fast_period=params['trend_filter_fast_period'],
                        trend_filter_slow_period=params['trend_filter_slow_period'],
                        fast_donchian_channel_period=params['fast_donchian_channel_period'],
                        slow_donchian_channel_period=params['slow_donchian_channel_period'],
                        trailing_stop_atr_period=params['trailing_stop_atr_period'],
                        trailing_stop_atr_count=params['trailing_stop_atr_count'],
                        risk_factor=params['risk_factor'])
    # cerebro.optstrategy(BTStrategy.CCICrossStrategy, hold= range(5,10))

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
    # figs = cerebro.plot(style = "candle", iplot= False, subtxtsize = 6, maxcpus=1)
    # Helper().saveFig(figs, FOLDERNAME)

    # #Bokeh Plotting
    # from backtrader_plotting import Bokeh
    # from backtrader_plotting.schemes import Tradimo
    # b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    # fig = cerebro.plot(b, iplot=False)

    #Analyzer methods
    # strategy = results[0]
    # df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), FOLDERNAME)
    # df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), FOLDERNAME)
    # df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), FOLDERNAME)
    # df4 = BTAnalyzer.get(strategy.analyzers.drawdown.get_analysis(), FOLDERNAME)

    stats = {
        # 'PnL': list(results[0].analyzers.timereturn.get_analysis().values())[0],
        'PnL': cerebro.broker.getvalue() / INITIALCASH - 1,
        'BnH': list(results[0].analyzers.buyandhold.get_analysis().values())[0],
        'Sharpe_Ratio': results[0].analyzers.sharperatio.get_analysis()['sharperatio'],
        'CARG': results[0].analyzers.returns.get_analysis()['ravg'],
        'Max_Drawdown': results[0].analyzers.drawdown.get_analysis().max.drawdown / 100,
        'num_trades': results[0].analyzers.ta.get_analysis().total.total,
    }

    # strategies = [x[0][0] for x in results]
    # for strategy in enumerate(strategies):
    #     df = BTAnalyzer.getTradeAnalysisDf(strategy.analyzers.ta.get_analysis(), folderName)
    #     df2 = BTAnalyzer.getSQNDf(strategy.analyzers.sqn.get_analysis(), folderName)
    #     df3 = BTAnalyzer.getTransactionsDf(strategy.analyzers.transactions.get_analysis(), folderName)

    return {**params, **stats}


def grid_search() -> pd.DataFrame:
    params_list = []

    for fast_donchian_channel_period in range(30, 40):
        for m1 in range(2, 5):
            for m2 in range(2, 5):
                for atr_count in range(3, 6):
                    params = {
                        'trend_filter_fast_period': fast_donchian_channel_period * m1,
                        'trend_filter_slow_period': fast_donchian_channel_period * m1 * m2,
                        'fast_donchian_channel_period': fast_donchian_channel_period,
                        'slow_donchian_channel_period': fast_donchian_channel_period * m1,
                        'trailing_stop_atr_period': fast_donchian_channel_period * m1 * m2,
                        'trailing_stop_atr_count': atr_count,
                        'risk_factor': 0.002
                    }
                    params_list.append(params)

    #     with ProgressBar(): # Backtrader is not compatible with Dask ???
    #         stats = db.from_sequence(params_list).map(run_strategy).compute()

    #     with multiprocessing.Pool(os.cpu_count()) as p:
    #         stats = p.map(run_strategy, params_list)
    from tqdm.contrib.concurrent import process_map
    stats = process_map(run_strategy, params_list, max_workers=os.cpu_count())

    df = pd.DataFrame(stats)
    df.sort_values('Sharpe_Ratio', ascending=False, inplace=True)
    return df

df = grid_search()
Helper().outputXLSX(df, "Optimized")
