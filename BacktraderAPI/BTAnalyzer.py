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

def getReturnDf(analyzer, xlsx=False):
    rtot = round(analyzer["rtot"], 2)
    ravg = round(analyzer["ravg"], 2)
    rnorm = round(analyzer["rnorm"], 2)
    rnorm100 = round(analyzer["rnorm100"], 2)
    index = ["Total Compound Return", "Average Return", "Annualized Return", "Annualized Return%"]
    result = [rtot, ravg, rnorm, rnorm100]
    resultDF = pd.Series(result, index=index)

    print ("Total Compound Return: {}%".format(rtot * 100))
    print("Annualized Return%: {}%".format(rnorm100))

    if xlsx:
        Helper().outputXLSX(resultDF, fileName="Returns")

    return resultDF

from backtrader import Analyzer
from backtrader.mathsupport import average
from backtrader.utils import AutoOrderedDict


class Kelly(Analyzer):
    '''Kelly formula was described in 1956 by J. L. Kelly, working at Bell Labs.
    It is used to determine the optimal size of a series of bets (or trades).
    The optimal size is given as a percentage of the account value.
    Caution: Kellys works optimally for systems that do not change over time.
    Such as mechanical systems e.g. tossing a coin, rolling a dice or a spin
    of a roulette wheel.
    Trading systems are not fixed, and may work for a period and then stop
    working due to market conditions changing.
    Continuing to use Kelly's optimal percent to bet with as a system stops
    working, will incur heavy losses. I'm speaking from personal experience! :)
    LESSON: Kelly percent is optimal providing your system edge remains
    working. The catch is, assume no system edge remains forever. Prepare for
    your system to stop working over time. Markets change.
    I personally find Kellys a useful measure for comparing systems.
    The formula:
        K = W - [(1 - W) / R]
    K = Kelly optimal percent
    e.g. 0.156 = 15.6 percent of account is the optimal bet size
    (based on the historical trades your system generated).
    W = Win rate
    e.g. 0.6 (= 60%)
    Determined by percentage of profitable trades.
    R = Win/Loss ratio
    e.g. 1.5 = Winners were on average 1.5 x losers
    Determined by taking average of all winners and dividing by average of all
    losing trades.
    Because R and W are determined from all trades the strategy generates when
    run, there needs to be at least 1 winner and 1 loser. Otherwise 'None'
    is returned.
    Note: A negative Kelly percent e.g. -1.16 or -0.08, means the strategy lost
    money. The sign is important here. The actual value does not give any useful
    information as far as I can see.
    Methods:
      - get_analysis
        Returns a dictionary with keys "kellyPercent" and "kellyRatio"
        "kellyPercent" is expressed as a percentage e.g. 11.6 = 11.6%
        "kellyRatio" is expressed as a ratio e.g. 0.116 is equivalent to 11.6%
    [This 'kelly.py' module was coded by Richard O'Regan (UK) September 2017.]
    '''


    def create_analysis(self):
        '''Replace default implementation to instantiate an AutoOrdereDict
        rather than an OrderedDict'''
        self.rets = AutoOrderedDict()

    def start(self):
        super().start()   # Call parent class start() method
        self.pnlWins = list()       # Create list to hold winning trades
        self.pnlLosses = list()     # Create list to hold losing trades

    def notify_trade(self, trade):
        if trade.status == trade.Closed:  # i.e. trade had both an entry & exit
        # Note: for trades that scratch (=breakeven), i.e. a trade has exactly
        # 0.0 points profits. Should they be classed as a winner or loser?
        # Or perhaps create a seperate category for 'breakeven'?

        # On balance it probably doesn't make much difference.
        # If we class as a win, the win percent will increase but the average
        # win will decrease, i.e. maths balances out. Vice versa with losers.

        # I notice Backtrader defaults to trades of 0.0 or greater are
        # classed as winners. [Used in modules such as 'tradeanalyzer.py']

        # Likewise I will choose to class trades >=0 as winners.

            # Trades >=0 classed as profitable
            if trade.pnlcomm >=0:
                # Trade made money -> add to win list
                self.pnlWins.append(trade.pnlcomm)
            else:
                # Trade lost money -> add to losses list
                self.pnlLosses.append(trade.pnlcomm)


    def stop(self):
        # There must be at least one winning trade and one losing trade to
        # Calculate Kelly percent. Else get a division by zero error.
        if len(self.pnlWins) > 0 and len(self.pnlLosses) > 0:

            # Calculate average wins and losses
            avgWins = average(self.pnlWins)
            avgLosses = abs(average(self.pnlLosses))  # Remove the -ve sign
            winLossRatio = avgWins / avgLosses

            # Check winLoss ratio not 0 else division by zero later because
            # otherwise a rare bug can occur if all winners have value of 0.
            # (Since BT convention is to class trades with profit >=0 as a
            # winner)
            if winLossRatio == 0:
                kellyPercent = None   # Because average of winners were 0.

            else:
                # Calculate probability of winning from our data.
                # Number of wins divide by number of trades.
                numberOfWins = len(self.pnlWins)
                numberOfLosses = len(self.pnlLosses)
                numberOfTrades = numberOfWins + numberOfLosses
                winProb = numberOfWins / numberOfTrades
                inverse_winProb = 1 - winProb

                # Now calculate Kelly percentage
                # i.e. optimal percent of account to risk on each trade.
                kellyPercent = winProb - (inverse_winProb / winLossRatio)

        else:
            kellyPercent = None  # Not enough information to calculate.

        self.rets.kellyRatio = kellyPercent             # e.g. 0.215
        self.rets.kellyPercent = kellyPercent * 100     # e.g. 21.5