from telebotapi import TelegramBot
from time import sleep
from datetime import datetime, timedelta
from json import dumps

t = TelegramBot("5129062759:AAHiYep3v1IcU8DBHU69qphiEuWmsFlbQgM")
t.bootstrap()


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


def send_help(ch_, pref):
    t.sendMessage(ch_, escape(f"{pref}\nMALEPORCO DETTO SCRIVI L'HELP QUI"))


def is_command(args_, *matches):
    for i_ in matches:
        if args_[0].lower() == i_:
            return True


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


x = InlineKeyboard()
x.add_row(InlineKeyboard.InlineKeyboardButton("Asso di bastoni", "1"),
          InlineKeyboard.InlineKeyboardButton("Asso di denari", "2"),
          InlineKeyboard.InlineKeyboardButton("Asso di picche", "5"))
x.add_row(InlineKeyboard.InlineKeyboardButton("No, wait...", "4"))
print(x.send())


while True:
    for up in t.get_updates():
        try:
            if not hasattr(up, "content"):
                print(dumps(up.raw, indent=4))
                print(up.content.type)
                continue
            fr = up.content.from_
            ch = up.content.chat
            txt = up.content.text
            ms_id = up.content.id
            print(txt.split(" ")[0] != "!briscola")
            if txt.split(" ")[0] != "!briscola":
                continue
            else:
                if len(txt.split(" ")) == 1 or len(txt.split(" ")[1]) == 0:
                    args = []
                else:
                    args = txt.split(" ")[1:]
            print(fr, ch, txt, args, up.content.entities)
            print()
            print(up.content.raw)
            print()
        except Exception as e:
            raise e

        if len(args) == 0:
            send_help(ch, "Nessun comando inviato, ecco come usare il bot:\n")

        elif is_command(args, "newgame", "new_game"):
            if len(args) == 1:
                print(f"Not enough arguments for a new game")
            else:
                t.sendMessage(ch, escape(f"Bene, ora {comma_and(args[1:])} moriranno di cacca addosso",))

        elif is_command(args, "test"):
            t.sendMessage(ch, escape("Testing InlineKeyboards, ladies and gentlemen:"),
                          a={
                              "reply_markup": dumps({
                                  "inline_keyboard": x.send(),
                                  "reply_to_message_id": ms_id
                              })
                          },
                          parse_mode="HTML")

    sleep(1)
