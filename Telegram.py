from telethon import TelegramClient, events, sync
import logging
import re
from CustomAPI.FutuAPI import FutuAPI; futuapi = FutuAPI()
from futu import TrdSide, OrderType, TrdEnv
import pandas as pd

def defaultLogging():
    logger = logging.getLogger("BookletsGeneration")
    format = '%(asctime)s [%(levelname)s] %(message)s'
    formatter = logging.Formatter(format)
    logging.basicConfig(level=logging.DEBUG, format=format, datefmt='%d/%m/%Y %H:%M:%S', filename="_log/debug.log")
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    ch2 = logging.FileHandler("_log/warning.log")
    ch2.setLevel(logging.WARNING)
    ch2.setFormatter(formatter)
    logging.getLogger('').addHandler(ch)
    logging.getLogger('').addHandler(ch2)

# These example values won't work. You must get your own api_id and api_hash from https://my.telegram.org, under API Development.
name = "Testing"
api_id = 2934476
api_hash = 'a30c1aaeb0e990c018399e0ce50f461c'
algolab = -1001478581063
myself = 432454473
client = TelegramClient(name, api_id, api_hash)

TRADINGENVIRONMENT = TrdEnv.REAL
TICKER = "HK.MHImain"
QUANTITY = 1
THRESHOLD = 10

def buy(price):
    logging.info(f"Buying MHImain at most {price + THRESHOLD}")
    result = futuapi.placeFutureOrder(price=price + THRESHOLD, quantity=QUANTITY, code=TICKER, tradeSide=TrdSide.BUY, orderType=OrderType.NORMAL, tradeEnvironment=TRADINGENVIRONMENT)
    return result

def sell(price):
    logging.info(f"Selling MHImain at least {price + THRESHOLD}")
    result = futuapi.placeFutureOrder(price=price - THRESHOLD, quantity=QUANTITY, code=TICKER, tradeSide=TrdSide.SELL, orderType=OrderType.NORMAL, tradeEnvironment=TRADINGENVIRONMENT)
    return result

def close(price):
    global result
    logging.info(f"Closing MHImain around {price}")
    df = futuapi.queryCurrentPositions(tradingEnvironment=TRADINGENVIRONMENT).to_dict("records")
    for record in df:
        if record["code"] == TICKER:
            quantity = record["quantity"]
            if record["position_side"] == "LONG":
                result = buy(price, quantity)
            elif record["position_side"] == "SHORT":
                result = sell(quantity)
            else:
                result = f"Having position, but cannot close."
        else:
            result = f"I am not holding {TICKER}, so cannot close position"
    return result
                
def parseMessageAndTrade(message):
    try:
        parsed = re.search(r"MultiCharts64 Alert: Strategy 01 generated '(.*) @(.*)' at (.*) on (.*) \((.*) Minutes\)(.*)", message)
        actionKey, price, ticker = parsed.group(1), int(parsed.group(2)), parsed.group(5)
        logging.info(f"{actionKey, price}")
        return actionKey, price
    except:
        logging.warning(f"Cannot parse message '{message}'")


def tradeByActionkey(actionKey, price):
    global tradeResult
    if actionKey == "Close Position":
        tradeResult = close(price)
    elif actionKey == "Buy":
        tradeResult = buy(price)
    elif actionKey == "Short":
        tradeResult = sell(price)
    else:
        logging.warning(f"Cannot trade {actionKey}")
    if type(tradeResult) is pd.DataFrame:
        records = tradeResult.to_dict("records")
        for record in records:
            if record["code"] == TICKER:
                orderStatus = record["order_status"]
                quantity = record["quantity"]
                tradeSide = record["trd_side"]
                price = record["price"]
                logging.info(f"{orderStatus}: {tradeSide}ING {TICKER} @{price} x {quantity}")
    elif type(tradeResult) is str:
        logging.warning(tradeResult)
    return tradeResult

def getRecentTelegramMessages(id, limit):
    with client:
        getmessage = client.get_messages(id, limit=limit)
        for message in getmessage[2:3]:
            text = message.message
            print(text)
            # try:
            key, price = parseMessageAndTrade(text)
            tradeResult = tradeByActionkey(key, price)
            print (tradeResult)
            # except:
            #     pass

def someOtherNotes():
    async def main():
        # # Getting information about yourself
        # me = await client.get_me()
        #
        # # "me" is a user object. You can pretty-print
        # # any Telegram object with the "stringify" method:
        # print(me.stringify())
        #
        # # When you print something, you see a representation of it.
        # # You can access all attributes of Telegram objects with
        # # the dot operator. For example, to get the username:
        # username = me.username
        # print(username)
        # print(me.phone)

        # You can print all the dialogs/conversations that you are part of:
        async for dialog in client.iter_dialogs():
            print(dialog.name, 'has ID', dialog.id)

        # messages = await client.get_messages(-1001478581063)
        # print (messages)

    with client:
        client.loop.run_until_complete(main())



if __name__ == "__main__":
    defaultLogging()
    # getRecentTelegramMessages(algolab, limit=5)
    while True:
        def realtimeGetNewMessages(id):
            @client.on(events.NewMessage(chats=id))
            async def my_event_handler(event):
                text = event.raw_text
                logging.info(f"Received telegram message '{event.raw_text}'")
                key, price = parseMessageAndTrade(text)
                tradeResult = tradeByActionkey(key, price)
                print(tradeResult)

        realtimeGetNewMessages(myself)
        client.start()
        client.run_until_disconnected()