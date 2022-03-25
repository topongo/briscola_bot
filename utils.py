from typing import Callable
from time import sleep
from telebotapi import TelegramBot


def comma_and(_list):
    if len(_list) == 0:
        return "Nessuno"
    elif len(_list) == 1:
        return _list[0]
    elif len(_list) == 2:
        return " e ".join(_list)
    else:
        return ", ".join(_list[:-1]) + f" e {_list[-1]}"


def escape(text):
    return text.replace("_", "\\_").replace("*", "\\*")


def is_command(args_, *matches):
    for i_ in matches:
        if args_[0].lower() == i_:
            return True


def wait_for(t: TelegramBot, *conditions: tuple[iter, bool, Callable], ender=None):
    cond = []
    for i in conditions:
        cond.append({
            "callback": i[2],
            "filter": i[0],
            "stop": i[1]
        })

    def do(callback_, mess_):
        callback_(mess_)

    def confront(mess_, get_prop_, filter_prop_):
        try:
            return filter_prop_(get_prop_(mess_))
        except AttributeError:
            print("Exception caught")
            return False

    print()
    print()
    print()
    while True:
        for u in t.get_updates():
            print(u.raw)
            for c in cond:
                if all(map(lambda l: confront(u.content, l[0], l[1]), c["filter"])):
                    c["callback"](u.content)
                    if c["stop"]:
                        return
        if ender:
            if ender(None):
                return
        sleep(1)


def parse_briscola_commands(txt):
    key = ["", "!briscola", "!br"][is_briscola_command(txt)]

    if len(txt) == 0 or len(txt.split(" ")) == 0 or txt.split(" ")[0] != key:
        return
    return txt.split(" ")[1:]


def is_briscola_command(txt) -> int:
    if len(txt) >= 9:
        if txt[:9] == "!briscola":
            return 1
        else:
            return 0
    elif len(txt) >= 3:
        if txt[:3] == "!br":
            return 2
        else:
            return 0
    else:
        return 0
