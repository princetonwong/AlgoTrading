import pandas as pd
from backtrader.utils.py3 import iteritems
from backtrader.utils import AutoOrderedDict
import backtrader as bt

from backtrader import TimeFrame
from backtrader.mathsupport import average, standarddev
from backtrader.analyzers import TimeReturn, AnnualReturn
import webbrowser

class _AnalyzerBase(bt.Analyzer):
    def getAnalyzerResultsDf(self):
        self.index = list()
        self.result = list()
        self.resultDF = pd.Series()

        return self.resultDF

    def updateResultDF(self):
        self.resultDF = pd.Series(self.result, index=self.index)

class Kelly(_AnalyzerBase):
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
        super().start()  # Call parent class start() method
        self.pnlWins = list()  # Create list to hold winning trades
        self.pnlLosses = list()  # Create list to hold losing trades

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
            if trade.pnlcomm >= 0:
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
                kellyPercent = 0  # Because average of winners were 0.

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
            kellyPercent = 0  # Not enough information to calculate.

        self.rets.kellyRatio = kellyPercent  # e.g. 0.215
        self.rets.kellyPercent = kellyPercent * 100  # e.g. 21.5

    def getAnalyzerResultsDf(self):
        super(Kelly, self).getAnalyzerResultsDf()
        kellyRatio = self.get_analysis().kellyRatio
        kellyPercent = round(self.get_analysis().kellyPercent, 2)
        self.index += ["Kelly Ratio", "Kelly Percent"]
        self.result += [kellyRatio, kellyPercent]

        self.updateResultDF()
        return self.resultDF

class SQN(_AnalyzerBase, bt.analyzers.SQN):

    def getAnalyzerResultsDf(self):
        super(SQN, self).getAnalyzerResultsDf()
        sqn = round(self.get_analysis().sqn, 2)
        self.index += ["SQN"]
        self.result += [sqn]

        print('SQN: {}'.format(sqn))

        self.updateResultDF()
        return self.resultDF

class SharpeRatio(_AnalyzerBase, bt.analyzers.SharpeRatio):
    params = dict(timeframe = bt.TimeFrame.Days,
                  compression = 1,
                  factor = 365,
                  annualize = True)

    def getAnalyzerResultsDf(self):
        super(SharpeRatio, self).getAnalyzerResultsDf()
        try:
            sharpeRatio = round(self.get_analysis()['sharperatio'], 2)
        except:
            sharpeRatio = 0
        self.index += ["Sharpe Ratio"]
        self.result += [sharpeRatio]

        print("Sharpe Ratio: {}".format(sharpeRatio))

        self.updateResultDF()
        return self.resultDF

class TradeAnalyzer(_AnalyzerBase, bt.analyzers.TradeAnalyzer):

    def getAnalyzerResultsDf(self):
        super(TradeAnalyzer, self).getAnalyzerResultsDf()
        try:
            total_open = self.get_analysis().total.open
            total_closed = self.get_analysis().total.closed
            total_won = self.get_analysis().won.total
            total_lost = self.get_analysis().lost.total
            win_streak = self.get_analysis().streak.won.longest
            lose_streak = self.get_analysis().streak.lost.longest
            pnl_net = round(self.get_analysis().pnl.net.total, 2)
            strike_rate = round(((total_won / total_closed) * 100), 2)
        except:
            total_open, total_closed, total_won, total_lost, strike_rate, win_streak, lose_streak, pnl_net = 0, 0, 0,0,0,0,0,0
        self.index += ['Total Open', 'Total Closed', 'Total Won', 'Total Lost', 'Strike Rate', 'Win Streak', 'Losing Streak',
                 'PnL Net']
        self.result += [total_open, total_closed, total_won, total_lost, strike_rate, win_streak, lose_streak, pnl_net]

        self.printTradeAnalysis(lose_streak, pnl_net, strike_rate, total_closed, total_lost, total_open, total_won,
                           win_streak)

        self.updateResultDF()
        return self.resultDF

    @staticmethod
    def printTradeAnalysis(lose_streak, pnl_net, strike_rate, total_closed, total_lost, total_open, total_won,
                           win_streak):
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



class VWR(_AnalyzerBase, bt.analyzers.VWR):

    def getAnalyzerResultsDf(self):
        super(VWR, self).getAnalyzerResultsDf()
        vwr = round(self.get_analysis()["vwr"], 2)
        self.index += ["VWR"]
        self.result += [vwr]

        print('VWR: {}'.format(vwr))

        self.updateResultDF()
        return self.resultDF

class DrawDown(_AnalyzerBase, bt.analyzers.DrawDown):

    def getAnalyzerResultsDf(self):
        super(DrawDown, self).getAnalyzerResultsDf()
        maxDrawDown = round(self.get_analysis().max.drawdown, 2)
        self.index += ["Max DrawDown"]
        self.result += [maxDrawDown]

        print ("Max Drawdown: {}%".format(maxDrawDown))

        self.updateResultDF()
        return self.resultDF

class Returns(_AnalyzerBase, bt.analyzers.Returns):

    def getAnalyzerResultsDf(self):
        super(Returns, self).getAnalyzerResultsDf()
        rtot = round(self.get_analysis()["rtot"], 3)
        ravg = round(self.get_analysis()["ravg"], 3)
        rnorm = round(self.get_analysis()["rnorm"], 3)
        rnorm100 = round(self.get_analysis()["rnorm100"], 3)
        self.index += ["Total Compound Return", "Average Return", "Annualized Return", "Annualized Return%"]
        self.result += [rtot, ravg, rnorm, rnorm100]

        print("Total Compound Return: {}%".format(rtot * 100))
        print("Annualized Return%: {}%".format(rnorm100))

        self.updateResultDF()
        return self.resultDF


class TimeReturn(_AnalyzerBase, bt.analyzers.TimeReturn):
    params = (
        ('data', None),
        ('firstopen', True),
        ('fund', None),
        ('timeframe', TimeFrame.Minutes)
    )

    def getAnalyzerResultsDf(self):
        super(TimeReturn, self).getAnalyzerResultsDf()
        for date, value in self.get_analysis().items():
            self.index.append(date)
            self.result.append(value)

        self.updateResultDF()
        return self.resultDF

class Transactions(_AnalyzerBase, bt.analyzers.Transactions):

    def getAnalyzerResultsDf(self):
        super(Transactions, self).getAnalyzerResultsDf()
        txs = list()
        for key, v in iteritems(self.get_analysis()):
            for v2 in v:
                txs.append([key] + v2)

        self.index = ['date', 'amount', 'price', 'sid', 'symbol', 'value']
        self.resultDF = pd.DataFrame(txs, columns=self.index)

        return self.resultDF


def getQuantStatsReport(helper, timeReturnDF): #TODO: Fix
    import quantstats as qs
    qs.extend_pandas()
    # stock = qs.utils.download_returns('FB')
    # stock.to_csv("fb.csv")
    qs.stats.sharpe(timeReturnDF)
    # qs.plots.snapshot(df, title='Performance')
    path = helper.generateFilePath("QSReport", ".html")
    qs.reports.html(timeReturnDF, output= path)
    webbrowser.open("file://" + path)

