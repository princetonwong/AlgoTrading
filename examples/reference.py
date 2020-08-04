#计算CCI
from CustomAPI.FutuAPI import FutuAPI
from futu import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


n = 20
a= 0.015
index = 'HK.02388'
kLineSubType = SubType.K_DAY
timeRange = ("2019-05-31", "00:00:00", "2020-06-30", "16:31:00")

# CCI策略双边交易表现
threshold = 100

def cal_meandev(tp,matp):
    mean_dev = (n-1)*[np.nan]
    for i in range(len(tp)-n+1):
        mean_dev.append(np.mean(abs(tp[i:i+n]-matp[i+n-1])))
    return np.array(mean_dev)

# extended_days = get_trade_days(end_date = start,count=n-1)
# start=extended_days[0]

def get_data(index, timeRange, kLineSubType,n,a):
    # df = get_price(index,start_date=start,end_date=end,fields = ['close','high','low'] )
    df = FutuAPI().getKLineFromDate(index, timeRange, kLineSubType)
    print(df.head(5))
    df['tp'] = (df['close']+df['high']+df['low'])/3
    df['matp'] = df['tp'].rolling(n).mean()
    mean_dev = cal_meandev(df['tp'],df['matp'])
    df['mean_dev'] = mean_dev
    df['cci'] = (df['tp']-df['matp'])/(a*df['mean_dev'])
    return df
df = get_data(index, timeRange, kLineSubType,n,a)

print ("df length: " + str(df.shape[0]))

# def gen_signal(cci, threshold):
#     signal = n * [0]
#     for i in range(n, len(cci)):
#         if cci[i] > threshold and cci[i - 1] < threshold:
#             signal.append(1)
#         elif cci[i] < -threshold and cci[i - 1] > -threshold:
#             signal.append(-1)
#         else:
#             signal.append(0)
#     return np.array(signal)




def cal_ret(df):
    ret = n * [0]
    for i in range(n, len(df)):
        ret.append(df['position'][i - 1] * df['index_ret'][i])
    ret = np.array(ret)
    return ret


def cal_cum_ret(ret):
    cum_ret = [1]
    for i in range(len(ret) - 1):
        cum_ret.append(cum_ret[-1] * (1 + ret[i]))
    cum_ret = np.array(cum_ret)
    return cum_ret


# def back_test(df, threshold, short, plot=True):
#     df['index_ret'] = np.concatenate(([np.nan], np.array(df['close'][1:]) / np.array(df['close'][:-1]))) - 1
#     df['signal'] = gen_signal(df['cci'], threshold)
#     df['position'] = gen_position(df['signal'], short)
#     ret = cal_ret(df)
#     df['ret'] = ret
#     cum_ret = cal_cum_ret(ret)
#
#     # 计算指标
#     sum_dict = {}
#     sum_dict['总收益'] = cum_ret[-1] - 1
#     sum_dict['日胜率'] = len(ret[ret > 0]) / (len(ret[ret > 0]) + len(ret[ret < 0]))
#     max_nv = np.maximum.accumulate(cum_ret)
#     mdd = -np.min(cum_ret / max_nv - 1)
#     sum_dict['最大回撤'] = mdd
#     sum_dict['夏普比率'] = ret.mean() / ret.std() * np.sqrt(240)
#     sum_df = pd.DataFrame(sum_dict, index=[0])
#
#     if plot:
#         # 作图
#         plt.figure(1, figsize=(20, 10))
#         plt.title('策略表现', fontsize=18)
#         plt.plot(df.index, cum_ret)
#         plt.plot(df.index, df['close'] / df['close'][0])
#         plt.legend(['CCI策略', 'HS300'], fontsize=14)
#         plt.show()
#     return sum_df
#
#
# back_test(df, threshold, True)
#
#
# #敏感性分析
# ns = list(range(15,31))
# sharpe_list =[]
# for n in ns:
#     df2 = get_data(start,end,n,a,index)
#     summary = back_test(df2,threshold,True,False)
#     sharpe_list.append(summary['夏普比率'][0])
# plt.figure(figsize=(15,8))
# plt.plot(ns,sharpe_list)
#
#
# #双边交易最优参数回测
# df2 = get_data(start,end,22,a,index)
# back_test(df2,threshold,True,True)
#
#
# #单边交易最优参数回测
# df3 = get_data(start,end,22,a,index)
# back_test(df2,threshold,False,True)
#
#
# #单边交易敏感性分析
# ns = list(range(15,31))
# sharpe_list =[]
# for n in ns:
#     df3 = get_data(start,end,n,a,index)
#     summary = back_test(df3,threshold,False,False)
#     sharpe_list.append(summary['夏普比率'][0])
# plt.figure(figsize=(15,8))
# plt.title('单边交易敏感性分析')
# plt.plot(ns,sharpe_list)
def gen_position(signal, short):
    position = [0]
    if short:
        short_pos = -1
    else:
        short_pos = 0
    for i in range(1, len(signal)):
        if signal[i] == 1:
            position.append(1)
        elif signal[i] == 0:
            position.append(position[-1])
        else:
            position.append(short_pos)
    return np.array(position)

# 优化的CCI择时策略(双边交易)
def gen_signal_2(cci, threshold, m):
    signal = n * [0]
    up_list = []
    down_list = []
    flag = 0
    for i in range(n, len(cci)):
        if cci[i] > 100 and cci[i - 1] < 100:
            signal.append(1)
            up_list.append(i)
        elif cci[i] < -100 and cci[i - 1] > -100:
            signal.append(-1)
            down_list.append(i)
        elif cci[i] < 100 and cci[i - 1] > 100:
            try:
                if up_list[-1] < i - m:
                    signal.append(0)
                else:
                    signal.append(-1)
            except:
                signal.append(0)
        elif cci[i] > -100 and cci[i - 1] < -100:
            try:
                if down_list[-1] < i - m:
                    signal.append(0)
                else:
                    signal.append(1)
            except:
                signal.append(0)
        else:
            signal.append(0)
    print("signal: " +str(len(signal)))
    return np.array(signal)


def back_test_2(df, threshold, m, short=True, plot=True):
    df['index_ret'] = np.concatenate(([np.nan], np.array(df['close'][1:]) / np.array(df['close'][:-1]))) - 1
    df['signal'] = gen_signal_2(df['cci'], threshold, m)
    df['position'] = gen_position(df['signal'], short)
    ret = cal_ret(df)
    df['ret'] = ret
    cum_ret = cal_cum_ret(ret)

    # 计算指标
    sum_dict = {}
    sum_dict['总收益'] = cum_ret[-1] - 1
    sum_dict['日胜率'] = len(ret[ret > 0]) / (len(ret[ret > 0]) + len(ret[ret < 0]))
    max_nv = np.maximum.accumulate(cum_ret)
    mdd = -np.min(cum_ret / max_nv - 1)
    sum_dict['最大回撤'] = mdd
    sum_dict['夏普比率'] = ret.mean() / ret.std() * np.sqrt(240)
    sum_df = pd.DataFrame(sum_dict, index=[0])

    if plot:
        # 作图
        plt.figure(1, figsize=(20, 10))
        plt.plot(df.index, cum_ret)
        plt.plot(df.index, df['close'] / df['close'][0])
        plt.legend(['CCI', 'index'], fontsize=14)
        plt.show()
        print (sum_df)
    return sum_df


df4 = get_data(index, timeRange, kLineSubType,n,a)
back_test_2(df4, threshold, m=7, short=True, plot=True)

# #优化的CCI择时策略(单边交易)
# df4 = get_data(start,end,20,a,index)
# back_test_2(df4,threshold,False)