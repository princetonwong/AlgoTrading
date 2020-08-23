import pandas as pd
from CustomAPI.Helper import Helper
from backtrader.utils.py3 import iteritems

def getVWRDf(analyzer, xlsx=False):

    '''
    https://www.crystalbull.com/sharpe-ratio-better-with-log-returns/
    '''

    vwr = round(analyzer["vwr"], 2)
    index = ['VWR']
    result = [vwr]
    resultDF = pd.Series(result, index=index)

    print('VWR: {}'.format(vwr))

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="VWR")

    return resultDF

def getTransactionsDf(analyzer, xlsx= False):
    txss = analyzer
    txs = list()
    for key, v in iteritems(txss):
        for v2 in v:
            txs.append([key] + v2)

    index = ['date', 'amount', 'price', 'sid', 'symbol', 'value']
    resultDF = pd.DataFrame(txs, columns= index)

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="Transactions")

    return resultDF

def getTradeAnalysisDf(analyzer, xlsx=False):
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = round(((total_won / total_closed) * 100),2)
    index = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost', 'Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    result = [total_open, total_closed, total_won, total_lost, strike_rate, win_streak, lose_streak, pnl_net]
    resultDF = pd.Series(result, index= index)

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="TradeAnalysis")

    # Print method
    # Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    # Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    # Print the rows
    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('', *row))

    return resultDF

def getSQNDf(analyzer, xlsx= False):
    '''
    SQN or SystemQualityNumber. Defined by Van K. Tharp to categorize trading systems.
    1.6 - 1.9 Below average
    2.0 - 2.4 Average
    2.5 - 2.9 Good
    3.0 - 5.0 Excellent
    5.1 - 6.9 Superb
    7.0 - Holy Grail?
    '''
    sqn = round(analyzer.sqn,2)
    index = ['SQN']
    result = [sqn]
    resultDF = pd.Series(result, index= index)

    print('SQN: {}'.format(sqn))

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="SQN")

    return resultDF

def getDrawDownDf(analyzer, xlsx= False):
    maxDrawDown = round(analyzer.max.drawdown, 2)
    index = ["Max DrawDown"]
    result = [maxDrawDown]
    resultDF = pd.Series(result, index=index)

    print ("Max Drawdown: {}".format(maxDrawDown))

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="Drawdown")

    return resultDF


def getSharpeRatioDf(analyzer, xlsx= False):
    sharpeRatio = round(analyzer["sharperatio"], 2)
    index = ["Sharpe Ratio"]
    result = [sharpeRatio]
    resultDF = pd.Series(result, index=index)

    print("Sharpe Ratio: {}".format(sharpeRatio))

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="SharpeRatio")

    return resultDF