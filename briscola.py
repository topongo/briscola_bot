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
            if isinstance(up.content, TelegramBot.Update.Message):
                fr = up.content.from_
                ch = up.content.chat
                txt = up.content.text
                ms = up.content

                if (args := parse_briscola_commands(txt)) is None:
                    continue
            else:
                continue
        except Exception as e:
            raise e

        if len(args) == 0:
            send_help(ch, "Nessun comando inviato, ecco come usare il bot:\n")

        elif is_command(args, "newgame", "new_game"):
            if len(args) == 0:
                t.sendMessage(ch, "Non puoi giocare da solo!", reply_to_message=ms)
            elif len(args) > 4:
                t.sendMessage(ch, "Non puoi giocare in piu' di 4 persone!", reply_to_message=ms)
            else:
                players = [fr.username]
                for i in (j.replace("@", "") for j in args[1:]):
                    if i not in players:
                        players.append(i)

                apply_form = InlineKeyboard()
                apply_form.add_row(
                    InlineKeyboard.InlineKeyboardButton("Accetta", "a"),
                    InlineKeyboard.InlineKeyboardButton("Rifiuta", "c")
                )
                apply_form.add_row(
                    InlineKeyboard.InlineKeyboardButton("Inizia Partita", "_s")
                )

                joined = {
                    players[0]: True
                }

                def body():
                    return escape(
                        f"{comma_and(players, at_=True)} "
                        f"cliccate su uno dei pulsanti per accettare"
                        f" o rifiutare.\n\n"
                        f"Risposte: {len(joined)}/{len(players)}\n"
                        f"Affermative: {len([k for k, i_ in joined.items() if i_])}/{len(joined)}"
                    )

                m_sent = \
                    TelegramBot.Update.Message.detect_type(None,
                                                           {
                                                               "message":
                                                                   t.sendMessage(ch, body(),
                                                                                 reply_markup=gen_inline_markup(
                                                                                     apply_form, ms.id
                                                                                 ))["result"]
                                                           })[0]

                conds = []

                for n, i in enumerate(players):
                    fils = (
                        (
                            lambda l: l.from_.username,
                            lambda l: l in players
                        ),
                        (
                            lambda l: l.original_message.id,
                            lambda l: l == m_sent.id
                        ),
                        (
                            lambda l: l.data,
                            lambda l: l[0] != "_"
                        )
                    )


                    def clb(msg):
                        mod = False
                        if msg.data == "a":
                            try:
                                if joined[msg.from_.username]:
                                    t.answerCallbackQuery(msg, "Sei gia' iscritto!")
                                else:
                                    joined[msg.from_.username] = True
                                    t.answerCallbackQuery(msg, "Ora sei iscritto alla partita!")
                                    mod = True
                            except KeyError:
                                joined[msg.from_.username] = True
                                t.answerCallbackQuery(msg, "Ora sei iscritto alla partita!")
                                mod = True
                        else:
                            try:
                                if not joined[msg.from_.username]:
                                    t.answerCallbackQuery(msg, "Hai gia' rifiutato l'invito.")
                                else:
                                    joined[msg.from_.username] = False
                                    t.answerCallbackQuery(msg, "Hai rifiutato l'invito.")
                                    mod = True
                            except KeyError:
                                joined[msg.from_.username] = False
                                t.answerCallbackQuery(msg, "Hai rifiutato l'invito.")
                                mod = True

                        if mod:
                            t.editMessageText(msg.original_message,
                                              body(),
                                              reply_markup=gen_inline_markup(apply_form, ms.id))


                    conds.append(
                        (fils, False, clb)
                    )

                def clb_start(msg):
                    if msg.from_.username != players[0]:
                        t.answerCallbackQuery(msg, "Non puoi avviare la partita, non sei amministratore")
                    else:
                        if len(joined) == 1:
                            t.answerCallbackQuery(msg, "Troppi pochi giocatori!")
                        elif len(joined) == 3:
                            t.answerCallbackQuery(msg, "Partite in 3 giocatori non sono (ancora) supportate!")
                        else:
                            t.answerCallbackQuery(msg, "Partita avviata in privato!")
                            link_to_private = InlineKeyboard()
                            link_to_private.add_row(
                                InlineKeyboard.InlineKeyboardButton("Vai in chat.",
                                                                    url=f"tg://user?id={t}")
                            )
                            t.sendMessage(ch, "Partita avviata in privato!",
                                          reply_to_message=m_sent,
                                          reply_markup=gen_inline_markup(link_to_private, ms.id)
                                          )


                conds.append(
                    (
                        (
                            (
                                lambda l: l.from_.username,
                                lambda l: l == players[0]
                            ),
                            (
                                lambda l: l.original_message.id,
                                lambda l: l == m_sent.id
                            ),
                            (
                                lambda l: l.data,
                                lambda l: l == "_s"
                            )
                        ),
                        False,
                        clb_start
                    ))

                wait_for(t, *conds)

        elif is_command(args, "test"):
            t.sendMessage(ch, escape("Testing InlineKeyboards, ladies and gentlemen:"),
                          reply_markup=gen_inline_markup(x, ms.id),
                          parse_mode="HTML")

    sleep(1)
