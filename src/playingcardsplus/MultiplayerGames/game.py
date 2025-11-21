"""
Defines primitive objects such as Player, Game, and Dealer

InstructionSet objects are needed for players to make decisions

Each entity should be communicating via a specific data fields so they may be hosted in different instances.
For being hosted on multiple envs, eventually need to support each entity communicating through various protocols like HTTPS, RPC, etc...
"""

from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.dealer import Dealer
from playingcardsplus.MultiplayerGames.player import Player
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.instructions import InstructionSetImplementer
from playingcardsplus.MultiplayerGames.data import CollectibleData, GameState, CheatingState
from playingcardsplus.custom_error import RuleViolationError

from typing_extensions import Dict, List, Iterable
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict, model_validator



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
    deck: MultiPlayerDeck = Field(frozen=True)  # there can be multiple decks & immutable
    roster: List[Player]  # TODO: make it circular so we can maintain order of playing in a trusted way? - maybe for v2...
    rules: Rules = Field(frozen=True)
    scoreboard: Dict[Player, int]  # Score should be kept by the Game. Trust this over what players keep track of - they're motivated by their behavior profiles in simulations and in real games, they may be conflated
    game_data_path: str # where to store data about the game - up to devs to decide how to manage this

    @classmethod
    def __one_hot_encode_iterable(cls, iterable: Iterable, exhaustive_list: Iterable):
        res = dict()
        for element in exhaustive_list:
            res[element] = 0
        for element in iterable:
            res[element] = element if (isinstance(element, int) or isinstance(element, float)) else True
        return res

    # *** Dealer & Game Assignments
    def __toggle_game_assignment(self):
        self.dealer._toggle_game_assignment()

    # Add validators to make sure
    # 1) Game parameters match the rules
    #   -> player count good
    #   -> deck size good
    # Guess there  aren;t much else right?
    #

    @model_validator(mode="after")
    def validate_player_count(self):
        if len(self.roster) < self.rules.player_range[0]:
            raise RuleViolationError(
                "Number of players is too low, should at least be {} but we're at {}".format(self.rules.player_range[0], len(self.roster))
            )
        elif len(self.roster) > self.rules.player_range[1]:
            raise RuleViolationError(
                "Number of players is too high, should at most be {} but we're at {}".format(self.rules.player_range[1], len(self.roster))
            )
        return self

    @model_validator(mode="after")
    def validate_deck_size(self):
        if len(self.deck) != self.rules.deck_size:
            raise RuleViolationError(
                "Size of the deck doesn't match the rules - should be {} cards but we have {} cards".format(self.rules.deck_size, len(self.deck))
            )
        return self

    @abstractmethod
    def calculate_score(self) -> Dict[Player, int]:
        ...

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

    def deal(self, hand_index: int):
        return self.dealer.deal(
            players=self.roster, rules=self.rules, deck=self.deck, hand_index=hand_index
        )

    def take_player_actions(self, instruction_implementer):
        game_state_post_deal = GameState(
            player_count=len(self.roster),
            board=self.deck.board,
            unused_count=len(self.deck.unused),
            trash_pile_count=len(self.deck.trash_pile),
            player_hand_count=sum(self.deck.player_hands.values()),
            deck_type=self.deck.type,
            joker_count=self.deck.joker_count
        )
        player_actions_map = dict()
        for player in self.roster:
            player_actions = player.take_action(
                current_game_state=game_state_post_deal,
                historical_states=[],
                cheating_states=[], #TODO: create option for cheating here
                instruction_implementer=instruction_implementer
            )
            # Actually apply those actions accordingly to players and dealers
            for (instruction, aux_input) in player_actions:
                if hasattr(instruction_implementer, "{}".format(instruction.operation)) and callable(getattr(instruction_implementer, "{}".format(instruction.operation))):
                    method = getattr(instruction_implementer, "{}".format(instruction.operation))

                    method(player=player, dealer=self.dealer, deck=self.deck, aux=aux_input) # TODO: hopefully this works...

            # Make sure it's recorded appropriately
            player_actions_map[player.name] = Game.__one_hot_encode_iterable(
                iterable = player_actions,
                exhaustive_list=self.rules.instructions.instructions
            )
        return player_actions_map

    def record_data(self, player_actions_map) -> CollectibleData:
        # Collect and return data
        # data at hand 0
        scoreboard = dict()
        for player, score in self.scoreboard.items():
            scoreboard[player.name] = score
        cards = self.deck.cards

        return CollectibleData(
            player_actions=player_actions_map,
            scores=scoreboard,
            player_state=self.deck.player_hands,
            unused_state=Game.__one_hot_encode_iterable(iterable=self.deck.unused, exhaustive_list=cards),
            board_state=self.deck.board,
            trash_pile_state=Game.__one_hot_encode_iterable(iterable=self.deck.trash_pile, exhaustive_list=cards)
        )

    # to be called by simulators
    def start_game(self, instruction_implementer: InstructionSetImplementer) -> CollectibleData:  # return data to be stored for analyzing results later
        # Assign Game / Auth Dealer for the game
        if self.dealer.game_assigned is False:
            self.__toggle_game_assignment()

        # Send rules, deck to dealer & Deal first hand (_deal shoul do the status update for the deck)
        self.deck, player_states_0 = self.deal(hand_index=0)

        # Let players take action -
        player_actions_map = self.take_player_actions(instruction_implementer)

        # Calcualte Score
        self.scoreboard = self.calculate_score()

        # Collect and return data
        return self.record_data(player_actions_map)


    def next_hand(self):  #
        # Assign Game / Auth Dealer for the game
        if self.dealer.game_assigned is False:
            self.__toggle_game_assignment()

        #TODO???
        # # Trigger player action
        # for player in self.roster:
        #     action_instructions = player.take_action
        # for player in self.roster:  # whatever is list equivalent version of it
        #     action_instructions = player.take_action(
        #         current_game_state={}, historical_states={}, cheat_codes=None
        #     )  # TODO: THINK ABOUT OPTIMAL IGNESTION PATH
        #     self.dealer._handle_player_actions(
        #         player=player,
        #         actions=action_instructions,
        #         deck=self.deck,
        #         rules=self.rules,
        #     )

        # Dealer handles those
        # record data and then return
        return
