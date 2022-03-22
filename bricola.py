from telebotapi import TelegramBot
from time import sleep
from datetime import datetime, timedelta

t = TelegramBot("5129062759:AAHiYep3v1IcU8DBHU69qphiEuWmsFlbQgM")
t.bootstrap()

while True:
    for i in t.get_updates():
        try:
            fr = i.content.from_
            ch = i.content.chat
            txt = i.content.text
            if i.content
        except AttributeError:
            continue

    sleep(1)
