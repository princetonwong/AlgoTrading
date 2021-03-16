from telethon import TelegramClient, events, sync
import logging
import re
from CustomAPI.FutuAPI import FutuAPI; futuapi = FutuAPI()
from futu import TrdSide, OrderType, TrdEnv
import pandas as pd
import Keys
from CustomAPI.Logger import defaultLogging

# These example values won't work. You must get your own api_id and api_hash from https://my.telegram.org, under API Development.
name = "Testing"
client = TelegramClient(name, Keys.Telegram_api_id, Keys.Telegram_api_hash)

class TGController(object):
    def __init__(self, traadingEnvironment=TrdEnv.SIMULATE, threshold=0.0001):
        self.tradingEnvironment = traadingEnvironment
        self.threshold = threshold

    def trade(self, price, ticker, quantity: int, tradeSide: TrdSide, orderType=OrderType.NORMAL):
        attributes = list()
        isFuture = False
        isHK = False
        isUS = False
        if "main" in ticker: isFuture = True
        if "HK." in ticker: isHK = True
        if "US." in ticker: isUS = True
        print (isFuture, isHK, isUS)

        coef = 1 if tradeSide == TrdSide.BUY else -1
        price = price * (1 + self.threshold * coef)

        if isHK and not isFuture: quantity = quantity * futuapi.getReference(ticker, "lot_size")

        if tradeSide == TrdSide.BUY:
            logging.info(f"Selling {quantity} {ticker} @ least {price}")
        else:
            logging.info(f"Buying {quantity} {ticker} @ most {price}")

        if isFuture:
            price = int(price)
            result = futuapi.placeFutureOrder(price=price, quantity=quantity, ticker=ticker, tradeSide=tradeSide,
                                              orderType=orderType, tradeEnvironment=TrdEnv.REAL)
        elif isHK:
            result = futuapi.placeHKOrder(price=price, quantity=quantity, ticker=ticker,tradeSide=tradeSide,
                                          orderType=orderType, tradeEnvironment=self.tradingEnvironment)
        elif isUS:
            result = futuapi.placeUSOrder(price=price, quantity=quantity, ticker=ticker, tradeSide=tradeSide,
                                          orderType=orderType, tradeEnvironment=self.tradingEnvironment)
        else:
            result = TypeError

        return result

    def close(self, price, ticker, orderType=OrderType.NORMAL):
        global result
        logging.info(f"Closing MHImain around {price}")
        df = futuapi.queryCurrentPositions(tradingEnvironment=self.tradingEnvironment).to_dict("records")
        for record in df:
            if record["code"] == ticker:
                quantity = record["quantity"]
                if record["position_side"] == "LONG":
                    result = self.trade(price, ticker, quantity, TrdSide.BUY, orderType)
                elif record["position_side"] == "SHORT":
                    result = self.trade(price, ticker, quantity, TrdSide.SELL, orderType)
                else:
                    result = f"Having position, but cannot close."
            else:
                result = f"I am not holding {ticker}, so cannot close position"
        return result

    def parseMessageAndTrade(self, message):
        try:
            parsed = re.search(r"MultiCharts64 Alert: Strategy 01 generated '(.*) @(.*)' at (.*) on (.*) \((.*) Minutes\)(.*)", message)
            action, price, tickerString = parsed.group(1), int(parsed.group(2)), parsed.group(4)
            ticker = "HK.MHImain" if tickerString == "MHI_IB" else tickerString
            logging.info(f"message parsed as: {action, price, ticker}")
            return (action, price, ticker)
        except:
            logging.warning(f"Cannot parse message '{message}', try next parsing")
        try:
            parsed = re.search(r"MultiCharts64 Alert: Alert for VENUS generated 'VENUS_(.*) @(.*)' at (.*) on (.*) \((.*) Minute\)(.*)", message)
            action, price, tickerString = parsed.group(1), int(parsed.group(2)), parsed.group(4)
            if action == "Buy":
                action = "Buy"
            elif action == "Short":
                action = "Short"
            elif action == "Close Buy Postion" or action == "Close Short Position":
                action = "Close Position"
            ticker = "HK.MHImain" if tickerString == "HSIG1" else tickerString
            logging.info(f"message parsed as:{action, price, ticker}")
            return action, price, ticker
        except:
            logging.warning(f"Cannot parse message '{message}', try next parsing")
        try:
            parsed = re.search(r"Python-Tg Alert P4: generated P4 (.*) Signal @(.*) on (.*)", message)
            action, price, tickerString = parsed.group(1), int(parsed.group(2)), parsed.group(3)
            if action == "BUY":
                action = "Buy"
            elif action == "SHORT":
                action = "Short"
            elif action == "COVER" or action == "SELL":
                action = "Close Position"
            ticker = "HK.MHImain" if "HSI" in tickerString else tickerString
            logging.info(f"message parsed as:{action, price, ticker}")
            return action, price, ticker
        except:
            logging.warning(f"Cannot parse message '{message}'")

    def tradeByActionkey(self, parsed):
        global tradeResult
        action, price, ticker = parsed
        quantity = 1

        if action == "Close Position":
            tradeResult = self.close(price, ticker)
        elif action == "Buy":
            tradeResult = self.trade(price, ticker, quantity, TrdSide.BUY)
        elif action == "Short":
            tradeResult = self.trade(price, ticker, quantity, TrdSide.SELL)
        else:
            logging.warning(f"Cannot trade {action}")
        if type(tradeResult) is pd.DataFrame:
            records = tradeResult.to_dict("records")
            for record in records:
                if record["code"] == ticker:
                    orderStatus = record["order_status"]
                    quantity = record["qty"]
                    tradeSide = record["trd_side"]
                    price = record["price"]
                    logging.info(f"{orderStatus}: {tradeSide}ING {ticker} @{price} x {quantity}")
        elif type(tradeResult) is str:
            logging.warning(tradeResult)
        return tradeResult

    def getRecentTelegramMessages(self, id, limit):
        with client:
            getmessage = client.get_messages(id, limit=limit)
            for message in getmessage:
                text = message.message
                print(text)
                try:
                    key, price = self.parseMessageAndTrade(text)
                    tradeResult = self.tradeByActionkey(key, price)
                    print (tradeResult)
                except:
                    pass

    def getInfoAboutMyself(self):
        async def main():
            me = await client.get_me()
            print(me.stringify())
            print(me.username)
            print(me.phone)

        with client:
            client.loop.run_until_complete(main())

    def getAllDialogs(self):
        async def main():
            # You can print all the dialogs/conversations that you are part of:
            async for dialog in client.iter_dialogs():
                print(dialog.name, 'has ID', dialog.id)
        with client:
            client.loop.run_until_complete(main())


if __name__ == "__main__":
    defaultLogging()
    tg = TGController()
    while True:
        def realtimeGetNewMessagesFrom(id):
            @client.on(events.NewMessage(chats=id))
            async def my_event_handler(event):
                text = event.raw_text
                logging.info(f"Received TG message: '{text}'")
                parsed = tg.parseMessageAndTrade(text)
                tradeResult = tg.tradeByActionkey(parsed)
                logging.info(tradeResult)
        # realtimeGetNewMessagesFrom(Keys.Telegram_Shuttlealgo)
        # realtimeGetNewMessagesFrom(Keys.Telegram_algolab)
        realtimeGetNewMessagesFrom(Keys.Telegram_Princeton)
        realtimeGetNewMessagesFrom(Keys.Telegram_TinTinTrader)
        client.start()
        client.run_until_disconnected()
