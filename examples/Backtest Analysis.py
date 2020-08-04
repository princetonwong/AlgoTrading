# Import a few libraries we need
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol,      schedule_function, date_rules, time_rules
from datetime import datetime
import pytz
import pyfolio as pf

# Parameters
BUY_AMOUNT = 1
short_periods = 5
long_periods = 35
PRICE = 4000

def MACD(asset, data):
    short_data = data.history(asset, 'price', bar_count=short_periods, frequency="1m")
    print(short_data)

    short_ema = pd.Series.ewm(short_data, span=short_periods).mean().iloc[-1]
    print(short_ema)

    long_data = data.history(asset, 'price', bar_count=long_periods, frequency="1m")
    long_ema = pd.Series.ewm(long_data, span=long_periods).mean().iloc[-1]

    macd = short_ema - long_ema
    macd_5 = pd.Series.ewm(macd, span=5).mean()
    print("MACD_5: " + macd_5)

    return macd_5, data

def initialize(context):
    # top5 = AverageDollarVolume(window_length=20).top(5)
    # context.pipe = Pipeline({'close': USEquityPricing.close.latest}, screen=top5)
    # context.attach_pipeline(context.pipe, "pipe")

    context.asset = symbol('AAPL')
    
    # Schedule the daily trading routine for once per month
    schedule_function(handle_data, date_rules.every_day(), time_rules.every_minute())
    
def handle_data(context, data):
    # for asset in context.portfolio.positions:
        asset = context.asset
        macd = MACD(asset, data)

        if macd < -0.1:
            # order_id = futuAPI.placeUSOrder(price= 0, quantity= BUY_AMOUNT, code= "US." + asset.symbol,
            #                         tradeSide= TrdSide.SELL, orderType= OrderType.NORMAL)
            order_target_percent(asset, target=0)

            # if order_id[0] != -1:
            #     log.info("MACD: " + str(macd))
            #     log.info(order_id[1])
            #     log.info("Closed position for {}".format(asset.symbol))

    # for asset in context.output.index:
    #     macd = MACD(asset, data)

        if macd > 0.1:
            # order_id = futuAPI.placeUSOrder(price= PRICE, quantity=BUY_AMOUNT, code="US." + asset.symbol,
            #                         tradeSide=TrdSide.BUY, orderType=OrderType.NORMAL)
            order_target_percent(asset, target= 0.1)

            # if order_id[0] != -1:
            #     log.info("MACD: " + str(macd))
            #     log.info(order_id[1])
            #     log.info("Bought {} shares of {}".format(BUY_AMOUNT, asset.symbol))
            
def analyze(context, perf):
    # Use PyFolio to generate a performance report
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
    pf.create_returns_tear_sheet(returns, benchmark_rets=None)
    

# Set start and end date
start = datetime(2017, 12, 25, tzinfo=pytz.UTC)
end = datetime(2017, 12, 31, tzinfo=pytz.UTC)

# Fire off the backtest
result = run_algorithm(
    start=start, 
    end=end, 
    initialize=initialize, 
    analyze=analyze, 
    capital_base=10000, 
    data_frequency = 'minute',
    bundle='quandl' 
)


# In[9]:


# Checking what columns are in the results dataframe
for column in result:
    print(column)


# In[16]:


# Inspecting the first days' exposure
result.gross_leverage.head()


# In[17]:


# Get the backtest data for a particular day
result.loc['2010-11-17']


# In[21]:


# Let's get a portfolio snapshot
# Import pandas and matplotlib
import pandas as pd
import matplotlib.pyplot as plt

# Select day to view
day = '2009-03-17'

# Get portfolio value and positions for this day
port_value = result.loc[day,'portfolio_value']
day_positions = result.loc[day,'positions']

# Empty DataFrame to store values
df = pd.DataFrame(columns=['value', 'pnl'])

# Populate DataFrame with position info
for pos in day_positions:
    ticker = pos['sid'].symbol 
    df.loc[ticker,'value'] = pos['amount'] * pos['last_sale_price']
    df.loc[ticker,'pnl'] = df.loc[ticker,'value'] - (pos['amount'] * pos['cost_basis'])
    
# Add cash position
df.loc['cash', ['value','pnl']] = [(port_value - df['value'].sum()), 0]    

# Make pie chart for allocations
fig, ax1 = plt.subplots(figsize=[12, 10])
ax1.pie(df['value'], labels=df.index, shadow=True, startangle=90)
ax1.axis('equal')
ax1.set_title('Allocation on {}'.format(day))
plt.show()

# Make bar chart for open PnL
fig, ax1 = plt.subplots(figsize=[12, 10])
pnl_df = df.drop('cash')
ax1.barh( pnl_df.index, pnl_df['pnl'],  align='center', color='green', ecolor='black')
ax1.set_title('Open PnL on {}'.format(day))
plt.show()


# In[37]:


df.loc[df['gross_leverage'] > 1.02, 'gross_leverage'] =1.01


# In[41]:


# Custom Time Series Analysis

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt, rc, ticker

# Format for book image
font = {'family' : 'eurostile',
        'weight' : 'normal',
        'size'   : 16}
rc('font', **font)

# Settings
calc_window = 126
year_length = 252

# Copy the columns we need
df = result.copy().filter(items=['portfolio_value', 'gross_leverage'])

# Function for annualized return
def ann_ret(ts):
    return np.power((ts[-1] / ts[0]), (year_length/len(ts))) -1  

# Function for drawdown
def dd(ts):
    return np.min(ts / np.maximum.accumulate(ts)) - 1

# Get a rolling window
rolling_window = result.portfolio_value.rolling(calc_window)

# Calculate rolling analytics
df['annualized'] = rolling_window.apply(ann_ret)
df['drawdown'] = rolling_window.apply(dd)

# Drop initial n/a values
df.dropna(inplace=True)

# Make a figure
fig = plt.figure(figsize=(12, 12))

# Make the base lower, just to make the graph easier to read
df['portfolio_value'] /= 100

# First chart
ax = fig.add_subplot(411)
ax.set_title('Strategy Results')
ax.plot(df['portfolio_value'], 
        linestyle='-', 
        color='black',
        label='Equity Curve', linewidth=3.0)

# Set log scale
ax.set_yscale('log') 

# Make the axis look nicer
ax.yaxis.set_ticks(np.arange(df['portfolio_value'].min(), df['portfolio_value'].max(), 500 ))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0f'))

# Add legend and grid
ax.legend()
ax.grid(False)

# Second chart
ax = fig.add_subplot(412)
ax.plot(df['gross_leverage'], 
        label='Strategy exposure'.format(calc_window), 
        linestyle='-', 
        color='black',
        linewidth=1.0)

# Make the axis look nicer
ax.yaxis.set_ticks(np.arange(df['gross_leverage'].min(), df['gross_leverage'].max(), 0.02 ))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.2f'))

# Add legend and grid
ax.legend()
ax.grid(True)

# Third chart
ax = fig.add_subplot(413)
ax.plot(df['annualized'], 
        label='{} days annualized return'.format(calc_window), 
        linestyle='-', 
        color='black',
        linewidth=1.0)

# Make the axis look nicer
ax.yaxis.set_ticks(np.arange(df['annualized'].min(), df['annualized'].max(), 0.5 ))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))

# Add legend and grid
ax.legend()
ax.grid(True)

# Fourth chart
ax = fig.add_subplot(414)
ax.plot(df['drawdown'], 
        label='{} days max drawdown'.format(calc_window), 
        linestyle='-', 
        color='black',
        linewidth=1.0)

# Make the axis look nicer
ax.yaxis.set_ticks(np.arange(df['drawdown'].min(), df['drawdown'].max(), 0.1 ))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))

# Add legend and grid
ax.legend()
ax.grid(True)


# In[ ]:




