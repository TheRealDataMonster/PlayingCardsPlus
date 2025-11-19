from playingcardsplus.MultiplayerGames.instructions import Instruction, InstructionSetImplementer
from playingcardsplus.MultiplayerGames.data import GameState, CheatingState
from playingcardsplus.card import Card, JokerCard

from typing_extensions import Optional, DefaultDict, Dict, NamedTuple, List, Any
from pydantic import BaseModel, Field


#TODO: so we need some sort of a validator to vlidate those two!
# TODO: 2 things that need to be received from other entities - potentially diff env in multi-host/decentrlzed env are
# 1) score
# 2) player hand updates
#
# 1 thing that need to be sent are
# 1) player hand update
#
# That means we must valdiate ->
# 1) Score update - in relation th new score that comes in vs current score & play's previous moves - depending on eng could be that I re-run the logic or verify the proof here
#  > thing is I need ot valdiate the formatting of the result here and see if it matches with trace inb the proof verification stage?
# 2) hand update: player received new hands - need to valdiate against its current udnerstanding of the deck and corr-ref againt proof of deck update


class ScoreAndHandValidator(BaseModel):
    """
    Use this like this
    1)
    2)
    3)
    """
    player_name: str = Field(frozen=True) #When validating, let's cross-ref this first
    pass


class PlayerBehavior(NamedTuple):
    name: str
    soul: Dict[str, Any] # TODO: think of the structure of this? - should prob include
    #   NameError
    #   model
    #   etc...
    #
    def run_model(self, *arg):
        return self.soul["model"](arg)


#TODO: it remaisn a choice whether to input a soul of a player of specific game or simply to input soul and separate types of players per game as a difff object...
class Player:
    """
    Player object where name is immutable. Behavior - defined by AI can be modified each hand
    """

    def __init__(self, name: str, initial_hand: DefaultDict[Card | JokerCard, int], initial_score: int, behvior: PlayerBehavior):
        self.__name = name
        self.__hand = initial_hand
        self.__score = initial_score #TODO: score needs to be received from the Game - which may require some validation given it'll need ot xfer
        self.__behavior = behvior

    # Player behavior can be parametrized by location of the model, specific rules-based criteria per game, etc...

    # Accept a dealt card - must be called by a Dealer
    @property
    def name(self):
        return self.__name


    @property
    def hand(self) -> DefaultDict[Card | JokerCard, int]:
        return self.__hand

    @property
    def score(self) -> int:
        return self.__score

    @property  # TODO: further access control? - only game devs and simulation runners need control
    def behavior(self) -> PlayerBehavior:
        return self.__behavior

    def _accept_card(self, card: Card | JokerCard):
        """list of cards come ordered in a way it should be accepting them"""
        self.__hand[card] += 1

    def _remove_card(self, card: Card | JokerCard):
        self.__hand[card] -= 1

    def _update_score(self, new_points: int):
        self.__score += new_points

    @behavior.setter
    def _update_behavior(self, new_behavior: Dict[str, str | int | float]):
        # exact logic for triggering this should be controlled by game devs
        self.__behavior = new_behavior

    def take_action(
        self,
        current_game_state: GameState, # need to look at - board, their own hand, card counts, etc..
        historical_states: List[GameState],
        cheating_states: Optional[List[CheatingState]], # If allowed to cheat then it can look at
        instruction_implementer: InstructionSetImplementer #TODO: rather a wrapper function that uses it
    ) -> List[Instruction]:
        """
        Takes in crucial information about the game itself to make a judgment & past information to make msot judgments.
        It can take in information that woould be normally considered cheating if it knew (cheat_code) - ie. knowing placement of specific cards

        Returns a specific action that the Game/Dealer needs to look at and take action.
        """

        # this will involve some sort of a model making a decision and that decision space will be the space of instruction set
        # 1) TODO: need a function to convert data into a model runnable format - whatever it might look like...
        # 2) Run model
        player_actions =  self.__behavior.soul.run_model(current_game_state, self.__hand, historical_states, cheating_states)

        # 3) TODO: Actually apply those actions
        for instruction in player_actions:
            if hasattr(instruction_implementer, "{}_player".format(instruction.operation)) and callable(getattr(instruction_implementer, "{}_player".format(instruction.operation))):
                method = getattr(instruction_implementer, "{}_player".format(instruction.operation))
                method(self) # TODO: hopefully this works...

        return player_actions
