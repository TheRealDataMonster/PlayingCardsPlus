from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.custom_error import DealerUnassignedError
from playingcardsplus.card import Color

from collections import Counter
from typing_extensions import OrderedDict
import pytest


__french_deck = {
    ("2", "♣"), ("2", "♦"), ("2", "♥"), ("2", "♠"),
    ("3", "♣"), ("3", "♦"), ("3", "♥"), ("3", "♠"),
    ("4", "♣"), ("4", "♦"), ("4", "♥"), ("4", "♠"),
    ("5", "♣"), ("5", "♦"), ("5", "♥"), ("5", "♠"),
    ("6", "♣"), ("6", "♦"), ("6", "♥"), ("6", "♠"),
    ("7", "♣"), ("7", "♦"), ("7", "♥"), ("7", "♠"),
    ("8", "♣"), ("8", "♦"), ("8", "♥"), ("8", "♠"),
    ("9", "♣"), ("9", "♦"), ("9", "♥"), ("9", "♠"),
    ("10", "♣"), ("10", "♦"), ("10", "♥"), ("10", "♠"),
    ("jack", "♣"), ("jack", "♦"), ("jack", "♥"), ("jack", "♠"),
    ("queen", "♣"), ("queen", "♦"), ("queen", "♥"), ("queen", "♠"),
    ("king", "♣"), ("king", "♦"), ("king", "♥"), ("king", "♠"),
    ("ace", "♣"), ("ace", "♦"), ("ace", "♥"), ("ace", "♠"),
}


def test_french_multiplayer_creation():
    """
    Test for the following
    1) Creation done well = Same 52 cards as specified above with no duplicates
    2) Distribution makes sense - unused, board, player hands, trash pile add up to cards
    """
    deck = MultiPlayerDeck(name="French_Multi_Player_Deck_NoJocker", joker_count=0)
    # 1) Same 52 cards, no duplicates
    assert len(deck) == len(__french_deck)
    assert Counter(deck.cards) == Counter(__french_deck)
    assert Counter(deck.unused) == Counter(__french_deck)

    # 2) Things add up!
    assert Counter(deck.cards) == (
        Counter(deck.unused)
        + Counter(deck.trash_pile)
        + Counter(deck.board)
        + Counter(deck.player_hands)
    )

    #TODO: add some that fails


def test_french_multiplayer_creation_with_jokers():
    """
    Test for the following
    1) Creation done well = Same 54 cards as specified above with no duplicates
    2) Distribution makes sense - unused, board, player hands, trash pile add up to cards
    """
    deck = MultiPlayerDeck(name="French_Multi_Player_Deck_Joker", joker_count=2)

    __french_with_joker = set()
    __french_with_joker.update(__french_deck)

    i = 1
    while i <= 2:
        for color_member in Color:
            __french_with_joker.add((color_member.value, i))
            i += 1
            if i > 2:
                break

    # 1) Same 54 cards, no duplicates
    assert len(deck) == len(__french_with_joker)
    assert Counter(deck.cards) == Counter(__french_with_joker)
    assert Counter(deck.unused) == Counter(__french_with_joker)

    # 2) Things add up!
    assert Counter(deck.cards) == (
        Counter(deck.unused)
        + Counter(deck.trash_pile)
        + Counter(deck.board)
        + Counter(deck.player_hands)
    )

@pytest.mark.parametrize("func_name, args, expected_exception, expected_message", [
    ("_take_from_unused", [5], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_replenish_unused", [[]], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_remove_from_board", [OrderedDict()], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_add_to_board", [[]], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_burn_trash", [3], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_add_trash", [[]], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_take_from_players", [OrderedDict()], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
    ("_give_to_players", [[]], DealerUnassignedError, "Dealer has not been assigned to this Deck"),
])
def test_french_multiplayer_deck_manipulation_fails_dealer_unassigned(func_name, args, expected_exception, expected_message):
    """
    Functions that need Dealers assigned need ot fail and raise DealerUnassignedError

    Test for
    1) Make sure dealer is unassigned
    2) Test each manipulation function and see that they raise DealerUnassignedError
    """
    deck = MultiPlayerDeck(name="French_Multi_Player_Deck_NoJoker", joker_count=0)

    # 1) Dealer unassigned
    assert deck.dealer_assigned == False

    #2) Manipulation w/out dealers -> DealerUnassignedError
    func = getattr(deck, func_name)
    with pytest.raises(expected_exception, match=expected_message) as excinfo:
        func(*args)
    assert expected_message == str(excinfo.value)


def test_french_multiplayer_dealer_assignment_toggle_fails():
    """Toggling dealer assignment is not allowed outside of Game object"""
    deck = MultiPlayerDeck(name="French_Multi_Player_Deck_NoJoker", joker_count=0)
    # 1) Dealer unassigned
    assert deck.dealer_assigned == False
    deck.__dealer_assigned = True
    assert deck.dealer_assigned == False
