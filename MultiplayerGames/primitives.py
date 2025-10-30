"""
Defines primitive objects such as Player, Game, and Dealer

InstructionSet objects are needed for players to make decisions

Each entity should be communicating via a specific data fields so they may be hosted in different instances.
For being hosted on multiple envs, eventually need to support each entity communicating through various protocols like HTTPS, RPC, etc...
"""

from ..deck import Card, AbstractDeck
from ..custom_error import DuplicateCardError, DeckInlclusionError, UnrecognizedCardError, DealerUnassignedError, GameUnassignedError

from typing import Optional, Any, List, DefaultDict, Dict, OrderedDict, Deque, Iterable, Tuple
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, PrivateAttr, NonNegativeInt


class PlayerDecision_InstructionSet(BaseModel):
    operations: DefaultDict
    # (K,V) function = instruction op, decision function

class Player(BaseModel, ABC):
    """
    Player object where name is immutable. Behavior - defined by AI can be modified each hand
    """
    name: str = Field(frozen=True)
    _hand: DefaultDict[Card, NonNegativeInt] = PrivateAttr(DefaultDict[Card, NonNegativeInt](int)) # How many of a given card does one have? - this way, we can track multi-decks and have it encodes
    _score: int = 0
    _behavior: Dict[str, Any] = PrivateAttr() # this is where you can plug-in some behavior - like an AI model or rules-based object wrapper
    # Player behavior can be parametrized by location of the model, specific rules-based criteria per game, etc...

    # Accept a dealt card - must be called by a Dealer
    @property
    def hand(self) -> DefaultDict[Card, NonNegativeInt]:
        return self._hand

    @property
    def score(self) -> int:
        return self._score

    @property #TODO: further access control? - only game devs and simulation runners need control
    def behavior(self) -> Dict[str, Any]:
        return self._behavior

    @hand.setter
    def _accept_card(self, cards: Dict):
        """list of cards come ordered in a way it should be accepting them"""
        for card, count in cards.items():
            self._hand[card] += count

    @score.setter
    def _update_score(self, new_points: int):
        self._score += new_points

    @behavior.setter
    def _update_behavior(self, new_behavior: Dict[str, Any]):
        # exact logic for triggering this should be controlled by game devs
        self._behavior = new_behavior

    # TODO: Need to think about data structure that it grabs - specifically for cheat_codes
    # TODO: should this directly call AI agent or make a ping to the agent, which should be grabbing the data on its own and retrieve the decision?
    @abstractmethod
    def take_action(self, crucial_game_state: Dict, historical_state: Iterable[Dict], cheat_codes: Optional[Any]) -> Iterable[PlayerDecision_InstructionSet]:
        """
        Abstract method to be implemented by subclasses.

        Takes in crucial information about the game itself to make a judgment & past information to make msot judgments.
        It can take in information that woould be normally considered cheating if it knew (cheat_code) - ie. knowing placement of specific cards

        Returns a specific action that the Game/Dealer needs to look at and take action.
        """
        ...

class MultiPlayerDeck(AbstractDeck):
    # TODO: creating visibility over this can allow Dealer to cheat, let's make sure the condition for this is set? so only cheeating can operate it?
    _unused: Deque[Card] = PrivateAttr(Deque[Card]()) # Make it LIFO - OrderedDict is by defaulkt but making last=True just in case
    _board: OrderedDict[Card, bool] = PrivateAttr(OrderedDict[Card, bool]()) # Make it LIFO
    _trash_pile: Deque[Card] = PrivateAttr(Deque[Card]()) # Make it LIFO
    _player_hands: OrderedDict[Card, bool] # Just track what cards are distriburted amongst players. This way the dealer doesn't have to track who has what hands
    _dealer_assigned: bool #TODO: is this necessary? I thin keventually this has to be some kind of handshake auth thing btw dealer and deck

    @property
    def unused(self) -> Deque[Card]:
        return self._unused

    @property
    def board(self) -> OrderedDict[Card, bool]:
        return self._board

    @property
    def trash_pile(self) -> Deque[Card]:
        return self._trash_pile

    @property
    def player_hands(self) -> OrderedDict[Card, bool]:
        return self._player_hands

    @property
    def dealer_assigned(self) -> bool:
        return self.__dealer_assigned

    @dealer_assigned.setter
    def _assign_dealer(self):
        self.__dealer_assigned = True

    @dealer_assigned.setter
    def _unassign_dealer(self):
        self.__dealer_assigned = False

    # *** Below functions are meant to be used by the Dealer to figure out what cards go from where to where
    @unused.setter
    def _take_from_unused(self, used_count: NonNegativeInt) -> Deque[Card]: # When updating the Deck, this is the first or second thing that needs to occur
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        # TODO: it's uncertain yet whether it needs to handle how it's being used here and match it againt instruction sets or this be done elsewhere
        used = Deque[Card]()
        for i in range(used_count):
            used.append(self._unused.pop())
            #TODO: might have to use a condition here that checks card for Deck Recognition - ie.does the deck include joker or not?
        return used

    @unused.setter
    def _replenish_unused(self, replenishers: List[Card]): # This doesn't handle duplicates, IF it happens, then it's a problem with the Deck initiation and potential cheating
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in replenishers[::-1]:
            self._unused.appendleft(card)


    @board.setter
    def _remove_from_board(self, removed: OrderedDict[Card, bool]) -> OrderedDict[Card, bool]: #TODO: THIS forces to create some sort of aggregate List, let's see if it's efficient or it's better to list it othersie
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        removed_cards = OrderedDict[Card, bool]()
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
    def _add_to_board(self, added: Iterable[Card]):
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in added: #
            if self._board[card] is True: # how can you add it if it's already there?
                raise DuplicateCardError()
            self._board[card] = True


    @trash_pile.setter
    def _burn_trash(self, burn_count: NonNegativeInt) -> Deque[Card]: #
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        burnt = Deque[Card]()
        for i in range(burn_count):
            burnt.append(self._trash_pile.pop())
            #TODO: might have to use a condition here that checks card for Deck Recognition - ie.does the deck include joker or not?
        return burnt

    @trash_pile.setter
    def _add_trash(self, trashed: Iterable[Card]):
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in trashed:
            self._trash_pile.append(card)


    @player_hands.setter
    def _take_from_players(self, removed: OrderedDict[Card, bool]) -> OrderedDict[Card, bool]:
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        taken_cards = OrderedDict[Card, bool]()
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
    def _give_to_players(self, distributed: Iterable[Card]):
        if self._dealer_assigned is False:
            raise DealerUnassignedError()
        for card in distributed:
            if self._player_hands[card] is True: # how can you add it if it's already there?
                raise DuplicateCardError()
            self._player_hands[card] = True

    # #TODO: it's unclear actually if this is necessary at all
    # def deal(self, player, cards_per_player): # Dealing should call above functions?
    #     return

class DealerBehavior(BaseModel):
    """
    Defines a behavior that a dealer can take. Normally, it should be instantiated within the Game object so it can track Players

    Enables devs to control whether devs are fair or treats certain players favorably or unfavorably

    For example:
    #    Behaviors:
    #       -> (fair) Default: No info other than Deck & Player count
    #       -> (Unfair) Favoritism: Uses card ordering to advantage certain players
    #       -> (Unfair) Ijime/Bully: Uses card ordering to disadvantage certain players

    Once a "Soul" is attached, it may change its fairness and favored/unfavored player based on its "mood"
    #   - "Soul" attachable:
    #       -> can be paramterized in a way where it really dislikes/likes players or this maybe fickle
    #       -> but a sense of justice may over-ride
    #
    """
    name: str = Field(frozen=True)
    fair: bool = True # If not fair then it also can look up card ordering
    liked_players: Optional[List[Player]]
    disliked_players: Optional[List[Player]]
    soul: Optional[Dict]

class Dealer(BaseModel, ABC):
    """
    Dealer comes in to any Game and should deal based on rules dictated by the Game, which gives the Dealer status about the Game.
    Assumes that the Game object is acting in good faith and is correct.

    When players communicate their action - in instruction sets, Dealers actually execute. When they execute, they're reading getters and setters in MultiPlayerDeck
    """
    #TODO: need a way to track and verify here that a Dealer is indeed dealing for a specific game
    #TODO: And that it has indeed received status about the Game from the Game object

    name: str = Field(frozen=True)
    _behavior: DealerBehavior
    _game_assigned: bool = False # TODO: prob will eventually have to become some sort of handshake/signature signing auth thing

    @property
    def behavior(self) -> DealerBehavior:
        return self._behavior

    @property
    def game_assigned(self) -> bool:
        return self._game_assigned

    # @behavior.setter
    # def update_behavior(self, new_behavior: DealerBehavior): # might lead to bad practices... Most changes should be programmed to the Soul
    #     self._behavior = new_behavior

    @game_assigned.setter
    def __assign_game(self):
        self._game_assigned = True

    @game_assigned.setter
    def _unassign_game(self):
        self._game_assigned = False

    #TODO: making sure these are only callable by the Game Object
    @abstractmethod
    def _deal(self, players: Iterable[Player], rules: Dict[Any, Any], deck: MultiPlayerDeck) -> Tuple[MultiPlayerDeck, Iterable[Player]]:
        """
        Deals cards to the players + set up the board conditions

        Args:
            players: A list of Player objects to deal to.
            cards_per_player: The number of cards each player should receive.

        Returns:
            A tuple containing the new deck and each Player
        """
        ...

    @abstractmethod #TODO: may not need to be abstract because rules may not be relevant here... or structure is pre-determined
    def _handle_player_actions(self, player: Player, actions: Iterable[PlayerDecision_InstructionSet], deck: MultiPlayerDeck, rules: Dict[Any, Any]):
        """
        For each action that a Player takes, execute those based on the provided rules then update the Deck
        """
        ...



# TODO: let's make a separate DS for roster?
#   -> circular & ordered - so you can quick rotating whose turn it is
#   -> has max & min capacity - determined by Game rule...
#   -> Current index preserving - so we know whose turn it is
#   -> O(n) iteration, O(1) lookup - mwah
#   -> can append or remove - because a player might leave at some point?
class TurnBasedCircularList:
    """
    A circular iterable with features for managing size, direction, and turns.
    """


# class CollectibleData(BaseModel):
#     #TODO: each player action follows one another and the palyer makes an action also based on the previous player's action - but prob ok
#     actions_per_hand: Dict[Player, List[str]] # What did each player do at each hand
#     score_change_per_hand: DefaultDict[Player, List[int]] # what was their score each hand
#     deck_state_per_hand: Any #TODO: prob need a better interface here - what did the board look like at each hand
#     player_behavior_state_per_hand: Optional[Dict[Player, List[Any]]]
#     dealer_behavior_state_per_hand: Optional[List[Any]]
#     # Hand starts at index 0, where Dealer has just dealt cards, then Player takes action.
#     # Index 1 after the Dealer has taken acount of Players' actions and then made changes to the Deck accordingly
#     # Index i so on...
#     # Until Index L (last hand): where it's after the dealer deals but now the stop conditions have been met - based on the rule

#     # Types of analysis to be done are going to be
#     # 1) Why did a player take a certain action? (& what would've been optimal for their goal) -> refernce each index at a time
#     # 2) When was it determined that a particular Player would win -> reference each index at a time then calculate odds based on deck status and what not



class Game(BaseModel, ABC):
    """
    Game object is the primary interface for running games.
    It should makes sure
    1) The Deck, while the Game is being played is only accessible to the designated Dealer
    2) Maintains a Roster and their Score at each hand of the game
    3) Enforces rules across the game by sending it to Dealers while making sure Dealer's functions are only accessible for the Game obj to run

    Game object is the interface that simulators will be interfacing with. They will call public Object functions that are intuitive - start_game, next_hand, etc...

    Game devs will be writing the code for this per Game. It takes 4 tasks to accomplish this
    -> Create rules
    -> Design instruction set
    -> Define player action types
    -> Define scoring logic

    Implements private/protected function to be used by public functions
    """
    name: str = Field(frozen=True)
    dealer: Dealer #should Dealer be swappable?
    decks: List[MultiPlayerDeck] = Field(frozen=True) # there can be multiple decks & immutable
    roster: Iterable[Player] #TODO: actually it needs to be circular so we can maintain order of playing
    rules: DefaultDict[Any, Any]
    scoreboard: DefaultDict[Player, int]  # Score should be kept by the Game. Trust this over
    game_data_path: str
    # 2) next round
    #   -> signal dealer to hand
    #   -> deck status update
    #   -> signal
    #
    # 3) Trigger Players for action
    #   -> signal players w/current deck situation read from the Deck
    #   -> wait for player actions/trigger it for simulation purposes
    #   -> incorporate player decisions
    #   -> deck status updates
    # 4) keep score
    #
    #

    # to be called by simulators
    def start_game(self): # return data to be stored for analyzing results later
        # Assign Game / Auth Dealer for the game
        print(self.dealer.game_assigned)
        self.dealer.__assign_game
        print(self.dealer.game_assigned)

        # Send rules, deck to dealer & Deal first hand (_deal shoul do the status update for the deck)
        hand_0, player_states_0 = self.dealer._deal(players=self.roster, rules=self.rules, deck=self.decks[0])

        # Data storage needs to reference each hand at a time.
        data_0 = {
            "action_score_hand": DefaultDict[str, Tuple[str, int, DefaultDict[Card, int](int)]](),
            "deck": {
                "unused": DefaultDict[Card, int](int), #TODO: turning this into a list only works for single deck
                "board": DefaultDict[Card, int](int),
                "trash_pile": DefaultDict[Card, int](int)
            },
            "player_behavior": {
                #TODO: storing this?
            },
            "dealer_behavior": "" # TODO: how to store this?
        }

        for player in self.roster: # TODO: once this becomes circular, it'll need a way to convert to a simple List
            data_0["action_score_hand"][player.name] = {"", player.score, player.hand} # list only works for single deck -> should just become

        for deck in self.decks:
            for card in deck.unused:
                data_0["deck"]["unused"][card] += 1
            for card, adder in deck.board.items():
                data_0["deck"]["board"][card] += adder
            for card in deck.trash_pile:
                data_0["deck"]["trash_pile"][card] += 1

        # data_0["player_behavior"] : {}
        # data_0["dealer_behavior"] = 0

        #TODO: write to a JSON file/DB somewhere

    def next_hand(self): #
        # Trigger player action
        for player in self.roster: #whatever is list equivalent version of it
            action_instructions = player.take_action(crucial_game_state: Dict, historical_state: Iterable[Dict], cheat_codes: Optional[Any])
            self.dealer._handle_player_actions(player=player, actions=action_instructions, deck=self.deck, rules=self.rules)

        # Dealer handles those
        # record data and then return
        return

    # functions hapepning beneathe - more functional than they are chronological
    def _keep_score(self):
        pass

    def _trigger_dealer(self):
        pass

    def _keep_score(self):
        pass
