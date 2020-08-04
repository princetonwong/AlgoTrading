import pandas as pandas

from pandas_datareader import data

start_date = '2016-01-01'
end_date = '2020-06-01'
SRC_DATA_FILENAME = 'goog_data.pkl'

# try:
#   goog_data2 = pd.read_pickle(SRC_DATA_FILENAME)
# except FileNotFoundError:
goog_data2 = data3.DataReader('AAPL', 'yahoo', start_date, end_date)
goog_data2.to_pickle(SRC_DATA_FILENAME)

aapl_data = goog_data2.tail(620)

close = aapl_data['Close']

'''
The Absolute Price Oscillator (APO) is based
 on the absolute differences between two moving averages of different
 lengths, a ‘Fast’ and a ‘Slow’ moving average.

APO = Fast Exponential Moving Average - Slow Exponential Moving Average
'''
num_periods_fast = 10 # time period for the fast EMA
K_fast = 2 / (num_periods_fast + 1) # smoothing factor for fast EMA
ema_fast = 0
num_periods_slow = 40 # time period for slow EMA
K_slow = 2 / (num_periods_slow + 1) # smoothing factor for slow EMA
ema_slow = 0

ema_fast_values = [] # we will hold fast EMA values for visualization purposes
ema_slow_values = [] # we will hold slow EMA values for visualization purposes
apo_values = [] # track computed absolute price oscillator values
for close_price in close:
  if (ema_fast == 0): # first observation
    ema_fast = close_price
    ema_slow = close_price
  else:
    ema_fast = (close_price - ema_fast) * K_fast + ema_fast
    ema_slow = (close_price - ema_slow) * K_slow + ema_slow

  ema_fast_values.append(ema_fast)
  ema_slow_values.append(ema_slow)
  apo_values.append(ema_fast - ema_slow)

aapl_data = aapl_data.assign(ClosePrice=pandas.Series(close, index=aapl_data.index))
aapl_data = aapl_data.assign(FastExponential10DayMovingAverage=pandas.Series(ema_fast_values, index=aapl_data.index))
aapl_data = aapl_data.assign(SlowExponential40DayMovingAverage=pandas.Series(ema_slow_values, index=aapl_data.index))
aapl_data = aapl_data.assign(AbsolutePriceOscillator=pandas.Series(apo_values, index=aapl_data.index))

close_price = aapl_data['ClosePrice']
ema_f = aapl_data['FastExponential10DayMovingAverage']
ema_s = aapl_data['SlowExponential40DayMovingAverage']
apo = aapl_data['AbsolutePriceOscillator']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(211, ylabel='Google price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema_f.plot(ax=ax1, color='b', lw=2., legend=True)
ema_s.plot(ax=ax1, color='r', lw=2., legend=True)
ax2 = fig.add_subplot(212, ylabel='APO')
apo.plot(ax=ax2, color='black', lw=2., legend=True)
plt.show()

