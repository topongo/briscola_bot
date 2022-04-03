from random import shuffle
from typing import Callable
from telebotapi import TelegramBot
from inline_keyboard import InlineKeyboard, gen_inline_markup
from utils import Filter, Condition, wait_for, escape, is_briscola_command, parse_briscola_commands
from emoji import emojize


class GameTelegram:
    from telebotapi import TelegramBot

    def __init__(self, t: TelegramBot, *players: TelegramBot.User):
        self.players = list([PlayerTelegram(u, 4, self) for u in players])
        self.master = players
        if len(self.players) == 1:
            raise TypeError("you can't play by yourself")
        if len(self.players) == 3:
            raise NotImplementedError("3 players game not yet implemented")
        self.teams = len(self.players) == 4
        self.t = t
        self.master = self.players[0]
        self.game = None

    def run(self):
        sent_msgs = {}
        for n, i in enumerate(self.players):
            sent_msgs[i.user.id] = i.send_welcome(self.t, self.master)

        conds = []
        ok = []
        to_delete = []

        # @@@@@@@@@@@@
        ok.append(self.players[1].user.id)
        ok.append(self.players[0].user.id)
        # @@@@@@@@@@@@

        def clb(msg):
            self.t.answerCallbackQuery(msg, "Ok!")
            if len(ok) == len(self.players):
                return
            if msg.from_.id not in ok:
                to_delete.append(
                    self.t.sendMessage(msg.from_,
                                       "Perfetto! Attendi che anche gli altri giocatori confermino."
                                       )
                )
                ok.append(msg.from_.id)

        conds.append(Condition(
            Filter(lambda l: l.from_.id in map(lambda j: j.user.id, self.players)),
            Filter(lambda l: l.original_message.id == sent_msgs[l.from_.id].id),
            Filter(lambda l: l.data == "g_start"),
            callback=clb
        ))

        conds.append(Condition(
            Filter(lambda l: l.from_.id in [i_.user.id for i_ in self.players]),
            Filter(lambda l: len(ok) == len(self.players)),
            Filter(lambda l: l.data == "g_start"),
            stop_return=True
        ))

        if wait_for(self.t, *conds):
            for i in sent_msgs:
                self.t.deleteMessage(sent_msgs[i])
            for i in to_delete:
                self.t.deleteMessage(i)
            for i in self.players:
                i.send_mess(self.t, "Tutti i giocatori hanno accettato,"
                                    " che la partita abbia inizio!")

        # now the game actually begins
        def clb_send_interface(g: Game, p: Player):
            if not isinstance(p, PlayerTelegram) or not isinstance(g, Game):
                raise TypeError(p, g)
            on_table = ""
            if len(g.table):
                for pl, ca in g.table.items():
                    on_table += f"\n - @{pl.user.username}: {g.represent_card(ca)}"
            else:
                on_table = "\n "

            """
            p.info = f"È il turno di @{p.user.username}\n" \
                     f"Le tue carte:\n - " + \
                     "\n - ".join([g.represent_card(ca) for ca in p.cards]) + \
                     f"\nCarte in gioco:" + on_table
            """
            p.info = f"È il turno di @{p.user.username}\n" + \
                     f"Carte in gioco:" + on_table + "\nLe tue carte:"
            p.send_interface(self.t, g)

        def clb_fetch(p: Player, t: TelegramBot, g: Game):
            if not isinstance(p, PlayerTelegram):
                raise TypeError(p)

            return p.ask_for_card(g, t,
                                  extra_conds=(Condition(
                                      Filter(lambda l: l.from_.id in [u.user.id for u in g.players]),
                                      Filter(lambda l: is_briscola_command(l.text)),
                                      Filter(lambda l: parse_briscola_commands(l.text)[0] == "stop"),
                                      callback=lambda l: t.answerCallbackQuery(l, "Shame on you, ma ok."),
                                      stop_return=-1
                                  ),))

        self.game = Briscola(*self.players)
        self.game.play(self.t, clb_send_interface, clb_fetch)


class Card:
    def __init__(self, seed, number, alias=None):
        self.seed = seed
        self.number = number
        self.alias = alias

    def __str__(self):
        if self.alias:
            return f"{self.alias} di {self.seed}"
        else:
            return f"{self.number} di {self.seed}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.seed == other.seed and self.number == self.number


class Player:
    def __init__(self, m_c: int):
        self.cards = []
        self.max_cards = m_c
        self.points = 0
        self.info = ""

    def add(self, c: Card):
        if len(self.cards) > self.max_cards:
            raise OverflowError(f"Players can't have more than {self.max_cards} cards")
        self.cards.append(c)

    def remove(self, c: Card):
        self.cards.remove(c)

    def add_points(self, p):
        self.points += p

    def points(self):
        return self.points

    def fetch_card(self, *args, **kwargs):
        pass


class Game:
    def __init__(self, *p: Player):
        self.players = list(p)
        self.deck = []
        self.finished = False
        self.table = {}

    def end(self) -> list[tuple[Player, int, bool]]:
        out = []
        winner = max(self.players, key=lambda l: l.points)
        for p in self.players:
            out.append(
                (p, p.points, p is winner)
            )
        return out

    def gen_deck(self):
        pass

    def draw(self):
        pass

    def winner(self):
        pass

    def setup(self):
        pass

    def represent_card(self, c: Card):
        return ""

    def gen_info(self, p: Player):
        pass


class Briscola(Game):
    SEEDS = ["Spade", "Denari", "Coppe", "Bastoni"]
    NUMBERS = list(range(1, 11))
    ALIASES = {
        1: "Asse",
        8: "Fante",
        9: "Cavallo",
        10: "Re"
    }
    SCORES = {
        1: 11,
        8: 2,
        9: 3,
        10: 4
    }
    EMOJIS = {
        "Spade": ":crossed_swords:",
        "Denari": ":money_bag:",
        "Coppe": ":trophy:",
        "Bastoni": ":wood:"
    }

    def __init__(self, *players: Player):
        if len(players) > 4:
            raise TypeError("Can't play at vanilla briscola in more than 4 players.")
        elif len(players) == 3:
            raise NotImplementedError("Can't yet play with 3 players")
        super().__init__(*players)

        self.gen_deck()
        self.briscola = None
        self.first = self.players[0]
        self.playing = self.players[0]
        self.setup()

    def gen_deck(self):
        for s in self.SEEDS:
            for n in self.NUMBERS:
                if n in self.ALIASES:
                    self.deck.append(Card(s, n, self.ALIASES[n]))
                else:
                    self.deck.append(Card(s, n))
        shuffle(self.deck)

    def setup(self):
        for _ in range(3):
            for p in self.players:
                p.add(self.deck.pop(0))
        self.briscola = self.deck.pop(0)

    def _player_ordered(self):
        ind = self.players.index(self.first)
        for i in range(len(self.players)):
            yield self.players[(ind + i) % len(self.players)]

    def draw(self):
        for p in self._player_ordered():
            p.add(self.deck.pop())

    def represent_card(self, c: Card):
        return emojize(f"{c} {self.EMOJIS[c.seed]}")

    def turn_winner(self) -> tuple[Player, Card, int]:
        w_p, w_c = list(self.table.items())[0]
        p = 0
        if w_c.number in self.SCORES:
            p += self.SCORES[w_c.number]
        lead = w_c.seed
        for pl, c in self.table[1:]:
            if w_c.seed == self.briscola and c.seed == self.briscola and c.number > w_c.number:
                w_p, w_c = pl, c
            else:
                if c.seed == self.briscola:
                    w_p, w_c = pl, c
                else:
                    if c.seed == lead and c.number > w_c.number:
                        w_p, w_c = pl, c
        return w_p, w_c, p


    def play(self, t: TelegramBot, callback_send_info: Callable[[Game, Player], None],
             callback_fetch: Callable[[Player, TelegramBot, Game], int]):
        def send_interface():
            for pl in self.players:
                callback_send_info(self, pl)

        send_interface()
        while True:
            self.table = {}
            for p in self._player_ordered():
                self.playing = p
                c_ind = callback_fetch(p, t, self)
                if c_ind == -1:
                    self.end()
                    return
                self.table[p] = p.cards.pop(c_ind)
                send_interface()
            # every player has thrown their card
            self.end_turn()


    def gen_info(self, p: Player):
        return f""


class PlayerTelegram(Player):
    def __init__(self, user: TelegramBot.User, m_c: int, t_game: GameTelegram):
        super().__init__(m_c)
        self.user = user
        self.keyboard = None
        self.interface = None
        self.t_game = t_game

    def send_interface(self, t: TelegramBot, g: Game):
        self.keyboard = InlineKeyboard()
        for n, c in enumerate(self.cards):
            self.keyboard.add_row(InlineKeyboard.InlineKeyboardButton(g.represent_card(c), str(n)))

        args = {
            "body": escape(self.info),
            "reply_markup": gen_inline_markup(self.keyboard)
        }
        if not self.interface:
            self.interface = t.sendMessage(self.user, **args)
        else:
            try:
                t.editMessageText(self.interface, **args)
            except TelegramBot.GenericQueryException:
                self.interface = t.sendMessage(self.user, **args)

    def send_welcome(self, t: TelegramBot, master):
        self.keyboard = InlineKeyboard()
        self.keyboard.add_row(InlineKeyboard.InlineKeyboardButton("Inizia!", "g_start"))
        return t.sendMessage(self.user,
                             f"La partita proposta da @{master.user.username} sta per iniziare, premi il "
                             f"tasto qui sotto per iniziare.",
                             reply_markup=gen_inline_markup(self.keyboard))

    def send_mess(self, t: TelegramBot, txt, **other):
        t.sendMessage(self.user, txt, **other)

    def ask_for_card(self, g: Game, t: TelegramBot, extra_conds=None):
        if extra_conds is None:
            extra_conds = []

        ret = wait_for(t,
                       Condition(
                           Filter(lambda l: l.from_.id == self.user.id),
                           Filter(lambda l: l.original_message.id == self.interface.id),
                           Filter(lambda l: 0 <= int(l.data) <= len(self.cards)),
                           stop_return=lambda l: int(l.data),
                           callback=lambda l: t.answerCallbackQuery(l, f"Hai messo il "
                                                                    f"{g.represent_card(self.cards[int(l.data)])}!")
                       ),
                       *extra_conds
                       )
        if ret == -1:
            for pl in [pla for pla in g.players if pla is not self]:
                t.sendMessage(pl, f"@{pl.user.username} si è arreso. Purtroppo la partite finisce qui.")
            return -1
        else:
            return ret
