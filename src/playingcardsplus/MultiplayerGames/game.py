"""
Defines primitive objects such as Player, Game, and Dealer

InstructionSet objects are needed for players to make decisions

Each entity should be communicating via a specific data fields so they may be hosted in different instances.
For being hosted on multiple envs, eventually need to support each entity communicating through various protocols like HTTPS, RPC, etc...
"""

from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.dealer import Dealer
from playingcardsplus.MultiplayerGames.player import Player
# from playingcardsplus.custom_error import DuplicateCardError, DeckInlclusionError, UnrecognizedCardError, DealerUnassignedError

from typing_extensions import TypedDict, Dict, Tuple, List
from abc import ABC, abstractmethod
from sqlalchemy import True_
from pydantic import BaseModel, Field, ConfigDict



# On hold as it's not certain if it's necessary. Might be if it starts becoming used for actual game development and security and exactness is a concern
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

    Game devs will be writing code for this per Game. It takes 4 tasks to accomplish this
    -> Create rules
    -> Design instruction set
    -> Define player action types
    -> Define scoring logic

    Implements private/protected function to be used by public functions
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(frozen=True)
    dealer: Dealer  # should Dealer be swappable?
    decks: List[MultiPlayerDeck] = Field(frozen=True)  # there can be multiple decks & immutable
    roster: List[Player]  # TODO: make it circular so we can maintain order of playing?
    rules: Dict[str, str] = Field(frozen=True)
    scoreboard: Dict[Player, int]  # Score should be kept by the Game. Trust this over what players keep track of - they're motivated by their behavior profiles in simulations and in real games, they may be conflated
    game_data_path: str # where to store data about the game - up to devs to decide how to manage this


    # *** Dealer & Game Assignments
    def assign_dealer(self): #TODO: does this work?
        for deck in self.decks:
            deck._toggle_dealer_assignment()

    def unassign_dealer(self): #TODO: this work?
        for deck in self.decks:
            deck._toggle_dealer_assignment()

    def __toggle_game_assignment(self):
        self.dealer._toggle_game_assignment()

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
    def start_game(self):  # return data to be stored for analyzing results later
        pass
        # Assign Game / Auth Dealer for the game
        # if self.dealer.game_assigned is False:
        #     self.__toggle_game_assignment()

        # # Send rules, deck to dealer & Deal first hand (_deal shoul do the status update for the deck)
        # hand_0, player_states_0 = self.dealer.deal(
        #     players=self.roster, rules=self.rules, deck=self.decks[0]
        # )

        # # Data storage needs to reference each hand at a time.
        # data_0 = {
        #     "action_score_hand": DefaultDict[
        #         str, Tuple[str, int, DefaultDict[Card | JokerCard, int](int)]
        #     ](),
        #     "deck": {
        #         "unused": DefaultDict[Card | JokerCard, int](
        #             int
        #         ),  # TODO: turning this into a list only works for single deck
        #         "board": DefaultDict[Card | JokerCard, int](int),
        #         "trash_pile": DefaultDict[Card | JokerCard, int](int),
        #     },
        #     "player_behavior": {
        #         # TODO: storing this?
        #     },
        #     "dealer_behavior": "",  # TODO: how to store this?
        # }

        # for player in self.roster:  # TODO: once this becomes circular, it'll need a way to convert to a simple List
        #     data_0["action_score_hand"][player.name] = {
        #         "",
        #         player.score,
        #         player.hand,
        #     }  # list only works for single deck -> should just become

        # for deck in self.decks:
        #     for card in deck.unused:
        #         data_0["deck"]["unused"][card] += 1
        #     for card, adder in deck.board.items():
        #         data_0["deck"]["board"][card] += adder
        #     for card in deck.trash_pile:
        #         data_0["deck"]["trash_pile"][card] += 1

        # data_0["player_behavior"] : {}
        # data_0["dealer_behavior"] = 0

        # TODO: write to a JSON file/DB somewhere

    # def next_hand(self):  #
        # # Trigger player action
        # for player in self.roster:
        #     action_instructions = player.take_action
        # for player in self.roster:  # whatever is list equivalent version of it
        #     action_instructions = player.take_action(
        #         crucial_game_state={}, historical_state={}, cheat_codes=None
        #     )  # TODO: THINK ABOUT OPTIMAL IGNESTION PATH
        #     self.dealer._handle_player_actions(
        #         player=player,
        #         actions=action_instructions,
        #         deck=self.deck,
        #         rules=self.rules,
        #     )

        # # Dealer handles those
        # # record data and then return
        # return

    #TODO: I think it's a logiscital decision whether to turn this into an abstract class and leave it so
    # or simplt make iy classmethod and go fro mthere
    # functions hapepning beneathe - more functional than they are chronological
    # @abstractmethod
    # def __keep_score(self): ...
