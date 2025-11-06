from playingcardsplus.MultiplayerGames.dealer import Dealer, DealerBehavior
# from playingcardsplus.custom_error import DealerUnassignedError

import pytest


def test_dealer_creation():
    normal_behavior = DealerBehavior(name="Normal Fair", fair=True)
    dealer = Dealer(name="Ordinary Dealer", initial_behavior=normal_behavior)
    pass

def test_dealer_run_without_game_assignment_fails():
    pass

def test_dealer_game_assignment_toggle_fails():
    pass


def test_dealer_soul_actions():
    """
    Test to see if soul's conditions to change
    """
    pass
