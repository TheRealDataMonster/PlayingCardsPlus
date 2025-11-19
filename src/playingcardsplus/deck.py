"""
Defines appropriate objects and functions for a Regular Card Deck
"""

from playingcardsplus.utils import create_french_cards
from playingcardsplus.card import Card, JokerCard


import random  # Should be replaced for thread-safety and/or cryptogrraphic security of the random seed
from abc import ABC
from typing_extensions import List
from enum import Enum
from pydantic import BaseModel, computed_field, NonNegativeInt, ConfigDict


class DeckType(str, Enum):
    FRENCH="french"
    # GERMAN="german"

CardCountMap = {
    DeckType.FRENCH: 52
}


class AbstractDeck(BaseModel, ABC):
    """
    An immutable Pydantic model for a deck of cards.

    The `cards` attribute is a tuple, which is immutable.
    Methods that modify the deck return a new `Deck` instance.
    """

    model_config = ConfigDict(frozen=True)
    name: str
    type: DeckType = DeckType.FRENCH
    joker_count: NonNegativeInt # In multi-host/decentralized env, this needs to be sent from the Game

    # Don't Actually need to store anythign because the actual interfaces used by Game Devs and Simulators shoulds use
    # -> specific implentations that use the below functions and stores them appropriately
    # ->
    #
    @computed_field
    @property
    def cards(self) -> List[Card | JokerCard]:
        return create_french_cards(joker_count=self.joker_count)

    @computed_field
    @property
    def shuffled_cards(self) -> List[Card | JokerCard]:
        """Returns a new Deck instance with the cards in a random order."""
        cards = self.cards
        random.shuffle(cards)
        return cards

    def __len__(self) -> int:
        count = 52
        if self.type==DeckType.FRENCH:
            count = 52
        return count + self.joker_count

        #TODO or dimply just


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
