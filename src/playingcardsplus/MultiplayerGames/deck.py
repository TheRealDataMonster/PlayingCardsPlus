from playingcardsplus.card import Card, JokerCard
from playingcardsplus.deck import AbstractDeck
from playingcardsplus.custom_error import (
    DuplicateCardError,
    DeckInlclusionError,
    UnrecognizedCardError,
    DealerUnassignedError
)

from enum import Enum
from typing_extensions import List, OrderedDict, Deque, Iterable, Self
from pydantic import PrivateAttr, NonNegativeInt, model_validator


class Distributee(str, Enum):
    PLAYER="player"
    BOARD="board"
    TRASH_PILE="trash_pile"
    UNUSED="unused"


class MultiPlayerDeck(AbstractDeck):
    # TODO: making sure we can track when Dealers or Game cheats?
    __unused: Deque[Card | JokerCard] = PrivateAttr(
        Deque[Card | JokerCard]()
    )  # Make it LIFO
    __board: OrderedDict[Card | JokerCard, bool] = PrivateAttr(
        OrderedDict[Card | JokerCard, bool]()
    )  # Make it LIFO
    __trash_pile: Deque[Card | JokerCard] = PrivateAttr(
        Deque[Card | JokerCard]()
    )  # Make it LIFO
    __player_hands: OrderedDict[Card | JokerCard, bool] = PrivateAttr(
        OrderedDict[Card | JokerCard, bool]()
    )  # Just track what cards are distriburted amongst players. This way the dealer doesn't have to track who has what hands
    __dealer_assigned: bool = PrivateAttr(default=False)  # TODO: eventually this has to be some kind of handshake auth thing btw dealer and deck

    @model_validator(mode="after")
    def __move_cards_to_unused(self) -> Self:
        self.__unused = Deque[Card | JokerCard](self.shuffled_cards)
        return self

    @property
    def unused(self) -> Deque[Card | JokerCard]:
        return self.__unused

    @property
    def board(self) -> OrderedDict[Card | JokerCard, bool]:
        return self.__board

    @property
    def trash_pile(self) -> Deque[Card | JokerCard]:
        return self.__trash_pile

    @property
    def player_hands(self) -> OrderedDict[Card | JokerCard, bool]:
        return self.__player_hands

    @property
    def dealer_assigned(self) -> bool:
        return self.__dealer_assigned

    def _toggle_dealer_assignment(self):
        self.__dealer_assigned = not self.__dealer_assigned


    # *** Below functions are meant to be used by the Dealer to manipulate the deck as needed
    def _take_from_unused(self, used_count: NonNegativeInt) -> Deque[Card | JokerCard]:  # When updating the Deck, this is the first or second thing that needs to occur
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        # TODO: it's uncertain yet whether it needs to handle how it's being used here and match it againt instruction sets or this be done elsewhere
        used = Deque[Card | JokerCard]()
        for i in range(used_count):
            used.append(self.__unused.pop())
            # TODO: might have to use a condition here that checks card for Deck Recognition - ie.does the deck include joker or not?
        return used

    def _replenish_unused(self, replenishers: List[Card | JokerCard]):  # This doesn't handle duplicates, IF it happens, then it's a problem with the Deck initiation and potential cheating
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        for card in replenishers[::-1]:
            self.__unused.appendleft(card)

    def _remove_from_board(self, removed: OrderedDict[Card | JokerCard, bool]) -> OrderedDict[Card | JokerCard, bool]:  # TODO: THIS forces to create some sort of aggregate List, let's see if it's efficient or it's better to list it othersie
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        removed_cards = OrderedDict[Card | JokerCard, bool]()
        for card, remove_status in removed.items():
            if remove_status is True:
                removed_card = self.__board.pop(card, "Not Found")
                if not removed_card:  # Have to remove a card but it's not there?
                    raise DeckInlclusionError()
                if removed_card == "Not Found":  # Card key is not om the board somehow?
                    raise UnrecognizedCardError()
                else:
                    removed_cards[card] = True
        return removed_cards  # this needs to be like reverse of removed

    def _add_to_board(self, added: Iterable[Card | JokerCard]):
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        for card in added:  #
            if self.__board[card] is True:  # how can you add it if it's already there?
                raise DuplicateCardError()
            self.__board[card] = True

    def _burn_trash(self, burn_count: NonNegativeInt) -> Deque[Card | JokerCard]:  #
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        burnt = Deque[Card | JokerCard]()
        for i in range(burn_count):
            burnt.append(self.__trash_pile.pop())
            # TODO: might have to use a condition here that checks card for Deck Recognition - ie.does the deck include joker or not?
        return burnt

    def _add_trash(self, trashed: Iterable[Card | JokerCard]):
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        for card in trashed:
            self.__trash_pile.append(card)

    def _take_from_players(self, removed: OrderedDict[Card | JokerCard, bool]) -> OrderedDict[Card | JokerCard, bool]:
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        taken_cards = OrderedDict[Card | JokerCard, bool]()
        for card, remove_status in removed.items():
            if remove_status is True:
                removed_card = self.__player_hands.pop(card, "Not Found")
                if not removed_card:  # Have to remove a card but it's not there?
                    raise DeckInlclusionError()
                if removed_card == "Not Found":  # Card key is not om the board somehow?
                    raise UnrecognizedCardError()
                else:
                    taken_cards[card] = True
        return taken_cards  # this needs to be like reverse of removed

    def _give_to_players(self, distributed: Iterable[Card | JokerCard]):
        if self.__dealer_assigned is False:
            raise DealerUnassignedError()
        for card in distributed:
            if (
                self.__player_hands[card] is True
            ):  # how can you add it if it's already there?
                raise DuplicateCardError()
            self.__player_hands[card] = True
