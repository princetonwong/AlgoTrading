from telethon import TelegramClient, events, sync
import logging

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

def getRecentMessages(id, limit):
    while True:
        with client:
            getmessage = client.get_messages(id, limit=limit)
            for message in getmessage:
                print(message.message)

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

while True:
    def realtimeGetNewMessages(id):
        @client.on(events.NewMessage(chats=id))
        async def my_event_handler(event):
            print(event.raw_text)
    realtimeGetNewMessages(myself)

    client.start()
    client.run_until_disconnected()