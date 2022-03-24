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
            return list([{"text": i.text, "callback_data": i.data} for i in self.data])

    class InlineKeyboardButton:
        def __init__(self, text, callback_data=None):
            self.text = text
            self.data = callback_data

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
