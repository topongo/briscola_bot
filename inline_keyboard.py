from utils import *
from json import dumps


class InlineKeyboard:
    class InlineKeyboardRow:
        def __init__(self, *buttons):
            self.data = []
            self.add_button(*buttons)

        def add_button(self, *buttons):
            for i in buttons:
                if isinstance(i, InlineKeyboard.InlineKeyboardButton):
                    self.data.append(i)
                    print(self.data)

        def send(self):
            o = []
            for i in self.data:
                d = {"text": i.text}
                if i.data:
                    d["callback_data"] = i.data
                if i.url:
                    d["url"] = i.url
                o.append(d)
            return list(o)

    class InlineKeyboardButton:
        def __init__(self, text, callback_data=None, url=None,):
            self.text = text
            self.data = callback_data
            self.url = url

            if not (self.url or self.data):
                raise TypeError("at least one of url or callback_data arguments must be supplied")

    def __init__(self):
        self.data = []

    def add_row(self, *buttons):
        self.data.append(InlineKeyboard.InlineKeyboardRow(*buttons))

    def send(self):
        return list([i.send() for i in self.data])


def gen_inline_markup(inline, m_i):
    return escape(dumps({
        "inline_keyboard": inline.send(),
        "reply_to_message_id": m_i
    }))
