from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
from copy import copy
from datetime import date, datetime, timedelta
import threading
import uuid

import ib.ext.Order
import ib.opt as ibopt
from futu import *

from backtrader.feed import DataBase
from backtrader import (TimeFrame, num2date, date2num, BrokerBase,
                        Order, OrderBase, OrderData)
from backtrader.utils.py3 import bytes, bstr, with_metaclass, queue, MAXFLOAT
from backtrader.metabase import MetaParams
from backtrader.comminfo import CommInfoBase
from backtrader.position import Position
from backtrader.order import Order
from backtrader.stores import ibstore
from backtrader.utils import AutoDict, AutoOrderedDict
from backtrader.comminfo import CommInfoBase
from BacktraderAPI.FutuStore import FutuStore, FutuOrder, FutuCommInfo
import time


class MetaFutuBroker(BrokerBase.__class__):
    def __init__(cls, name, bases, dct):
        '''Class has already been created ... register'''
        # Initialize the class
        super(MetaFutuBroker, cls).__init__(name, bases, dct)


class FutuBroker(with_metaclass(MetaFutuBroker, BrokerBase)):
    params = dict(region="HK", trd_env=TrdEnv.SIMULATE)

    def __init__(self, **kwargs):
        super(FutuBroker, self).__init__()

        self.futu = FutuStore(region=self.p.region, trd_env=self.p.trd_env)

        self.startingcash = self.cash = 0.0
        self.startingvalue = self.value = 0.0

        self._lock_orders = threading.Lock()  # control access
        self.orderbyId = dict()  # orders by order id
        self.executions = dict()  # notified executions
        self.ordstatus = collections.defaultdict(dict)
        # self.notifs = queue.Queue()  # holds orders which are notified
        # self.tonotify = collections.deque()  # hold oids to be notified

    def start(self):
        super(FutuBroker, self).start()
        self.futu.start(broker=self)

        if self.futu.connected():
            self.startingcash = self.cash = self.futu.get_acc_cash()
            self.startingvalue = self.value = self.futu.get_acc_value()
        else:
            self.startingcash = self.cash = 0.0
            self.startingvalue = self.value = 0.0

    def getcash(self):
        self.cash = self.futu.get_acc_cash()
        return self.cash

    def getvalue(self, datas=None):
        """
        if datas then we will calculate the value of the positions if not
        then the value of the entire portfolio (positions + cash)
        :param datas: list of data objects
        :return: float
        """

        if not datas:
            self.value = self.futu.get_acc_value()
            return self.value

        else:
            # let's calculate the value of the positions
            total_value = 0
            for d in datas:
                pos = self.getposition(d)
                if pos.size:
                    price = list(d)[0]
                    total_value += price * pos.size
            return total_value

    def getposition(self, data, clone=True):
        position = self.futu.getposition(data)
        if clone:
            pos = position.clone()

        return position

    def _makeorder(self, action, owner, data,
                   size, price=None, plimit=None,
                   exectype=None, valid=None,
                   tradeid=0, **kwargs):

        order = FutuOrder(action, owner, data, size, price, plimit, exectype, valid, tradeid, **kwargs)

        # order.addcomminfo(self.getcommissioninfo(data))
        return order

    def submit(self, order, **kwargs):
        order.submit(self)

        # ocoize if needed #TODO: oco
        # if order.oco is None:  # Generate a UniqueId
        #     order.m_ocaGroup = bytes(uuid.uuid4())
        # else:
        #     order.m_ocaGroup = self.orderbyId[order.oco.m_orderId].m_ocaGroup
        #


        placedOrder = self.futu.placeOrder(order)
        self.orderbyId[placedOrder.orderId] = placedOrder

        # self.notify(order) #TODO: Notify
        placedOrder.addinfo(**kwargs)
        placedOrder.addcomminfo(self.getcommissioninfo(placedOrder.data))

        return placedOrder

    def buy(self, owner, data,
            size, price=None, plimit=None,
            exectype=None, valid=None, tradeid=0,
            **kwargs):

        order = self._makeorder('BUY', owner, data, size, price, plimit, exectype, valid, tradeid, **kwargs)

        return self.submit(order)

    def sell(self, owner, data,
             size, price=None, plimit=None,
             exectype=None, valid=None, tradeid=0,
             **kwargs):

        order = self._makeorder('SELL', owner, data, size, price, plimit, exectype, valid, tradeid, **kwargs)

        return self.submit(order)

    def cancel(self, order):
        try:
            o = self.orderbyId[order.orderId]
        except (ValueError, KeyError):
            return  # not found ... not cancellable

        if order.status == Order.Cancelled:  # already cancelled
            return

        self.futu.cancelOrder(order)

    def stop(self):
        super(FutuBroker, self).stop()
        self.futu.stop()

    def getcommissioninfo(self, data):

        if "main" in data:
            mult = 10.0
            stocklike = False
        elif "." in data:  # Assume this is HK stocks from Futu
            mult = 1.0
            stocklike = True
        else:
            mult = 1.0
            stocklike = True

        return FutuCommInfo(mult=mult, stocklike=stocklike)

    # TODO: TODO
    def orderstatus(self, order):
        try:
            o = self.orderbyId[order.orderId]
        except (ValueError, KeyError):
            o = order

        return o.status

    def notify(self, order):
        self.notifs.put(order.clone())

    def get_notification(self):
        try:
            return self.notifs.get(False)
        except queue.Empty:
            pass

        return None

    def next(self):
        self.notifs.put(None)  # mark notificatino boundary

    def add_order_history(self, orders, notify=False):
        '''Add order history. See cerebro for details'''
        # raise NotImplementedError
        pass

    def set_fund_history(self, fund):
        '''Add fund history. See cerebro for details'''
        # raise NotImplementedError
        pass
    # # Order statuses in msg
    # (SUBMITTED, FILLED, CANCELLED, INACTIVE,
    #  PENDINGSUBMIT, PENDINGCANCEL, PRESUBMITTED) = (
    #     'Submitted', 'Filled', 'Cancelled', 'Inactive',
    #     'PendingSubmit', 'PendingCancel', 'PreSubmitted',)
    #
    # def push_orderstatus(self, msg):
    #     # Cancelled and Submitted with Filled = 0 can be pushed immediately
    #     try:
    #         order = self.orderbyId[msg.orderId]
    #     except KeyError:
    #         return  # not found, it was not an order
    #
    #     if msg.status == self.SUBMITTED and msg.filled == 0:
    #         if order.status == order.Accepted:  # duplicate detection
    #             return
    #
    #         order.accept(self)
    #         self.notify(order)
    #
    #     elif msg.status == self.CANCELLED:
    #         # duplicate detection
    #         if order.status in [order.Cancelled, order.Expired]:
    #             return
    #
    #         if order._willexpire:
    #             # An openOrder has been seen with PendingCancel/Cancelled
    #             # and this happens when an order expires
    #             order.expire()
    #         else:
    #             # Pure user cancellation happens without an openOrder
    #             order.cancel()
    #         self.notify(order)
    #
    #     elif msg.status == self.PENDINGCANCEL:
    #         # In theory this message should not be seen according to the docs,
    #         # but other messages like PENDINGSUBMIT which are similarly
    #         # described in the docs have been received in the demo
    #         if order.status == order.Cancelled:  # duplicate detection
    #             return
    #
    #         # We do nothing because the situation is handled with the 202 error
    #         # code if no orderStatus with CANCELLED is seen
    #         # order.cancel()
    #         # self.notify(order)
    #
    #     elif msg.status == self.INACTIVE:
    #         # This is a tricky one, because the instances seen have led to
    #         # order rejection in the demo, but according to the docs there may
    #         # be a number of reasons and it seems like it could be reactivated
    #         if order.status == order.Rejected:  # duplicate detection
    #             return
    #
    #         order.reject(self)
    #         self.notify(order)
    #
    #     elif msg.status in [self.SUBMITTED, self.FILLED]:
    #         # These two are kept inside the order until execdetails and
    #         # commission are all in place - commission is the last to come
    #         self.ordstatus[msg.orderId][msg.filled] = msg
    #
    #     elif msg.status in [self.PENDINGSUBMIT, self.PRESUBMITTED]:
    #         # According to the docs, these statuses can only be set by the
    #         # programmer but the demo account sent it back at random times with
    #         # "filled"
    #         if msg.filled:
    #             self.ordstatus[msg.orderId][msg.filled] = msg
    #     else:  # Unknown status ...
    #         pass
    #
    # def push_execution(self, ex):
    #     self.executions[ex.m_execId] = ex
    #
    # def push_commissionreport(self, cr):
    #     with self._lock_orders:
    #         ex = self.executions.pop(cr.m_execId)
    #         oid = ex.m_orderId
    #         order = self.orderbyId[oid]
    #         ostatus = self.ordstatus[oid].pop(ex.m_cumQty)
    #
    #         position = self.getposition(order.data, clone=False)
    #         pprice_orig = position.price
    #         size = ex.m_shares if ex.m_side[0] == 'B' else -ex.m_shares
    #         price = ex.m_price
    #         # use pseudoupdate and let the updateportfolio do the real update?
    #         psize, pprice, opened, closed = position.update(size, price)
    #
    #         # split commission between closed and opened
    #         comm = cr.m_commission
    #         closedcomm = comm * closed / size
    #         openedcomm = comm - closedcomm
    #
    #         comminfo = order.comminfo
    #         closedvalue = comminfo.getoperationcost(closed, pprice_orig)
    #         openedvalue = comminfo.getoperationcost(opened, price)
    #
    #         # default in m_pnl is MAXFLOAT
    #         pnl = cr.m_realizedPNL if closed else 0.0
    #
    #         # The internal broker calc should yield the same result
    #         # pnl = comminfo.profitandloss(-closed, pprice_orig, price)
    #
    #         # Use the actual time provided by the execution object
    #         # The report from TWS is in actual local time, not the data's tz
    #         dt = date2num(datetime.strptime(ex.m_time, '%Y%m%d  %H:%M:%S'))
    #
    #         # Need to simulate a margin, but it plays no role, because it is
    #         # controlled by a real broker. Let's set the price of the item
    #         margin = order.data.close[0]
    #
    #         order.execute(dt, size, price,
    #                       closed, closedvalue, closedcomm,
    #                       opened, openedvalue, openedcomm,
    #                       margin, pnl,
    #                       psize, pprice)
    #
    #         if ostatus.status == self.FILLED:
    #             order.completed()
    #             self.ordstatus.pop(oid)  # nothing left to be reported
    #         else:
    #             order.partial()
    #
    #         if oid not in self.tonotify:  # Lock needed
    #             self.tonotify.append(oid)
    #
    # def push_portupdate(self):
    #     # If the IBStore receives a Portfolio update, then this method will be
    #     # indicated. If the execution of an order is split in serveral lots,
    #     # updatePortfolio messages will be intermixed, which is used as a
    #     # signal to indicate that the strategy can be notified
    #     with self._lock_orders:
    #         while self.tonotify:
    #             oid = self.tonotify.popleft()
    #             order = self.orderbyId[oid]
    #             self.notify(order)
    #
    # def push_ordererror(self, msg):
    #     with self._lock_orders:
    #         try:
    #             order = self.orderbyId[msg.id]
    #         except (KeyError, AttributeError):
    #             return  # no order or no id in error
    #
    #         if msg.errorCode == 202:
    #             if not order.alive():
    #                 return
    #             order.cancel()
    #
    #         elif msg.errorCode == 201:  # rejected
    #             if order.status == order.Rejected:
    #                 return
    #             order.reject()
    #
    #         else:
    #             order.reject()  # default for all other cases
    #
    #         self.notify(order)
    #
    # def push_orderstate(self, msg):
    #     with self._lock_orders:
    #         try:
    #             order = self.orderbyId[msg.orderId]
    #         except (KeyError, AttributeError):
    #             return  # no order or no id in error
    #
    #         if msg.orderState.m_status in ['PendingCancel', 'Cancelled',
    #                                        'Canceled']:
    #             # This is most likely due to an expiration]
    #             order._willexpire = True


## This works
broker = FutuBroker(region="US", trd_env=TrdEnv.REAL)
order = broker.buy(owner=0, data="US.TSLA", size=1, price=400)
time.sleep(5)
broker.cancel(order)