from telebotapi import TelegramBot
from utils import *
from inline_keyboard import *


class Game:
    def __init__(self, t: TelegramBot, *players: TelegramBot.User):
        self.players = list([Player(u) for u in players])
        self.teams = len(self.players) == 4
        self.t = t

    def run(self):
        for i in self.players:
            i.send_keyboard(self.t)


class Player:
    def __init__(self, user: TelegramBot.User):
        self.user = user
        self.interface = InlineKeyboard()

    def send_keyboard(self, t: TelegramBot):
        t.sendMessage(self.user, "Test", reply_markup=escape(dumps(self.interface.send())))



