from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.dealer import Dealer, DealerBehavior
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.game import Game

from playingcardsplus.custom_error import GameUnassignedError

import pytest


# def test_game_creation():
#     deck = MultiPlayerDeck(name="French_Multi_Player_Deck_NoJocker", joker_count=0)
#     normal_behavior = DealerBehavior(name="Normal Fair", fair=True)
#     dealer = Dealer(name="Ordinary Dealer", initial_behavior=normal_behavior)

#     rules = Rules(

#     )

#     game = Game()



# class TestGameCreation(unittest.TestCase):
#     def create_game(self):
#         # assert Game creation states like Dealer,  Deck, Roster scoreboard
#         pass
#     def rotate_roster(self): # Ds check
#         pass
