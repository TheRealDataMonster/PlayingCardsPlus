from enum import Enum
from typing_extensions import NamedTuple


class Suit(str, Enum):
    """Enumeration for the four suits of a standard deck."""

    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"


class Rank(str, Enum):
    """Enumeration for the ranks of a standard deck."""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "jack"
    QUEEN = "queen"
    KING = "king"
    ACE = "ace"


class Color(str, Enum):
    RED = "red"
    BLACK = "black"
    BLUE = "blue"


class Card(NamedTuple):
    rank: Rank | str
    suit: Suit | str


class JokerCard(NamedTuple):
    color: Color | str
    number: int
