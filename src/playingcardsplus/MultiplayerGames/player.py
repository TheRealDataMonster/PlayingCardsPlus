from playingcardsplus.card import Card, JokerCard

from typing_extensions import Optional, DefaultDict, Dict, NamedTuple, List, Any
from abc import ABC, abstractmethod
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


class PlayerBehavior(BaseModel):
    name:str = Field(frozen=True)
    soul: Optional[Any] = None


class Instruction(NamedTuple):
    op: str


class PlayerDecision_InstructionSet(NamedTuple):
    operations: List[Instruction]
    # (K,V) function = instruction op, [decision functions which is a function in player action]


class Player:
    """
    Player object where name is immutable. Behavior - defined by AI can be modified each hand
    """

    def __init__(self, name: str, initial_hand: DefaultDict[Card | JokerCard, int], initial_score: int, starting_behvior: Dict[str, str | int | float]):
        self.__name = name
        self.__hand = initial_hand
        self.__score = initial_score #TODO: score needs to be received from the Game - which may require some validation given it'll need ot xfer
        self.__behavior = starting_behvior

    # Player behavior can be parametrized by location of the model, specific rules-based criteria per game, etc...

    # Accept a dealt card - must be called by a Dealer
    @property
    def hand(self) -> DefaultDict[Card | JokerCard, int]:
        return self.__hand

    @property
    def score(self) -> int:
        return self.__score

    @property  # TODO: further access control? - only game devs and simulation runners need control
    def behavior(self) -> Dict[str, str | int | float]:
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

    # TODO: Need to think about data structure that it grabs - specifically for cheat_codes
    # TODO: should this directly call AI agent or make a ping to the agent, which should be grabbing the data on its own and retrieve the decision?
    # @abstractmethod
    def take_action(
        self,
        crucial_game_state: Dict,
        historical_state: List[Dict],
        cheat_codes: Optional[str],
    ) -> List[Instruction]:
        """
        Takes in crucial information about the game itself to make a judgment & past information to make msot judgments.
        It can take in information that woould be normally considered cheating if it knew (cheat_code) - ie. knowing placement of specific cards

        Returns a specific action that the Game/Dealer needs to look at and take action.
        """
        return self.behavior.soul(crucial_game_state, historical_state, cheat_codes)
