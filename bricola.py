from telebotapi import TelegramBot
from time import sleep
from datetime import datetime, timedelta
from json import dumps
from utils import *
from inline_keyboard import *
from game import *

t = TelegramBot("5129062759:AAHiYep3v1IcU8DBHU69qphiEuWmsFlbQgM")
t.bootstrap()


x = InlineKeyboard()


def send_help(ch_, pref):
    t.sendMessage(ch_, escape(f"{pref}\nMALEPORCO DETTO SCRIVI L'HELP QUI"))


while True:
    for up in t.get_updates():
        try:
            print(dumps(up.raw, indent=4))
            if not hasattr(up, "content"):
                print(dumps(up.raw, indent=4))
                print(up.content.type)
                continue
            if isinstance(up.content, TelegramBot.Update.Message):
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
            else:
                print(up.content.type)
                if up.content.type == "callback_query":
                    print(up.content.chat_instance)
                    x.add_row(InlineKeyboard.InlineKeyboardButton("Ecco un altra riga", "-6"))
                    t.editMessageReplyMarkup(gen_inline_markup(x, up.content.original_message.id),
                                             message=up.content.original_message)

                continue
        except Exception as e:
            raise e

        if len(args) == 0:
            send_help(ch, "Nessun comando inviato, ecco come usare il bot:\n")

        elif is_command(args, "newgame", "new_game"):
            if len(args) == 1:
                print(f"Not enough arguments for a new game")
            else:
                m_sent = TelegramBot.Update.Message.detect_type(None,
                                                             {"message":
                                                                  t.sendMessage(ch, escape(
                                                                      f"{comma_and(args[1:])}"
                                                                      f"rispondete \"ok\" a questo messaggio per"
                                                                      f" iniziare una nuova partita insieme.", )
                                                                                )["result"]
                                                              })[0]

                conds = []
                players = {}

                for i in args[1:]:
                    fils = (
                        (
                            lambda l: l.from_.username,
                            lambda l: l == i.replace("@", "")
                        ),
                        (
                            lambda l: l.reply_from_message.id,
                            lambda l: l == m_sent.id
                        )
                    )

                    def clb(msg):
                        players[msg.from_.username] = ("si" in msg.text.lower() or
                                                       "yes" in msg.text.lower() or
                                                       "ok" in msg.text.lower())
                    conds.append(
                        (fils, False, clb)
                    )

                wait_for(t, *conds, ender=lambda l: len(players) == len(args[1:]))

        elif is_command(args, "test"):
            t.sendMessage(ch, escape("Testing InlineKeyboards, ladies and gentlemen:"),
                          reply_markup=gen_inline_markup(x, ms_id),
                          parse_mode="HTML")

    sleep(1)
