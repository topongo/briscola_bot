from telebotapi import TelegramBot
from utils import *
from inline_keyboard import *


class Briscola:
    def __init__(self, t: TelegramBot, *players: TelegramBot.User):
        self.players = list([Player(u) for u in players])
        self.master = players
        if len(self.players) == 1:
            raise TypeError("you can't play by yourself")
        if len(self.players) == 3:
            raise NotImplementedError("3 players game not yet implemented")
        self.teams = len(self.players) == 4
        self.t = t
        self.master = self.players[0]

    def run(self):
        sent_msgs = {}
        for n, i in enumerate(self.players):
            sent_msgs[i.user.username] = i.send_welcome(self.t, self.master)

        conds = []
        ok = []
        to_delete = []

        def clb(msg):
            self.t.answerCallbackQuery(msg, "Ok!")
            if len(ok) == len(self.players):
                return
            if msg.from_.username not in ok:
                to_delete.append(
                    TelegramBot.Update.Message.detect_type(
                        None,
                        self.t.sendMessage(msg.from_,
                                           "Perfetto! Attendi che anche gli altri giocatori confermino.")
                    )[0]
                )
                ok.append(msg.from_.username)

        conds.append(Condition(
            Filter(lambda l: l.from_.username in map(lambda j: j.user.username, self.players)),
            Filter(lambda l: l.original_message.id == sent_msgs[l.from_.username]),
            Filter(lambda l: l.data == "g_start"),
            callback=clb
        ))

        conds.append(Condition(
            Filter(lambda l: l.from_.username in [i_.user.username for i_ in self.players]),
            Filter(lambda l: len(ok) == len(self.players)),
            Filter(lambda l: l.data == "g_start"),
            stop_return=True
        ))

        if wait_for(self.t, *conds):
            for i in to_delete:
                self.t.deleteMessage(i)
            for i in self.players:
                i.send_mess(self.t, "Tutti i giocatori hanno accettato,"
                                    " che la partita abbia inizio!")

        # now the game actually begins





class Player:
    def __init__(self, user: TelegramBot.User):
        self.user = user
        self.interface = InlineKeyboard()

    def send_keyboard(self, t: TelegramBot):
        t.sendMessage(self.user, "Test", reply_markup=gen_inline_markup(self.interface))

    def send_welcome(self, t: TelegramBot, master):
        self.interface.add_row(InlineKeyboard.InlineKeyboardButton("Inizia!", "g_start"))
        return TelegramBot.Update.Message.detect_type(
            None,
            t.sendMessage(self.user, f"La partita proposta da @{master.user.username} sta per iniziare, premi il "
                                     f"tasto qui sotto per iniziare.",
                          reply_markup=gen_inline_markup(self.interface)))[0].id

    def send_mess(self, t: TelegramBot, txt, **other):
        t.sendMessage(self.user, txt, **other)



