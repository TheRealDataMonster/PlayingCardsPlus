from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet

from typing_extensions import TypedDict, Dict, Tuple, List
from pydantic import BaseModel, PositiveInt, NonNegativeInt, field_validator, model_validator, ConfigDict



class BoardTrashUnusedConfig(TypedDict):
    board: NonNegativeInt
    trash_pile: NonNegativeInt
    unused: NonNegativeInt


class Rules(BaseModel): # Requires a pretty sphisticated validation
    model_config = ConfigDict(frozen=True)

    # Basic Settings About The Game
    deck_size: PositiveInt
    player_range: Tuple[PositiveInt, PositiveInt] # (min_player, max_player)

    # Rules for how dealers should distribute cards
    cards_per_player_hand_0: Dict[PositiveInt, PositiveInt] | PositiveInt # if dict then number is arange for each of player count other wise it's an int
    cards_per_player_hand_i: Dict[PositiveInt, PositiveInt] | PositiveInt
    other_card_distribution_hand_0: BoardTrashUnusedConfig
    other_card_distribution_hand_i: BoardTrashUnusedConfig
    distribution_methods: Dict[str, CardDistributionMethod] # ie- {}
    distribution_ordering: List[str] #TODO: maybe this should be order preserving & circular

    # Rules for how player actions should be interpretted by the Game & Dealer
    instructions: PlayerDecision_InstructionSet
    instruction_constraints: Dict #TODO: not exactly sure what this'd look like yet TBH

    # Make sure Min player <= Max player count - I mena obviously...
    @field_validator('player_range', mode='after')
    @classmethod
    def validate_player_range(cls, range: Tuple[PositiveInt, PositiveInt]) -> Tuple[PositiveInt, PositiveInt]:
        if range[0] >= range[1]:
            raise ValueError('The first value in the tuple must be strictly less than the second value.')
        return range

    # Make sure total cards distributed <= cards in deck
    @model_validator(mode="after")
    def validate_card_count_hand_0(self):
        if type(self.cards_per_player_hand_0) is int:
            if self.cards_per_player_hand_0*self.player_range[1] > self.deck_size:
                raise ValueError(
                    "More cards are being handed out to players than ther eare cards available"
                    "\n | max_player_count={} & cards_per_player_hand_0={} & deck_size={}".format(self.player_range[1], self.cards_per_player_hand_0, self.deck_size)
                )
        elif type(self.cards_per_player_hand_0) is dict:
            for player_count, card_count in self.cards_per_player_hand_0.items():
                if player_count*card_count > self.deck_size:
                    raise ValueError(
                        "More cards are being handed out to players than ther eare cards available"
                        "\n | player_count={} & player_size= cards_per_player_hand_0={} & deck_size={}".format(player_count, self.cards_per_player_hand_0, self.deck_size)
                    )
        return self

    # Make sure total cards being handed out  <= deck_size - handed out at 0
    @model_validator(mode="after")
    def validate_card_count_hand_i(self):
        if type(self.cards_per_player_hand_i) is int:
            if self.cards_per_player_hand_i*self.player_range[1] > self.deck_size:
                raise ValueError(
                    "More cards are being handed out to players than ther eare cards available"
                    "\n | max_player_count={} & cards_per_player_hand_0={} & deck_size={}".format(self.player_range[1], self.cards_per_player_hand_i, self.deck_size)
                )
        elif type(self.cards_per_player_hand_i) is dict:
            for player_count, card_count in self.cards_per_player_hand_i.items():
                if player_count*card_count > self.deck_size:
                    raise ValueError(
                        "More cards are being handed out to players than ther eare cards available"
                        "\n | player_count={} & player_size= cards_per_player_hand_0={} & deck_size={}".format(player_count, self.cards_per_player_hand_i, self.deck_size)
                    )
        return self
