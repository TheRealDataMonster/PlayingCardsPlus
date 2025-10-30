# from deck import AbstractDeck, SinglePlayerDeck, Card, Suit, Rank
# from MultiplayerGames.primitives import *


from typing import DefaultDict
import unittest
from collections import defaultdict

from pydantic.types import NonNegativeInt


class TestDeckCreation(unittest.TestCase):
    def createSinglePlayerDeck(self):
        # deck = SinglePlayerDeck(name="single_player_deck1", cards=)
        # Assert that player deck size and they're all unique or they match some hardcoded set
        pass

    def createMultiPlayerDeck(self):
        # deck = MultiPlayerDeck(name="multi_player_deck1", cards=)
        # Assert that player deck size and they're all unique or they match some hardcoded set
        pass

    #
class TestDealerCreation(unittest.TestCase):
    def create_dealer(self):
        #assert Dealer creation states like well defined behavior
        pass

class TestGameCreation(unittest.TestCase):
    def create_game(self):
        # assert Game creation states like Dealer,  Deck, Roster scoreboard
        pass
    def rotate_roster(self): # Ds check
        pass

class TestDeckActions(unittest.TestCase):
    # TODO: bunch of functions like Deck taking actions with/without Dealer assigned + Dealer assigned functions do work properly as intended
    # TODO: hacking Dealer assignment without Game assignment -> should fail
    # TODO: unassigning Dealer without proper validation
    pass

class TestDealerActions(unittest.TestCase):
    # TODO: Deal value check
    # TODO: running with/without Game assignment
    # TODO: unassigning game assignment without proper validation
    # TODO: assigning game without proper validation
    pass


if __name__ == "__main__":
    a = DefaultDict[str, int](int)
    a["hi"] += 1
    a["fre"] = 2
    print(a)
