from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.card import Color

from collections import Counter

CLUBS = "♣"
DIAMONDS = "♦"
HEARTS = "♥"
SPADES = "♠"

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

def test_french_multiplayer_deck_creation():
    """
    Test for the following
    1) Creation done well = Same 52 cards as specified above with no duplicates
    2) Distribution makes sense - unused, board, player hands, trash pile add up to cards
    """
    deck = MultiPlayerDeck(
        name="French_Multi_Player_Deck_NoJocker",
        joker_count=0
    )
    # 1) Same 52 cards, no duplicates
    assert(len(deck) == 52)
    assert(Counter(deck.cards) == Counter(__french_deck))
    assert(Counter(deck.unused) == Counter(__french_deck))

    # 2) Things add up!
    print(Counter(deck.unused))
    assert(Counter(deck.cards) == (
        Counter(deck.unused) + Counter(deck.trash_pile) +
        Counter(deck.board) + Counter(deck.player_hands)
    ))

def test_french_multiplayer_deck_creation_with_jokers():
    """
    Test for the following
    1) Creation done well = Same 54 cards as specified above with no duplicates
    2)
    """
    deck = MultiPlayerDeck(
        name="French_Multi_Player_Deck_Joker",
        joker_count=2
    )
    # Same 54 cards, no duplicates
    assert(len(deck)==54)
    __french_with_joker = set()
    __french_with_joker.update(__french_deck)

    i = 1
    while i <= 2:
        for color_member in Color:
            __french_with_joker.add((color_member.value, i))
            i+=1
            if i > 2:
                break

    assert(Counter(deck.cards) == Counter(__french_with_joker))

# TODO:
# class TestDeckActions(unittest.TestCase):
#     # TODO: bunch of functions like Deck taking actions with/without Dealer assigned + Dealer assigned functions do work properly as intended
#     # TODO: hacking Dealer assignment without Game assignment -> should fail
#     # TODO: unassigning Dealer without proper validation
#     pass
#





# if __name__ == "__main__":
#     print("hi")
