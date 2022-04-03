from typing import Callable
from time import sleep
from telebotapi import TelegramBot
from copy import deepcopy
from datetime import datetime, timedelta
from inspect import getsource


def comma_and(list_, at_):
    list__ = [f"@{i}" for i in deepcopy(list_)]
    if len(list__) == 0:
        return "Nessuno"
    elif len(list__) == 1:
        return list__[0]
    elif len(list__) == 2:
        return " e ".join(list__)
    else:
        return ", ".join(list__[:-1]) + f" e {list__[-1]}"


def escape(text):
    out = text
    for i in ("_", "*"):
        out = out.replace(i, f"\\{i}")
    return out


def is_command(args_, *matches):
    for i_ in matches:
        if args_[0].lower() == i_:
            return True


class Filter:
    def __init__(self, comparer: Callable):
        self.comparer = comparer

    def call(self, msg):
        try:
            return self.comparer(msg)
        except AttributeError:
            print("Exception caught")
            return False

    def __str__(self):
        return f"Filter(\"{getsource(self.comparer).strip()}\""

    def __repr__(self):
        return str(self)


class Condition:
    def __init__(self, *filters: Filter, callback=lambda l: None, stop_return=None):
        self.callback = callback
        self.stop_return = stop_return
        self.filters = list(filters)

    def add_filter(self, *f):
        for i in f:
            self.filters.append(i)

    def meet(self, msg):
        return all(map(lambda l: l.call(msg), self.filters))

    def __str__(self):
        return f"Condition(\n    filters=[\n        " + ",\n        ".join(map(lambda l: str(l), self.filters))\
               + f"\n    ],\n    callback=\"{self.callback}\"," \
                 f"\n    stop_return={self.stop_return}\n)"

    def __repr__(self):
        return str(self)


def wait_for(t: TelegramBot,
             *conditions: Condition,
             timeout=300):

    t.daemon.delay = 0.5

    timeout_end = datetime.now() + timedelta(seconds=timeout)

    while True:
        for u in t.get_updates():
            for c in conditions:
                if c.meet(u.content):
                    c.callback(u.content)
                    if c.stop_return is not None:
                        if isinstance(c.stop_return, Callable):
                            return c.stop_return(u.content)
                        else:
                            return c.stop_return
        if timeout_end < datetime.now():
            return False
        sleep(0.1)


def parse_briscola_commands(txt):
    key = ["", "!briscola", "!br"][is_briscola_command(txt)]

    if len(txt) == 0 or len(txt.split(" ")) == 0 or txt.split(" ")[0] != key:
        return
    return txt.split(" ")[1:]


def is_briscola_command(txt) -> int:
    if len(txt) >= 9:
        if txt[:9] == "!briscola":
            return 1
    if len(txt) >= 3:
        if txt[:3] == "!br":
            return 2
    return 0
