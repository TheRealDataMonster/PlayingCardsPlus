from playingcardsplus.card import Card, JokerCard
from playingcardsplus.deck import DeckType, CardCountMap

from typing_extensions import Dict
from pydantic import BaseModel, NonNegativeInt, PositiveInt, model_validator, ValidationError


# class CollectibleMetaData(BaseModel):
#     dealer: Dealer
#     deck: MultiPlayerDeck
#     roster: List[str] # list of player names

class CollectibleData(BaseModel): # Per Hand
    player_actions: Dict[str, Dict[str, int|float|bool]] # (k,(k,v)) = (player_name, (action_type, binary or int/float for magnitude of the decision when relevant))
    scores: Dict[str, int] # (k,v) = (player_name, score)
    player_state: Dict[Card | JokerCard, bool]
    unused_state: Dict[Card | JokerCard, bool]
    board_state: Dict[Card | JokerCard, bool]
    trash_pile_state: Dict[Card | JokerCard, bool]

    # Hand starts at index 0, where Dealer has just dealt cards, then Player takes action.
    # Index 1 after the Dealer has taken acount of Players' actions and then made changes to the Deck accordingly
    # Index i so on...
    # Until Index L (last hand): where it's after the dealer deals but now the stop conditions have been met - based on the rule

#     # Types of analysis to be done are going to be
#     # 1) Why did a player take a certain action? (& what would've been optimal for their goal) -> refernce each index at a time
#     # 2) When was it determined that a particular Player would win -> reference each index at a time then calculate odds based on deck status and what not


class GameState(BaseModel):
    """Players use this to make decisions"""
    player_count: PositiveInt
    board: Dict[Card | JokerCard, bool]
    unused_count: NonNegativeInt
    trash_pile_count: NonNegativeInt
    player_hand_count: NonNegativeInt
    deck_type: DeckType
    joker_count: NonNegativeInt

    @model_validator(mode="after")
    def validate_card_count(self):
        if self.unused_count + self.trash_pile_count + self.player_hand_count + sum(self.board.values()) != CardCountMap[self.deck_type] + self.joker_count:
            raise ValidationError("number of cards do not add up! are you sure you recorded the Game State correctly?")
        return self

class CheatingState(BaseModel): #TODO: prob includes some combination of - ordering of unused, trashpile, and what player hands
    pass
