from typing import Callable

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
            "callback": i[1],
            "filter": i[0],
            "stop": i[1]
        })

    def do(callback_, stop_, mess_):
        callback_(mess_)
        if stop_:
            return True

    def confront(u_, get_prop_, filter_prop_, callback_, stop_):
        try:
            if filter_prop_(get_prop_(u_.content)):
                return do(callback_, stop_, u_.content)
        except AttributeError:
            pass

    while True:
        for u in t.get_updates():
            for c in cond:
                for f in c["filter"]:
                    if confront(u, f[0], f[1], c["callback"], c["stop"]):
                        return
            if ender:
                if ender(None):
                    return

