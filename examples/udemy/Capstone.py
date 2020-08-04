import pandas
import numpy
import matplotlib.pyplot as plt
import pandas_datareader.data as dr

startDate = "2012-01-01"
endDate = "2017-01-01"
dataSource = "yahoo"

tesla = dr.DataReader("TSLA", dataSource, startDate, endDate)
ford = dr.DataReader("F", dataSource, startDate, endDate)
gm = dr.DataReader("GM", dataSource, startDate, endDate)

allData = [tesla, ford, gm]
# TSLAData = pandas.read_csv("Tesla_Stock.csv")
# FORDData = pandas.read_csv("Ford_Stock.csv")
# GMData = pandas.read_csv("GM_Stock.csv")


for data2 in allData:
    dates = pandas.DatetimeIndex(data2.index)
    data2["Date"] = dates
    data2["Total Traded"] = data2["Open"] * data2["Volume"]

lineWidth = 1.0


def plot(yVariable, title):
    figure = plt.figure(figsize=(16, 8), dpi=100)
    axes = figure.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.plot(tesla[yVariable], label="Tesla")
    axes.plot(ford[yVariable], label="Ford")
    axes.plot(gm[yVariable], label="GM")
    axes.set_xlabel("Date")
    axes.set_title(title)
    plt.legend()
# axes.plot_date(dates, TSLAData["Open"], label= "Tesla", linewidth = lineWidth)
# axes.plot_date(dates, FORDData["Open"], label= "Ford", linewidth = lineWidth)
# axes.plot_date(dates, GMData["Open"], label= "GM", linewidth = lineWidth)

# plot(yVariable= "Open", title= "Open Price")
# plt.show()
# plot(yVariable= "Volume", title= "Volume")
# plt.show()

print(ford["Date"][ford["Volume"].argmax()])
# plot(yVariable= "Total Traded", title= "Volume")
# plt.show()

print(tesla["Date"][tesla["Total Traded"].argmax()])

# import talib
# TSLAData["MA50"] = talib.SMA(TSLAData["Open"], timeperiod = 50)
# TSLAData["MA200"] = talib.SMA(TSLAData["Open"], timeperiod = 200)
# TSLAData[["MA200", "MA50", "Open"]].plot(figsize = (16,8))
# plt.show()
#
# from pandas.plotting import scatter_matrix
# car_comp = pandas.concat([TSLAData['Open'],GMData['Open'],FORDData['Open']],axis=1)
# car_comp.columns = ['Tesla Open','GM Open','Ford Open']
# scatter_matrix(car_comp,figsize=(8,8),alpha=0.2,hist_kwds={'bins':50})
# plt.show()


# 
import mplfinance
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY

# Rest the index to get a column of January Dates
ford_reset = ford.loc['2012-01':'2012-01']

# Create a new column of numerical "date" values for matplotlib to use
# ford_reset['date_ax'] = ford_reset['Date'].apply(lambda date: date2num(date))
# ford_values = [tuple(vals) for vals in ford_reset[['date_ax', 'Open', 'High', 'Low', 'Close']].values]
#
# mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
# alldays = DayLocator()              # minor ticks on the days
# weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
# dayFormatter = DateFormatter('%d')      # e.g., 12
#
# #Plot it
# fig, ax = plt.subplots()
# fig.subplots_adjust(bottom=0.2)
# ax.xaxis.set_major_locator(mondays)
# ax.xaxis.set_minor_locator(alldays)
# ax.xaxis.set_major_formatter(weekFormatter)

# mplfinance.plot(ford_reset, type= "candle")
# plt.show()

# tesla['returns'] = (tesla['Close'] / tesla['Close'].shift(1) ) - 1
tesla['returns'] = tesla['Close'].pct_change(1)
ford['returns'] = ford['Close'].pct_change(1)
gm['returns'] = gm['Close'].pct_change(1)


ford['returns'].hist(bins=50, alpha= 0.2, label="Ford")
gm['returns'].hist(bins=50, alpha= 0.2, label="GM")
tesla['returns'].hist(bins=50, alpha= 0.2, label="Tesla")
plt.legend()
plt.show()