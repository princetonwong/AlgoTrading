from futu import *
from time import sleep
import Keys as Keys

class FutuAPI():
    
    password = Keys.FutuPassword
    
    def placeUSOrder(self, price, quantity, code, tradeSide, orderType = OrderType.NORMAL, tradeEnvironment = TrdEnv.SIMULATE):
        tradeContext= OpenUSTradeContext(host='127.0.0.1', port=11111)
        unlock = tradeContext.unlock_trade(self.password)
        _, placedOrder = tradeContext.place_order(price= price, qty= quantity, code= code, trd_side=tradeSide, order_type= orderType, trd_env= tradeEnvironment)
        tradeContext.close()
        return placedOrder
    
    def placeHKOrder(self, price, quantity, code, tradeSide, orderType = OrderType.NORMAL, tradeEnvironment = TrdEnv.SIMULATE):
        tradeContext= OpenHKTradeContext(host='127.0.0.1', port=11111)
        unlock = tradeContext.unlock_trade(self.password)
        _, placedOrder = tradeContext.place_order(price= price, qty= quantity, code= code, trd_side=tradeSide, order_type= orderType, trd_env= tradeEnvironment)
        tradeContext.close()
        return placedOrder

    def placeFutureOrder(self, price, quantity, code, tradeSide, orderType = OrderType.NORMAL, tradeEnvironment = TrdEnv.SIMULATE):
        tradeContext= OpenFutureTradeContext(host='127.0.0.1', port=11111)
        unlock = tradeContext.unlock_trade(self.password)
        _, placedOrder = tradeContext.place_order(price= price, qty= quantity, code= code, trd_side=tradeSide, order_type= orderType, trd_env= tradeEnvironment)
        tradeContext.close()
        return placedOrder
    
    def queryUSOrderList(self, tradingEnvironment= TrdEnv.SIMULATE):
        tradeContext = OpenUSTradeContext(host='127.0.0.1', port=11111)
        unlock = tradeContext.unlock_trade(self.password)
        query = tradeContext.order_list_query(trd_env= tradingEnvironment)
        tradeContext.close()
        sleep(5)
        return query
    def queryCurrentPositions(self, tradingEnvironment= TrdEnv.SIMULATE):
        trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
        trd_ctx.unlock_trade(self.password)
        _, df = trd_ctx.position_list_query(trd_env=tradingEnvironment)
        trd_ctx.close()
        return df
    
    @staticmethod
    def getRealTimeData(symbol):
        data4 = pd.DataFrame.empty
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
        ret_sub, err_message = quote_ctx.subscribe([symbol], [SubType.RT_DATA],
                                                   subscribe_push=False)  # 先订阅分时数据类型。订阅成功后OpenD将持续收到服务器的推送，False代表暂时不需要推送给脚本
        if ret_sub == RET_OK:  # 订阅成功
            ret, data4 = quote_ctx.get_rt_data(symbol)  # 获取一次分时数据
            if ret == RET_OK:
                pass
            else:
                print('error:', data4)
        else:
            print('subscription failed', err_message)
    
        quote_ctx.close()
        return data4
    
    @staticmethod
    def getRealTimeKLine(symbol, subtype: SubType = SubType.K_1M, num=1000):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret_sub, err_message = quote_ctx.subscribe([symbol], [subtype], subscribe_push=False)
        if ret_sub == RET_OK:
            ret, data2 = quote_ctx.get_cur_kline(symbol, num = num, ktype = subtype, autype = AuType.QFQ)
            if ret == RET_OK:
                pass
                # print(data['turnover_rate'].values.tolist())  # 转为list
            else:
                print('error:', data2)
        else:
            print('subscription failed', err_message)
        quote_ctx.close()
        return data2
    
    @staticmethod
    def getPlateStock(plate):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = quote_ctx.get_plate_stock(plate)
        if ret == RET_OK:
            print ("ok")
            # print(data['stock_name'].values.tolist())  # 转为list
        else:
            print('error:', data)
        quote_ctx.close()
        return data

    @staticmethod
    def getKLineFromDate(symbol, kLineSubType, timeRange, count=10000):
        print (timeRange)
        start, startTime, end, endTime = timeRange
        output = ""
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data, page_req_key = quote_ctx.request_history_kline(symbol, start=start, end=end, ktype=kLineSubType,
                                                                  max_count=count)
        if ret == RET_OK:
            pass
            output = data
            # print(data['close'].values.tolist())  # 第一页收盘价转为list
        else:
            print('error:', data)
        while page_req_key != None:  # 请求后面的所有结果
            # print('*************************************')
            ret, data, page_req_key = quote_ctx.request_history_kline(symbol, start=start, end=end,
                                                                      max_count=count, ktype=kLineSubType,
                                                                      page_req_key=page_req_key)  # 请求翻页后的数据
            if ret == RET_OK:
                pass
            else:
                print('error:', data)
        print('All pages are finished!')
        quote_ctx.close()

        data = output
        data['time_key'] = pd.to_datetime(data['time_key'], format="%Y-%m-%d %H:%M:%S")
        start = datetime.strptime(startTime, '%H:%M:%S').time()
        end = datetime.strptime(endTime, '%H:%M:%S').time()
        data = data[data['time_key'].dt.time.between(start, end)]

        return data
