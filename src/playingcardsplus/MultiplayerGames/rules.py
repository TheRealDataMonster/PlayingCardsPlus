from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.custom_error import RuleIllFormedError

from typing_extensions import Dict, Tuple, List
from pydantic import BaseModel, PositiveInt, NonNegativeInt, field_validator, model_validator, computed_field, ConfigDict




class Rules(BaseModel): # Requires a pretty sphisticated validation
    model_config = ConfigDict(frozen=True)

    # Basic Settings About The Game
    deck_size: PositiveInt
    player_range: Tuple[PositiveInt, PositiveInt] # (min_player, max_player)

    # Rules for how dealers should distribute cards
    cards_per_player_hand_0: Dict[PositiveInt, PositiveInt] | PositiveInt # if dict then number is arange for each of player count other wise it's an int
    cards_per_player_hand_i: Dict[PositiveInt, PositiveInt] | PositiveInt
    other_card_distribution_hand_0: Dict[Distributee, NonNegativeInt]
    other_card_distribution_hand_i: Dict[Distributee, NonNegativeInt]
    distribution_methods: Dict[Distributee, CardDistributionMethod] # ie- {}
    distribution_ordering: List[Distributee] #TODO: maybe this should be order preserving & circular

    # Rules for how player actions should be interpretted by the Game & Dealer
    instructions: PlayerDecision_InstructionSet
    instruction_constraints: Dict | None #TODO: not exactly sure what this'd look like yet TBH


    @property
    @computed_field
    def total_card_count_to_players_at_hand_0(self) -> NonNegativeInt | Dict[PositiveInt, NonNegativeInt]:
        # counter = None
        if type(self.cards_per_player_hand_0) is int:
           return self.cards_per_player_hand_0

        elif type(self.cards_per_player_hand_0) is dict:
            counter = dict()
            for player_count, card_count in self.cards_per_player_hand_0.items():
                counter[player_count] = card_count
            return counter
        else:
            raise RuleIllFormedError(
               """
               type of `cards_per_player_hand_0` needs to be either int or Dict[int, int] but currently is {}
               """.format(type(self.cards_per_player_hand_0))
            )

    # Make sure Min player <= Max player count - I mena obviously...
    @field_validator('player_range', mode='after')
    @classmethod
    def validate_player_range(cls, range: Tuple[PositiveInt, PositiveInt]) -> Tuple[PositiveInt, PositiveInt]:
        if range[0] >= range[1]:
            raise RuleIllFormedError('The first value in the tuple must be strictly less than the second value.')
        return range

    # Make sure total cards distributed <= cards in deck
    @model_validator(mode="after")
    def validate_cards_per_player_hand_0(self):
        if type(self.cards_per_player_hand_0) is int:
            if self.cards_per_player_hand_0*self.player_range[1] > self.deck_size:
                raise RuleIllFormedError(
                    """More cards are being handed out to players than ther eare cards available"""
                    """\n | max_player_count={} & cards_per_player_hand_0={} & deck_size={}""".format(self.player_range[1], self.cards_per_player_hand_0, self.deck_size)
                )
        elif type(self.cards_per_player_hand_0) is dict:
            for player_count, card_count in self.cards_per_player_hand_0.items():
                if player_count*card_count > self.deck_size:
                    raise RuleIllFormedError(
                        """More cards are being handed out to players than ther eare cards available"""
                        """\n | player_count={} & player_size= cards_per_player_hand_0={} & deck_size={}""".format(player_count, self.cards_per_player_hand_0, self.deck_size)
                    )
        else:
            raise RuleIllFormedError(
               """
               type of `cards_per_player_hand_0` needs to be either int or Dict[int, int] but currently is {}
               """.format(type(self.cards_per_player_hand_0))
            )
        return self

    @field_validator("other_card_distribution_hand_0", "other_card_distribution_hand_i", mode="after")
    @classmethod
    def validate_other_card_distribution_hand_keys(cls, other_card_distribution: Dict[Distributee, NonNegativeInt]) -> Dict[Distributee, NonNegativeInt]:
        for key in other_card_distribution.keys():
            if not key in {"board", "unused", "trash_pile"}:
               raise RuleIllFormedError(
                   "'other_card_distribution_hand' is supposed to have  'board', 'unused', 'trash_pile' as keys"
               )
        return other_card_distribution

    # @model_validator(mode="after")
    # def validate_other_card_distribution_hand_0(self):
    #     # sum of cards <= deck_size - any previously handed out cards
    #     # -> If condition fails then only return error if the ordering prevents game from proceeding
    #     # TODO: defining this may be a bit difficult and very circumstantial.....

    #     # Sum of Cards
    #     handed_out = sum(self.other_card_distribution_hand_0.values())
    #     # Any cards previously handed out
    #     counter = 0
    #     if self.distribution_ordering[0] == 'player':
    #         counter = self.total_card_count_to_players_at_hand_0 #TODO: ?TypeError: 'PydanticDescriptorProxy' object is not callable
    #     else:
    #         counter = 0

    #     if isinstance(counter, int):
    #         if handed_out > self.deck_size - counter*self.player_range[1]:
    #             raise RuleIllFormedError("Number of cards being handed out to non-players in turn 0 is too large")
    #     else:
    #         for player_count, card_count in counter.items():
    #             if handed_out > self.deck_size - card_count*player_count:
    #                 raise RuleIllFormedError("Number of cards being handed out to non-players in turn 0 is too large")
    #     return self

    # Make sure total cards being handed out <= deck_size - handed out at 0
    @model_validator(mode="after")
    def validate_cards_per_player_hand_i(self):
        # TODO: feel like I should be adding other at 0?
        minus_counter = self.total_card_count_to_players_at_hand_0

        if type(self.cards_per_player_hand_i) is int:
            if self.cards_per_player_hand_i*self.player_range[1] > self.deck_size - minus_counter*self.player_range[1]:
                raise RuleIllFormedError(
                    "More cards are being handed out to players than ther eare cards available"
                    "\n | max_player_count={} & cards_per_player_hand_0={} & deck_size={}".format(self.player_range[1], self.cards_per_player_hand_i, self.deck_size)
                )
        elif type(self.cards_per_player_hand_i) is dict:
            for player_count, card_count in self.cards_per_player_hand_i.items():
                if player_count*card_count > self.deck_size - minus_counter[player_count]*player_count:
                    raise RuleIllFormedError(
                        "More cards are being handed out to players than ther eare cards available"
                        "\n | player_count={} & player_size= cards_per_player_hand_0={} & deck_size={}".format(player_count, self.cards_per_player_hand_i, self.deck_size)
                    )
        else:
            raise RuleIllFormedError(
               """
               Type of `cards_per_player_hand_i` needs to be either int or Dict[int, int] but currently is {}
               """ .format(type(self.cards_per_player_hand_i))
            )
        return self

    # @model_validator(mode="after")
    # def validate_other_card_distribution_hand_i(self):
    #    sum of cards <= deck_size - any previously handed out cards
    #    -> If condition fails then only return error if the ordering prevents game from proceeding
    # TODO: defining this may be a bit difficult and very circumstantial.....

    # Sum of Cards
    # handed_out = sum(self.other_card_distribution_hand_i.values())
    # # Any cards previously handed out
    # counter = 0
    # if self.distribution_ordering[0] == 'player':
    #     counter = self.total_card_count_to_players_at_hand_i #TODO: ?TypeError: 'PydanticDescriptorProxy' object is not callable
    # else:
    #     counter = 0

    # if isinstance(counter, int):
    #     if handed_out > self.deck_size - counter*self.player_range[1]:
    #         raise RuleIllFormedError("Number of cards being handed out to non-players in turn 0 is too large")
    # else:
    #     for player_count, card_count in counter.items():
    #         if handed_out > self.deck_size - card_count*player_count:
    #             raise RuleIllFormedError("Number of cards being handed out to non-players in turn 0 is too large")
    # return self


    @field_validator("distribution_methods", mode="after")
    @classmethod
    def validate_distribution_methods(cls, distribution_methods: Dict[Distributee, CardDistributionMethod]) -> Dict[Distributee, CardDistributionMethod]:
        """Basically just checks if there are anything that shouldn't be there"""
        for distributee, distribution_method in distribution_methods.items():
            if not isinstance(distributee, Distributee):
                raise RuleIllFormedError(
                    """
                    Cannot distribute cards to such an entity ('{}')
                    Please check 'distribution_ordering' to see if it contains something that is not in 'player', 'unused', 'board', or 'trash_pile'
                    """.format(distributee)
                )
            if not isinstance(distribution_method, CardDistributionMethod):
                raise RuleIllFormedError(
                    """
                    Such a distribution method '{}' is not known!
                    Please check 'distribution_method' to see if it contains something that is not in 'ONE_AT_A_TIME=one_at_a_time' or 'LUMP=lump'
                    """.format(distribution_method)
                )
        return distribution_methods

    @field_validator("distribution_ordering", mode="after")
    @classmethod
    def validate_distribution_ordering(cls, distribution_ordering: List[Distributee]) -> List[Distributee]:
        """Basically just needs to check if there aren't any insances that shouldn't be there"""
        for distributee in distribution_ordering:
            if not isinstance(distributee, Distributee):
                raise RuleIllFormedError(
                    """
                    Cannot distribute cards to such an entity!
                    Please check 'distribution_ordering' to see if it contains something that is not in 'player', 'unused', 'board', or 'trash_pile'
                    """
                )
        return distribution_ordering

    #TODO: valdiating these 2 exactly?
    # Rules for how player actions should be interpretted by the Game & Dealer
    # instructions: PlayerDecision_InstructionSet
    # instruction_constraints: Dict | None #TODO: not exactly sure what this'd look like yet TBH
