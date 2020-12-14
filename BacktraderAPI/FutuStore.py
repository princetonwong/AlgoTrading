from futu import *
import time
from backtrader.position import Position
from backtrader.metabase import MetaParams
from backtrader.utils.py3 import bytes, bstr, queue, with_metaclass, long
import pandas as pd
from get_variable_name import get_variable_name
import glog as gLog
from backtrader import OrderBase, CommInfoBase
import Keys



class StockQuoteTest(StockQuoteHandlerBase):
    """
    获得报价推送数据
    """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(StockQuoteTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("* StockQuoteTest : %s" % content)
        return RET_OK, content


class CurKlineTest(CurKlineHandlerBase):
    """ kline push"""
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(CurKlineTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* CurKlineTest: error, msg: %s" % content)
        return RET_OK, content


class RTDataTest(RTDataHandlerBase):
    """ 获取分时推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(RTDataTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* RTDataTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("* RTDataTest :%s \n" % content)
        return RET_OK, content


class TickerTest(TickerHandlerBase):
    """ 获取逐笔推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(TickerTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* TickerTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("* TickerTest\n", content)
        return RET_OK, content


class OrderBookTest(OrderBookHandlerBase):
    """ 获得摆盘推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(OrderBookTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* OrderBookTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("* OrderBookTest\n", content)
        return RET_OK, content


class BrokerTest(BrokerHandlerBase):
    """ 获取经纪队列推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, stock_code, contents = super(BrokerTest, self).on_recv_rsp(rsp_pb)
        if ret_code == RET_OK:
            bid_content = contents[0]
            ask_content = contents[1]
            print("* BrokerTest code \n", stock_code)
            print("* BrokerTest bid \n", bid_content)
            print("* BrokerTest ask \n", ask_content)
        return ret_code


class SysNotifyTest(SysNotifyHandlerBase):
    """sys notify"""
    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, content = super(SysNotifyTest, self).on_recv_rsp(rsp_pb)

        if ret_code == RET_OK:
            main_type, sub_type, msg = content
            print("* SysNotify main_type='{}' sub_type='{}' msg='{}'\n".format(main_type, sub_type, msg))
        else:
            print("* SysNotify error:{}\n".format(content))
        return ret_code, content


class TradeOrderTest(TradeOrderHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeOrderTest, self).on_recv_rsp(rsp_pb)

        if ret == RET_OK:
            print("* TradeOrderTest content={}\n".format(content))

        return ret, content


class TradeDealTest(TradeDealHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeDealTest, self).on_recv_rsp(rsp_pb)

        if ret == RET_OK:
            print("TradeDealTest content={}".format(content))

        return ret, content






class MetaSingleton(MetaParams):
    '''Metaclass to make a metaclassed class a singleton'''
    def __init__(cls, name, bases, dct):
        super(MetaSingleton, cls).__init__(name, bases, dct)
        cls._singleton = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = (
                super(MetaSingleton, cls).__call__(*args, **kwargs))

        return cls._singleton

class FutuCommInfo(CommInfoBase):
    '''
    Commissions are calculated by ib, but the trades calculations in the
    ```Strategy`` rely on the order carrying a CommInfo object attached for the
    calculation of the operation cost and value.

    These are non-critical informations, but removing them from the trade could
    break existing usage and it is better to provide a CommInfo objet which
    enables those calculations even if with approvimate values.

    The margin calculation is not a known in advance information with IB
    (margin impact can be gotten from OrderState objects) and therefore it is
    left as future exercise to get it'''

    def getvaluesize(self, size, price):
        # In real life the margin approaches the price
        return abs(size) * price

    def getoperationcost(self, size, price):
        '''Returns the needed amount of cash an operation would cost'''
        # Same reasoning as above
        return abs(size) * price

class FutuStore(with_metaclass(MetaSingleton, object)):
    params = dict(host= "127.0.0.1", port= 11111, region="US", trd_env= TrdEnv.SIMULATE)

    def __init__(self):
        super(FutuStore, self).__init__()

        # Connection object
        if self.p.region == "US":
            self.tradeContext = OpenUSTradeContext(host=self.p.host, port=self.p.port)
        elif self.p.region == "HK":
            self.tradeContext = OpenHKTradeContext(host=self.p.host, port=self.p.port)

    def isConnected(self):
        connection, errorMessage = self.tradeContext.get_acc_list()
        if connection == RET_OK:
            return True
        else:
            print(errorMessage)
            return False

    def connected(self):
        # The isConnected method is available through __getattr__ indirections
        # and may not be present, which indicates that no connection has been
        # made because the subattribute sender has not yet been created, hence
        # the check for the AttributeError exception
        try:
            return self.isConnected()
        except AttributeError:
            pass

        return False  # non-connected (including non-initialized)

    def get_acc_cash(self):
        _ , df = self.tradeContext.accinfo_query(trd_env= self.p.trd_env)
        cash = df["cash"].item()
        return cash


    def get_acc_value(self):
        _ , df = self.tradeContext.accinfo_query(trd_env= self.p.trd_env)
        portfolioValue = df["total_assets"].item()
        return portfolioValue


    def getposition(self, data):
        _, df = self.tradeContext.position_list_query(code= data, trd_env=self.p.trd_env)
        # df.to_csv("position.csv")
        size = df ["qty"].item()
        costPrice = df["cost_price"].item()
        return Position(size= size, price= costPrice)


    def placeOrder(self, order):
        try:
            if order.exectype == order.Market: # 市价，目前仅美股
                order.orderType = OrderType.MARKET
            elif order.exectype == None: # 普通订单(港股的增强限价单、A股限价委托、美股的限价单)
                order.orderType = OrderType.NORMAL
        except (ValueError):
            return

        self.unlockTrade()
        ret , df = self.tradeContext.place_order(price= order.price, qty= order.size,
                                              code= order.data, trd_side= order.action,
                                              order_type= order.orderType, adjust_limit=0,
                                              trd_env=self.p.trd_env, acc_id=0, acc_index=0,
                                              remark=None)
        if ret != RET_OK:
            print ("error:"+ df)

        placedOrder = order
        placedOrder.orderId = df["order_id"].item()
        print ("Order of ID {} is successfully placed.".format(placedOrder.orderId))

        return placedOrder


    def cancelOrder(self, order):

        self.unlockTrade()
        ret , df = self.tradeContext.modify_order(modify_order_op= ModifyOrderOp.CANCEL, order_id= order.orderId,
                                       qty= 0, price=0, trd_env=self.p.trd_env)
        if ret != RET_OK:
            print ("error:"+ df)

        cancelledOrder = order
        cancelledOrder.orderId = df["order_id"].item()
        print("Order of ID {} is successfully cancelled.".format(cancelledOrder.orderId))

        return cancelledOrder

    def stop(self):
        try:
            self.tradeContext.close()  # disconnect should be an invariant
        except AttributeError:
            pass    # conn may have never been connected and lack "disconnect"

    #TODO
    def start(self, data=None, broker=None):
        self.reconnect(fromstart=True)  # reconnect should be an invariant

        # Datas require some processing to kickstart data reception
        if data is not None:
            self._env = data._env
            # For datas simulate a queue with None to kickstart co
            self.datas.append(data)

            # if connection fails, get a fake registration that will force the
            # datas to try to reconnect or else bail out
            return self.getTickerQueue(start=True)

        elif broker is not None:
            self.broker = broker

    def reconnect(self, fromstart=False, resub=False):
        # This method must be an invariant in that it can be called several
        # times from the same source and must be consistent. An exampler would
        # be 5 datas which are being received simultaneously and all request a
        # reconnect

        # Policy:
        #  - if dontreconnect has been set, no option to connect is possible
        #  - check connection and use the absence of isConnected as signal of
        #    first ever connection (add 1 to retries too)
        #  - Calculate the retries (forever or not)
        #  - Try to connct
        #  - If achieved and fromstart is false, the datas will be
        #    re-kickstarted to recreate the subscription
        firstconnect = False
        try:
            if self.tradeContext.isConnected():
                if resub:
                    self.startdatas()
                return True  # nothing to do
        except AttributeError:
            # Not connected, several __getattr__ indirections to
            # self.conn.sender.client.isConnected
            firstconnect = True

        if self.dontreconnect:
            return False

        # This is only invoked from the main thread by datas and therefore no
        # lock is needed to control synchronicity to it
        retries = self.p.reconnect
        if retries >= 0:
            retries += firstconnect

        while retries < 0 or retries:
            if not firstconnect:
                time.sleep(self.p.timeout)

            firstconnect = False

            if self.tradeContext.connect():
                if not fromstart or resub:
                    self.startdatas()
                return True  # connection successful

            if retries > 0:
                retries -= 1

        self.dontreconnect = True
        return False  # connection/reconnection failed

    def getTickerQueue(self, start=False):
        '''Creates ticker/Queue for data delivery to a data feed'''
        q = queue.Queue()
        if start:
            q.put(None)
            return q

        with self._lock_q:
            tickerId = self.nextTickerId()
            self.qs[tickerId] = q  # can be managed from other thread
            self.ts[q] = tickerId
            self.iscash[tickerId] = False

        return tickerId, q

    def reqAccountUpdates(self, subscribe=True, account=None):
        '''Proxy to reqAccountUpdates

        If ``account`` is ``None``, wait for the ``managedAccounts`` message to
        set the account codes
        '''
        if account is None:
            self._event_managed_accounts.wait()
            account = self.managed_accounts[0]

        self.tradeContext.reqAccountUpdates(subscribe, bytes(account))

    def unlockTrade(self):
        ret, df = self.tradeContext.unlock_trade(Keys.FutuPassword)

        if ret != RET_OK:
            print ("error:"+ df)

class FutuOrder(OrderBase):

    def __init__(self, action, owner, data, size, price, plimit, exectype, valid, tradeid=0, **kwargs):

        self.ordtype = self.Buy if action == 'BUY' else self.Sell
        self.action = action
        self.owner = owner
        self.data= data
        self.size = size
        self.price = price
        self.plimit = plimit
        self.exectype = exectype
        self.valid = valid
        self.tradeid = tradeid
        # super(FutuOrder, self).__init__()







def quote_test():
    '''
    行情接口调用测试
    :return:
    '''
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    # 设置异步回调接口
    quote_ctx.set_handler(StockQuoteTest())
    quote_ctx.set_handler(CurKlineTest())
    quote_ctx.set_handler(RTDataTest())
    quote_ctx.set_handler(TickerTest())
    quote_ctx.set_handler(OrderBookTest())
    quote_ctx.set_handler(BrokerTest())
    quote_ctx.set_handler(SysNotifyTest())
    quote_ctx.start()

    # 获取推送数据
    big_sub_codes = ['HK.02318', 'HK.02828', 'HK.00939', 'HK.01093', 'HK.01299', 'HK.00175',
                     'HK.01299', 'HK.01833', 'HK.00005', 'HK.00883', 'HK.00388', 'HK.01398',
                     'HK.01114', 'HK.02800', 'HK.02018', 'HK.03988', 'HK.00386', 'HK.01211',
                     'HK.00700', 'HK.01177',  'HK.02601', 'HK.02628', 'HK.HSImain']
    subtype_list = [SubType.QUOTE, SubType.ORDER_BOOK, SubType.TICKER, SubType.K_DAY, SubType.RT_DATA, SubType.BROKER]

    sub_codes =  ['HK.00700', 'HK.HSImain']

    # print("* get_owner_plate : {}\n".format(quote_ctx.get_owner_plate(code_list)))
    # print("* get_referencestock_list : {}\n".format(quote_ctx.get_referencestock_list(
    #     code_list[0], SecurityReferenceType.WARRANT)))
    # # print("* get_holding_change_list : {}\n".format(quote_ctx.get_holding_change_list(
    # #     "US.AAPL", StockHolder.EXECUTIVE, "2018-01-01", None)))
    #
    # print("* request_history_kline : {}\n".format(quote_ctx.request_history_kline(
    #     code_list[0], "2018-01-01", None, KLType.K_1M, AuType.QFQ, [KL_FIELD.ALL], 50000)))

    # 测试大量数据定阅
    # if len(big_sub_codes):
    #     print("* subscribe : {}\n".format(quote_ctx.subscribe(big_sub_codes, subtype_list)))

    """
    if True:
        print("* subscribe : {}\n".format(quote_ctx.subscribe(code_list, subtype_list)))
        print("* query_subscription : {}\n".format(quote_ctx.query_subscription(True)))
        sleep(60.1)
        print("* unsubscribe : {}\n".format(quote_ctx.unsubscribe(code_list, subtype_list)))
        print("* query_subscription : {}\n".format(quote_ctx.query_subscription(True)))
        sleep(1)
    """
    print("* subscribe : {}\n".format(quote_ctx.subscribe(sub_codes, subtype_list)))

    # # """
    # print("* get_stock_basicinfo : {}\n".format(quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.ETF)))
    # print("* get_cur_kline : {}\n".format(quote_ctx.get_cur_kline(code_list[0], 10, SubType.K_DAY, AuType.QFQ)))
    #
    # print("* get_rt_data : {}\n".format(quote_ctx.get_rt_data(code_list[0])))
    # print("* get_rt_ticker : {}\n".format(quote_ctx.get_rt_ticker(code_list[0], 10)))
    #
    # print("* get_broker_queue : {}\n".format(quote_ctx.get_broker_queue(code_list[0])))
    # print("* get_order_book : {}\n".format(quote_ctx.get_order_book(code_list[0])))
    # print("* request_history_kline : {}\n".format(quote_ctx.request_history_kline('HK.00700', start='2017-06-20', end='2017-06-22')))
    # # """
    #
    # # """
    # print("* get_multi_points_history_kline : {}\n".format(quote_ctx.get_multi_points_history_kline(code_list, ['2017-06-20', '2017-06-22', '2017-06-23'], KL_FIELD.ALL,
    #                                                KLType.K_DAY, AuType.QFQ)))
    # print("* get_autype_list : {}\n".format(quote_ctx.get_autype_list("HK.00700")))
    #
    # print("* get_trading_days : {}\n".format(quote_ctx.get_trading_days(Market.HK, '2018-11-01', '2018-11-20')))
    #
    # print("* get_market_snapshot : {}\n".format(quote_ctx.get_market_snapshot('HK.21901')))
    # print("* get_market_snapshot : {}\n".format(quote_ctx.get_market_snapshot(code_list)))
    #
    # print("* get_plate_list : {}\n".format(quote_ctx.get_plate_list(Market.HK, Plate.ALL)))
    # print("* get_plate_stock : {}\n".format(quote_ctx.get_plate_stock('HK.BK1001')))
    # """

    # """
    time.sleep(15)
    quote_ctx.close()
    # """

def trade_hkcc_test():
    """
    A股通交易测试
    :return:
    """
    trd_ctx = OpenHKCCTradeContext(host='127.0.0.1', port=11111)
    trd_ctx.set_handler(TradeOrderTest())
    trd_ctx.set_handler(TradeDealTest())
    trd_ctx.start()

    # 交易请求必须先解锁 !!!
    # pwd_unlock = '147536'
    # print("* unlock_trade : {}\n".format(trd_ctx.unlock_trade(pwd_unlock)))
    #
    # print("* accinfo_query : {}\n".format(trd_ctx.accinfo_query()))
    # print("* position_list_query : {}\n".format(trd_ctx.position_list_query(pl_ratio_min=-50, pl_ratio_max=50)))
    # print("* order_list_query : {}\n".format(trd_ctx.order_list_query(status_filter_list=[OrderStatus.DISABLED])))
    # print("* get_acc_list : {}\n".format(trd_ctx.get_acc_list()))
    # print("* order_list_query : {}\n".format(trd_ctx.order_list_query(status_filter_list=[OrderStatus.SUBMITTED])))
    #
    # ret_code, ret_data = trd_ctx.place_order(0.1, 100, "SZ.000979", TrdSide.BUY)
    # print("* place_order : {}\n".format(ret_data))
    # if ret_code == RET_OK:
    #     order_id = ret_data['order_id'][0]
    #     print("* modify_order : {}\n".format(trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0)))
    #
    # print("* deal_list_query : {}\n".format(trd_ctx.deal_list_query(code="000979")))
    # print("* history_order_list_query : {}\n".format(trd_ctx.history_order_list_query(status_filter_list=[OrderStatus.FILLED_ALL, OrderStatus.FILLED_PART],
    #                                        code="512310", start="", end="2018-2-1")))
    #
    # print("* history_deal_list_query : {}\n".format(trd_ctx.history_deal_list_query(code="", start="", end="2018-6-1")))

    time.sleep(10)
    trd_ctx.close()

def trade_us_test(**kwargs):

    trd_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111)
    trd_ctx.set_handler(TradeOrderTest())
    trd_ctx.set_handler(TradeDealTest())
    trd_ctx.start()

    # 交易请求必须先解锁 !!!
    eP("unlock_trade", trd_ctx.unlock_trade("147536"))
    eP("accinfo_query", trd_ctx.accinfo_query(**kwargs))
    eP("position_list_query", trd_ctx.position_list_query(pl_ratio_min=-50, pl_ratio_max=50, **kwargs))
    eP("order_list_query", trd_ctx.order_list_query(status_filter_list=[OrderStatus.DISABLED], **kwargs))
    eP("get_acc_list", trd_ctx.get_acc_list())
    eP("order_list_query", trd_ctx.order_list_query(status_filter_list=[OrderStatus.SUBMITTED], **kwargs))

    ret_code, ret_data = trd_ctx.place_order(700.0, 100, "US.TSLA", TrdSide.SELL, order_type=OrderType.MARKET, **kwargs)
    eP("place_order", ret_data)

    if ret_code == RET_OK:
        order_id = ret_data['order_id'][0]
        eP("modify_order", trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0))

    eP("deal_list_query", trd_ctx.deal_list_query(code="US.TSLA"))

    history_order_list_query = trd_ctx.history_order_list_query(**kwargs)
    eP("history_order_list_query", history_order_list_query[1])
    history_order_list_query[1].to_csv("order_list.csv")

    history_deal_list_query = trd_ctx.history_deal_list_query(code="", start="", end="2018-6-1", **kwargs)
    eP("history_deal_list_query", history_deal_list_query[1])

    time.sleep(100000)
    trd_ctx.close()

def trade_hk_test(**kwargs):

    trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
    trd_ctx.set_handler(TradeOrderTest())
    trd_ctx.set_handler(TradeDealTest())
    trd_ctx.start()

    # 交易请求必须先解锁 !!!
    eP("unlock_trade", trd_ctx.unlock_trade("147536"))
    eP("accinfo_query", trd_ctx.accinfo_query(**kwargs))
    eP("position_list_query", trd_ctx.position_list_query(pl_ratio_min=-50, pl_ratio_max=50, **kwargs))

    order_list_query = trd_ctx.order_list_query(**kwargs)
    print (get_variable_name(order_list_query), order_list_query)
    eP("order_list_query", trd_ctx.order_list_query(**kwargs))
    eP("get_acc_list", trd_ctx.get_acc_list())
    eP("order_list_query", trd_ctx.order_list_query(status_filter_list=[OrderStatus.SUBMITTED], **kwargs))

    # ret_code, ret_data = trd_ctx.place_order(400.0, 100, "HK.00700", TrdSide.BUY, order_type=OrderType.NORMAL, **kwargs)
    # easyPrint("place_order", ret_data)
    #
    # if ret_code == RET_OK:
    #     order_id = ret_data['order_id'][0]
    #     easyPrint("modify_order", trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0))

    eP("deal_list_query", trd_ctx.deal_list_query(code="00700"))

    history_order_list_query = trd_ctx.history_order_list_query(**kwargs)
    eP("history_order_list_query", history_order_list_query[1])
    history_order_list_query[1].to_csv("order_list.csv")

    history_deal_list_query = trd_ctx.history_deal_list_query(code="", start="", end="2018-6-1", **kwargs)
    eP("history_deal_list_query", history_deal_list_query[1])

    time.sleep(100000)
    trd_ctx.close()

def eP(title, message):
    print (f"* {title} : {message}\n")

#same as in FutuAPI
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