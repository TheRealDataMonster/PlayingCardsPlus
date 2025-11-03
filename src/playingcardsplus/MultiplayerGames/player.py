from playingcardsplus.card import Card, JokerCard

from typing_extensions import Optional, DefaultDict, Dict, Iterable
from pydantic import BaseModel, Field, PrivateAttr, NonNegativeInt
from abc import ABC, abstractmethod


class PlayerDecision_InstructionSet(BaseModel):
    operations: DefaultDict
    # (K,V) function = instruction op, decision function

class Player(BaseModel, ABC):
    """
    Player object where name is immutable. Behavior - defined by AI can be modified each hand
    """
    name: str = Field(frozen=True)
    _hand: DefaultDict[Card|JokerCard, NonNegativeInt] = PrivateAttr(DefaultDict[Card|JokerCard, NonNegativeInt](int)) # How many of a given card does one have? - this way, we can track multi-decks and have it encodes
    _score: int = 0
    _behavior: Dict[str, str | int | float] = PrivateAttr() # this is where you can plug-in some behavior - like an AI model or rules-based object wrapper
    # Player behavior can be parametrized by location of the model, specific rules-based criteria per game, etc...

    # Accept a dealt card - must be called by a Dealer
    @property
    def hand(self) -> DefaultDict[Card|JokerCard, NonNegativeInt]:
        return self._hand

    @property
    def score(self) -> int:
        return self._score

    @property #TODO: further access control? - only game devs and simulation runners need control
    def behavior(self) -> Dict[str, str | int | float]:
        return self._behavior

    @hand.setter
    def _accept_card(self, cards: DefaultDict[Card|JokerCard, NonNegativeInt]):
        """list of cards come ordered in a way it should be accepting them"""
        for card, count in cards.items():
            self._hand[card] += count

    @score.setter
    def _update_score(self, new_points: int):
        self._score += new_points

    @behavior.setter
    def _update_behavior(self, new_behavior: Dict[str, str | int | float]):
        # exact logic for triggering this should be controlled by game devs
        self._behavior = new_behavior

    # TODO: Need to think about data structure that it grabs - specifically for cheat_codes
    # TODO: should this directly call AI agent or make a ping to the agent, which should be grabbing the data on its own and retrieve the decision?
    @abstractmethod
    def take_action(self, crucial_game_state: Dict, historical_state: Iterable[Dict], cheat_codes: Optional[str]) -> Iterable[PlayerDecision_InstructionSet]:
        """
        Abstract method to be implemented by subclasses.

        Takes in crucial information about the game itself to make a judgment & past information to make msot judgments.
        It can take in information that woould be normally considered cheating if it knew (cheat_code) - ie. knowing placement of specific cards

        Returns a specific action that the Game/Dealer needs to look at and take action.
        """
        ...
