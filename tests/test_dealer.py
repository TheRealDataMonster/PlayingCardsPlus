from playingcardsplus.MultiplayerGames.dealer import Dealer, DealerBehavior
from playingcardsplus.custom_error import GameUnassignedError

import pytest


def test_dealer_creation():
    normal_behavior = DealerBehavior(name="Normal Fair", fair=True)
    dealer = Dealer(name="Ordinary Dealer", initial_behavior=normal_behavior)

    # Just testing if creation was done well?
    assert dealer.name == "Ordinary Dealer"
    assert dealer.behavior == normal_behavior
    assert dealer.game_assigned == False

    #TODO: add some that fails creation


@pytest.mark.parametrize("func_name, args, expected_exception, expected_message", [
    ("test_action", [], GameUnassignedError, "Game has not been assigned to this Dealer!"),
])
def test_dealer_run_without_game_assignment_fails(func_name, args, expected_exception, expected_message):
    normal_behavior = DealerBehavior(name="Normal Fair", fair=True)
    dealer = Dealer(name="Ordinary Dealer", initial_behavior=normal_behavior)

    # 1) making sure
    assert dealer.game_assigned == False

    # 2) run some action
    func = getattr(dealer, func_name)
    with pytest.raises(expected_exception, match=expected_message) as excinfo:
        func(*args)
    assert expected_message == str(excinfo.value)


def test_dealer_game_assignment_toggle_fails():
    normal_behavior = DealerBehavior(name="Normal Fair", fair=True)
    dealer = Dealer(name="Ordinary Dealer", initial_behavior=normal_behavior)

    assert dealer.game_assigned == False
    dealer.__game_assigned = True
    assert dealer.game_assigned == False

    # # TODO: this is to be done carefully
    # dealer._toggle_game_assignment()
    # assert dealer.game_assigned == True
