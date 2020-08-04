import talib as tl
from datetime import datetime
import pandas as pd
# import matplotlib.finance as mpf
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# 公用函数
def get_data(count):
    # 上一个交易日
    # date = list(jqdata.get_trade_days(end_date=end_date, count=2))[0]

    # 股票行情数据, 要计算60日均线，取62日
    df = pd.read_csv("hk00700data.csv")
    # macdData = talib.MACD(df["cur_price"], 5, 35, 5)

    # 计算均线
    df['ma5'] = pd.Series(tl.MA(df['cur_price'].values, 5), index=df.index.values)
    df['ma10'] = pd.Series(tl.MA(df['cur_price'].values, 10), index=df.index.values)
    df['ma20'] = pd.Series(tl.MA(df['cur_price'].values, 20), index=df.index.values)
    df['ma60'] = pd.Series(tl.MA(df['cur_price'].values, 60), index=df.index.values)

    # MACD指标
    diff, dea, macd = tl.MACD(df['cur_price'].values,5,35,5)

    df['diff'] = pd.Series(diff, index=df.index.values)
    df['dea'] = pd.Series(dea, index=df.index.values)
    df['macd'] = pd.Series(macd * 2.0, index=df.index.values)

    # 截取最近 count 天的数据
    df = df.iloc[0 - count:]
    t = range(count)

    df['t'] = pd.Series(t, index=df.index)
    df = df.set_index('t')

    return df

# 显示K线和均线
def show_k_ma(ax, df):
    ##################################################################
    # 绘制K线 & 绘制均线
    ##################################################################

    ax.set_xlim(0, days)
    # ax1.set_axis_off()
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

    # 计算 quotes
    t = range(len(df))

    o = list(df['open'].values)
    h = list(df['high'].values)
    l = list(df['low'].values)
    c = list(df['close'].values)
    quotes = zip(t, o, h, l, c)

    # 画K线
    mpf.candlestick_ohlc(ax, quotes, width=0.5, colorup='r', colordown='g')

    # 画均线
    df[['ma5', 'ma10', 'ma20', 'ma60']].plot(ax=ax, legend=True)

# 显示卡线图上均线交叉
def show_k_ma_cross_ma(ax, df):
    ma5 = df['ma5'].values
    ma10 = df['ma10'].values
    ma20 = df['ma20'].values

    # 均线交叉
    for i in range(4, len(ma5)):
        if ma10[i - 1] < ma20[i - 1] and ma10[i] > ma20[i]:
            # 10日线金叉20日线，用红圈标出金叉
            ax.scatter(i - 1, ma10[i - 1], color='', marker='o', edgecolors='r', s=300, linewidths=3)

        elif ma5[i - 1] > ma10[i - 1] and ma5[i] < ma10[i]:
            # 5日线死叉10日线，用绿圈标出死叉
            ax.scatter(i - 1, ma5[i - 1], color='', marker='o', edgecolors='g', s=300, linewidths=3)

# 显示K线图上MACD交叉（买入卖出标记）
def show_k_ma_cross_macd(ax, df):
    # MACD柱状图
    macd = df['macd'].values
    macdDIFF = df['diff'].values
    macdDEA = df['dea'].values

    # MACD交叉标记
    for i in range(4, len(macd)):
        if macdDIFF[i - 1] < macdDEA[i - 1] and macdDIFF[i] > macdDEA[i]:
            # 用红圈标出金叉
            ax.scatter(i, df['low'].values[i] * 0.99, color='', marker='^', edgecolors='r', s=500, linewidths=5)

        elif macdDIFF[i - 1] > macdDEA[i - 1] and macdDIFF[i] < macdDEA[i]:
            # 用绿圈标出死叉
            ax.scatter(i, df['high'].values[i] * 1.01, color='', marker='v', edgecolors='g', s=500, linewidths=5)

# 显示 MACD图
def show_macd(ax, df):
    macd = df['macd'].values
    macdDIFF = df['diff'].values
    macdDEA = df['dea'].values

    ##################################################################
    # 绘制MACD
    ##################################################################
    # ax.set_axis_off()
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

    ax.plot(df['diff'], 'b')
    ax.plot(df['dea'], 'y')

    t = range(len(df))
    for i in t:
        ax.bar(i, macd[i], color='r' if macd[i] > 0 else 'g')

def show_macd_cross(ax, df):
    macd = df['macd'].values
    macdDIFF = df['diff'].values
    macdDEA = df['dea'].values

    for i in range(4, len(macd)):
        if macdDIFF[i - 1] < macdDEA[i - 1] and macdDIFF[i] > macdDEA[i]:
            # 用红圈标出金叉
            ax.scatter(i, macdDEA[i], color='', marker='^', edgecolors='r', s=300, linewidths=3)

        elif macdDIFF[i - 1] > macdDEA[i - 1] and macdDIFF[i] < macdDEA[i]:
            # 用绿圈标出死叉
            ax.scatter(i, macdDEA[i], color='', marker='v', edgecolors='g', s=300, linewidths=3)

# 显示成交量
def show_volume(ax, df):
    # ax.set_axis_off()
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

    vv = df['volume'].values
    v = list(df['volume'].values)

    t = range(len(df))

    o = list(df['open'].values)
    h = list(df['high'].values)
    l = list(df['low'].values)
    c = list(df['close'].values)

    barlist = ax.bar(t, v, width=0.5)

    color = 'r'
    for i in t:
        if o[i] < c[i]:
            color = 'r'
        else:
            color = 'g'

        barlist[i].set_color(color)

# 初始化

stock = '600276.XSHG'
days = 150
end_date = datetime.now().date()

# 获取数据，包含了MA和MACD数据
df = get_data(count=days)

# 准备画图
plt.close()
fig = plt.figure(figsize=(20, 20), dpi=80, frameon=False)

# K线画板
ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=3, colspan=1)
ax1.set_xlim(0, days + 1)

# 画 K 线和均线
show_k_ma(ax=ax1, df=df)

# MACD画板
ax2 = plt.subplot2grid((6, 1), (3, 0), rowspan=1, colspan=1, sharex=ax1)
# ax2.set_xlim(0,days+1)


# 画 MACD
show_macd(ax=ax2, df=df)

# # 成交量画板
# ax3 = plt.subplot2grid((6, 1), (4, 0), rowspan=1, colspan=1, sharex=ax1)
# # ax3.set_xlim(0,days+1)
#
# # 画 成交量
# show_volume(ax=ax3, df=df)
#
# # 显示 MACD交叉
# show_macd_cross(ax=ax2, df=df)
# show_k_ma_cross_macd(ax=ax1, df=df)
# show_k_ma_cross_ma(ax=ax1, df=df)