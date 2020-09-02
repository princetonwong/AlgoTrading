import pandas as pd
import numpy as np
from CustomAPI.Helper import Helper
from heatmap import heatmap, corrplot
import pandas as pd
from matplotlib import pyplot as plt
from pylab import rcParams
import seaborn as sns
import numpy as np
sns.set(color_codes=True, font_scale=1.2)
rcParams['figure.figsize'] = 10,10

STRATEGYColumns = ["cci", "squeezePerc"]
CSVPATH = "/Users/princetonwong/PycharmProjects/AlgoTrading/Output/HK.MHImain-K_30M [09-02 22-03] CMOCrossStrategyWithSqueezePercCCI /BackTraderData-HK.MHImain-K_30M [09-02 22-03] CMOCrossStrategyWithSqueezePercCCI .csv"


def getOrders(csvpath = CSVPATH, output = False):
    orders = pd.read_csv(csvpath, header=1, na_values=0).fillna(0)
    BASICColumns = ["close", "pnlplus", "pnlminus", "buy", "sell"]
    orders["pnl"] = orders["pnlplus"] + orders["pnlminus"]
    orders["buysell"] = orders["buy"] - orders["sell"]
    ORDERColumns = ["close", "pnl", "buysell"] + STRATEGYColumns
    orders = orders[ORDERColumns]
    orders = orders[orders["close"] > 0]

    if output:
        Helper().gradientAppliedXLSX(orders, fileName="Orders", subset=ORDERColumns)

    return orders

def getEntryExit(orders, output = False):
    entryexit = orders[orders["buysell"] != 0]
    entry = entryexit[np.arange(len(entryexit)) % 2 == 0]
    entry = entry.add_prefix("entry.")
    exit = entryexit[np.arange(len(entryexit)) % 2 == 1]
    exit = exit.add_prefix("exit.")
    entryexit = pd.concat([entry, exit], axis=1)
    entryexit[exit.columns] = entryexit[exit.columns].shift(-1)
    entryexit = entryexit[entryexit["entry.pnl"] == 0].drop(columns=["entry.pnl"])

    if output:
        Helper().gradientAppliedXLSX(entryexit, fileName="EntryExit", subset=entryexit.columns)

    return entryexit

def plotCorrelogram(df):
    corr = df.corr()
    ax = sns.heatmap(corr,vmin=-1, vmax=1, center=0,cmap=sns.diverging_palette(20, 220, n=200),square=True)
    ax.set_xticklabels(ax.get_xticklabels(),rotation=45,horizontalalignment='right')
    plt.show()

def plotScatterMatrix(df, selectedColumns = None):
    if selectedColumns:
        pd.plotting.scatter_matrix(df[selectedColumns])
    else:
        pd.plotting.scatter_matrix(df)

    plt.show()

orders = getOrders()
# orders["cci"] = abs(orders["cci"])
# orders["ash"] = abs(orders["ash"])
entryexit = getEntryExit(orders, output= True)
plotCorrelogram(entryexit)
plotScatterMatrix(entryexit)







