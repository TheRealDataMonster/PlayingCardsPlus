from playingcardsplus.card import Card, JokerCard
from playingcardsplus.deck import AbstractDeck
from playingcardsplus.custom_error import DuplicateCardError, DeckInlclusionError, UnrecognizedCardError, DealerUnassignedError

from typing_extensions import List, OrderedDict, Deque, Iterable, Self
from pydantic import PrivateAttr, NonNegativeInt, model_validator


class MultiPlayerDeck(AbstractDeck):
    # TODO: creating visibility over this can allow Dealer to cheat, let's make sure the condition for this is set? so only cheeating can operate it?
    _unused: Deque[Card|JokerCard] = PrivateAttr(Deque[Card|JokerCard]()) # Make it LIFO - OrderedDict is by defaulkt but making last=True just in case
    _board: OrderedDict[Card|JokerCard, bool] = PrivateAttr(OrderedDict[Card|JokerCard, bool]()) # Make it LIFO
    _trash_pile: Deque[Card|JokerCard] = PrivateAttr(Deque[Card|JokerCard]()) # Make it LIFO
    _player_hands: OrderedDict[Card|JokerCard, bool] = PrivateAttr(OrderedDict[Card|JokerCard, bool]()) # Just track what cards are distriburted amongst players. This way the dealer doesn't have to track who has what hands
    _dealer_assigned: bool = False #TODO: is this necessary? I thin keventually this has to be some kind of handshake auth thing btw dealer and deck

    @model_validator(mode='after')
    def move_cards_to_unused(self) -> Self:
        self._unused = Deque[Card|JokerCard](self.shuffled_cards)
        return self

    @property
    def unused(self) -> Deque[Card|JokerCard]:
        return self._unused

    @property
    def board(self) -> OrderedDict[Card|JokerCard, bool]:
        return self._board

    @property
    def trash_pile(self) -> Deque[Card|JokerCard]:
        return self._trash_pile

    @property
    def player_hands(self) -> OrderedDict[Card|JokerCard, bool]:
        return self._player_hands

    @property
    def dealer_assigned(self) -> bool:
        return self._dealer_assigned

    @dealer_assigned.setter
    def _assign_dealer(self):
        self._dealer_assigned = True

    @dealer_assigned.setter
    def _unassign_dealer(self):
        self._dealer_assigned = False

    # *** Below functions are meant to be used by the Dealer to figure out what cards go from where to where

    def _take_from_unused(self, used_count: NonNegativeInt) -> Deque[Card|JokerCard]: # When updating the Deck, this is the first or second thing that needs to occur
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        # TODO: it's uncertain yet whether it needs to handle how it's being used here and match it againt instruction sets or this be done elsewhere
        used = Deque[Card|JokerCard]()
        for i in range(used_count):
            used.append(self._unused.pop())
            #TODO: might have to use a condition here that checks card for Deck Recognition - ie.does the deck include joker or not?
        return used


    def _replenish_unused(self, replenishers: List[Card|JokerCard]): # This doesn't handle duplicates, IF it happens, then it's a problem with the Deck initiation and potential cheating
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in replenishers[::-1]:
            self._unused.appendleft(card)


    @board.setter
    def _remove_from_board(self, removed: OrderedDict[Card|JokerCard, bool]) -> OrderedDict[Card|JokerCard, bool]: #TODO: THIS forces to create some sort of aggregate List, let's see if it's efficient or it's better to list it othersie
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        removed_cards = OrderedDict[Card|JokerCard, bool]()
        for card, remove_status in removed.items():
            if remove_status is True:
                removed_card = self._board.pop(card , "Not Found")
                if not removed_card: # Have to remove a card but it's not there?
                    raise DeckInlclusionError()
                if removed_card == "Not Found": # Card key is not om the board somehow?
                    raise UnrecognizedCardError()
                else:
                    removed_cards[card] = True
        return removed_cards # this needs to be like reverse of removed

    @board.setter
    def _add_to_board(self, added: Iterable[Card|JokerCard]):
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in added: #
            if self._board[card] is True: # how can you add it if it's already there?
                raise DuplicateCardError()
            self._board[card] = True


    @trash_pile.setter
    def _burn_trash(self, burn_count: NonNegativeInt) -> Deque[Card|JokerCard]: #
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        burnt = Deque[Card|JokerCard]()
        for i in range(burn_count):
            burnt.append(self._trash_pile.pop())
            #TODO: might have to use a condition here that checks card for Deck Recognition - ie.does the deck include joker or not?
        return burnt

    @trash_pile.setter
    def _add_trash(self, trashed: Iterable[Card|JokerCard]):
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in trashed:
            self._trash_pile.append(card)


    @player_hands.setter
    def _take_from_players(self, removed: OrderedDict[Card|JokerCard, bool]) -> OrderedDict[Card|JokerCard, bool]:
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        taken_cards = OrderedDict[Card|JokerCard, bool]()
        for card, remove_status in removed.items():
            if remove_status is True:
                removed_card = self._player_hands.pop(card , "Not Found")
                if not removed_card: # Have to remove a card but it's not there?
                    raise DeckInlclusionError()
                if removed_card == "Not Found": # Card key is not om the board somehow?
                    raise UnrecognizedCardError()
                else:
                    taken_cards[card] = True
        return taken_cards # this needs to be like reverse of removed

    @player_hands.setter
    def _give_to_players(self, distributed: Iterable[Card|JokerCard]):
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in distributed:
            if self._player_hands[card] is True: # how can you add it if it's already there?
                raise DuplicateCardError()
            self._player_hands[card] = True
