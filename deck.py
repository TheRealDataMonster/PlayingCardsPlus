"""
Defines appropriate objects and functions for a Regular Card Deck
"""

import random # Should be replaced for thread-safety and/or cryptogrraphic security of the random seed
from enum import Enum
from typing import Tuple, Any, Iterable
from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

class Suit(str, Enum):
    """Enumeration for the four suits of a standard deck."""
    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"

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

Card = Tuple[Rank, Suit]


class AbstractDeck(BaseModel, ABC):
    """
    An immutable Pydantic model for a deck of cards.

    The `cards` attribute is a tuple, which is immutable.
    Methods that modify the deck return a new `Deck` instance.
    """
    model_config = ConfigDict(frozen=True)
    name: str
    cards: Iterable[Card]

    def shuffle(self) -> "AbstractDeck":
        """Returns a new Deck instance with the cards in a random order."""
        shuffled_cards = list(self.cards)
        random.shuffle(shuffled_cards)
        return type(self)(name=self.name, cards=tuple(shuffled_cards))

    @abstractmethod
    def deal(self, *args: Any, **kwargs: Any) -> Tuple["AbstractDeck", Iterable[Card]]:
        """
        Abstract method to be implemented by subclasses.

        Returns a new Deck instance and a list of dealt cards.
        """
        ...

# class SinglePlayerDeck(AbstractDeck):
#     """A concrete deck with standard top-of-deck dealing logic. Serves as an example for how to overwrite deal()"""
#     # TODO: make sure that when you add dealt cards and undealt cards, you get both
#     dealt_cards: Deque[Card] = PrivateAttr(Deque[Card]())
#     undealt_cards: OrderedDict[Card, bool]

#     def deal(self, num_cards: int) -> Tuple["SinglePlayerDeck", Iterable[Card]]:
#         """Deals from the top of the deck, returning a new deck and the dealt cards."""
#         if num_cards > len(self.undealt_cards):
#             raise ValueError(
#                 f"Cannot deal {num_cards} cards; only {len(self.cards)} remain."
#             )

#         dealt_cards = list(self.cards[:num_cards])
#         remaining_cards = self.cards[num_cards:]

#         return StandardDeck(cards=remaining_cards), dealt_cards
