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
    def __init__(self, traadingEnvironment=TrdEnv.SIMULATE, ticker="HK.02800", quantity=500, threshold=0.0001):
        self.tradingEnvironment = traadingEnvironment
        self.ticker = ticker
        self.quantity = quantity
        self.threshold = threshold

    def buy(self, price, quantity=None):
        if quantity is None:
            quantity = self.quantity
        price = price * int(1+self.threshold) / 98
        logging.info(f"Buying {quantity} {self.ticker} @ most {price}")
        result = futuapi.placeHKOrder(price=price + self.threshold, quantity=quantity, code=self.ticker, tradeSide=TrdSide.BUY, orderType=OrderType.NORMAL, tradeEnvironment=self.tradingEnvironment)
        return result

    def sell(self, price, quantity=None):
        if quantity is None:
            quantity = self.quantity
        price = price * int(1 + self.threshold) / 98
        logging.info(f"Selling {quantity} {self.ticker} @ least {price}")
        result = futuapi.placeHKOrder(price=price - self.threshold, quantity=quantity, code=self.ticker, tradeSide=TrdSide.SELL, orderType=OrderType.NORMAL, tradeEnvironment=self.tradingEnvironment)
        return result

    def close(self, price):
        global result
        logging.info(f"Closing MHImain around {price}")
        df = futuapi.queryCurrentPositions(tradingEnvironment=self.tradingEnvironment).to_dict("records")
        for record in df:
            if record["code"] == self.ticker:
                quantity = record["quantity"]
                if record["position_side"] == "LONG":
                    result = self.sell(price, quantity)
                elif record["position_side"] == "SHORT":
                    result = self.buy(price, quantity)
                else:
                    result = f"Having position, but cannot close."
            else:
                result = f"I am not holding {self.ticker}, so cannot close position"
        return result

    def parseMessageAndTrade(self, message):
        try:
            parsed = re.search(r"MultiCharts64 Alert: Strategy 01 generated '(.*) @(.*)' at (.*) on (.*) \((.*) Minutes\)(.*)", message)
            actionKey, price, ticker = parsed.group(1), int(parsed.group(2)), parsed.group(5)
            logging.info(f"{actionKey, price}")
            return actionKey, price
        except:
            logging.warning(f"Cannot parse message '{message}'")


    def tradeByActionkey(self, actionKey, price):
        global tradeResult
        if actionKey == "Close Position":
            tradeResult = self.close(price)
        elif actionKey == "Buy":
            tradeResult = self.buy(price)
        elif actionKey == "Short":
            tradeResult = self.sell(price)
        else:
            logging.warning(f"Cannot trade {actionKey}")
        if type(tradeResult) is pd.DataFrame:
            records = tradeResult.to_dict("records")
            for record in records:
                if record["code"] == self.ticker:
                    orderStatus = record["order_status"]
                    quantity = record["qty"]
                    tradeSide = record["trd_side"]
                    price = record["price"]
                    logging.info(f"{orderStatus}: {tradeSide}ING {self.ticker} @{price} x {quantity}")
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
                key, price = tg.parseMessageAndTrade(text)
                tradeResult = tg.tradeByActionkey(key, price)
                print(tradeResult)


        realtimeGetNewMessagesFrom(Keys.Telegram_Princeton)
        client.start()
        client.run_until_disconnected()
