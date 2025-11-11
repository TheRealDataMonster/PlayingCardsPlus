from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.custom_error import PlayerRangeError, CardDistributionError

from typing_extensions import Dict, Tuple, List, DefaultDict
from pydantic import BaseModel, PositiveInt, NonNegativeInt, ConfigDict, Field, field_validator, model_validator, computed_field


class Rules(BaseModel): # Requires a pretty sphisticated validation
    model_config = ConfigDict(frozen=True)

    # Basic Settings About The Game
    deck_size: PositiveInt
    player_range: Tuple[PositiveInt, PositiveInt] # (min_player, max_player)

    # Rules for how dealers should distribute cards
    allow_trash_pile_addition: bool = Field(default=False)
    cards_per_player_hand_0: Dict[PositiveInt, PositiveInt] | PositiveInt # if dict then number is arange for each of player count other wise it's an int
    cards_per_player_hand_i: Dict[PositiveInt, PositiveInt] | PositiveInt
    board_distribution_hand_0: PositiveInt
    board_distribution_hand_i: PositiveInt
    distribution_methods: Dict[Distributee, CardDistributionMethod] # ie- {}
    distribution_ordering: List[Distributee] #TODO: maybe this should be order preserving & circular

    # Rules for how player actions should be interpretted by the Game & Dealer
    instructions: PlayerDecision_InstructionSet
    instruction_constraints: Dict | None #TODO: not exactly sure what this'd look like yet TBH

    @computed_field
    @property
    def cards_to_distribute_hand_0(self) -> NonNegativeInt | Dict[PositiveInt, NonNegativeInt]:
        # counter = None
        if type(self.cards_per_player_hand_0) is int:
           return self.cards_per_player_hand_0*self.player_range[0]

        elif type(self.cards_per_player_hand_0) is dict:
            counter = dict()
            for player_count, card_count in self.cards_per_player_hand_0.items():
                counter[player_count] = card_count*player_count
            return counter


    @computed_field
    @property
    def cards_to_distribute_hand_i(self) -> NonNegativeInt | Dict[PositiveInt, NonNegativeInt]:
        # counter = None
        if type(self.cards_per_player_hand_i) is int:
           return self.cards_per_player_hand_i*self.player_range[0]

        elif type(self.cards_per_player_hand_i) is dict:
            counter = dict()
            for player_count, card_count in self.cards_per_player_hand_i.items():
                counter[player_count] = card_count*player_count
            return counter

    # This'd be super annoying for devs...
    # @model_validator(mode="after")
    # def validate_allow_trash_pile_addition(self):
    #     if not self.allow_trash_pile_addition and

    # Make sure Min player <= Max player count - I mena obviously...
    @field_validator('player_range', mode='after')
    @classmethod
    def validate_player_range(cls, range: Tuple[PositiveInt, PositiveInt]) -> Tuple[PositiveInt, PositiveInt]:
        if range[0] > range[1]:
            raise PlayerRangeError('The first value in the tuple must be strictly less than the second value.')
        return range

    @classmethod
    def __calculate_used_previously(cls,
        distribution_ordering: List[Distributee],
        board_distributed: int,
        trash_distributed: int = 0,
        unused_distributed: int = 0,
        stump: int = 0):
        """
        """
        other_cards_used = 0
        for entity in distribution_ordering: # find out the index of players
            if entity == Distributee.PLAYER:
                break
            elif entity == Distributee.BOARD:
                other_cards_used += board_distributed
            elif entity == Distributee.TRASH_PILE:
                other_cards_used += trash_distributed
            elif entity == Distributee.UNUSED:
                other_cards_used -= unused_distributed
            else:
                raise ValueError("distribution_ordering as in from the Rules")

        return stump + other_cards_used

    @classmethod
    def __validate_card_distribution(cls, deck_size: int, used_previously: int, cards_to_distribute: int):
        return deck_size - used_previously >= cards_to_distribute

    @classmethod
    def __validation_wrapper(cls,
        cards_to_distribute: NonNegativeInt | Dict[PositiveInt, NonNegativeInt],
        deck_size: PositiveInt,
        used_previously: PositiveInt,
        max_players: PositiveInt,
        cards_per_player: NonNegativeInt | Dict[PositiveInt, NonNegativeInt],
        hand: str
    ):
        if type(cards_to_distribute) is int:
            if not Rules.__validate_card_distribution(
                deck_size=deck_size,
                used_previously=used_previously,
                cards_to_distribute=cards_to_distribute
            ):
                raise CardDistributionError(
                    """More cards are being handed out to players than there are cards available. The math follows:"""
                    """\n {} (deck_size) - {} (previously used cards) < {} (max_player_count) X {} (cards_per_player_hand_{}) = {} (cards_to_distribute_hand_{})""".format(
                        deck_size, used_previously, max_players, cards_per_player, hand, cards_to_distribute, hand
                    )
                )
        elif type(cards_to_distribute) is dict:
            rule_violations = DefaultDict[PositiveInt, str]()
            error_msg_header = """More cards are beign handed out to players than there are cards available at the following configs: \n"""
            error_msg_body = \
            """ Player Count = {} | {} (deck_size) - {} (previously used cards) < {} (player_count) X {} (cards_per_player_hand_{}) = {} (cards_to_distribute_hand_{}) \n"""
            for player_count, total_cards_to_players in cards_to_distribute.items():
                if not Rules.__validate_card_distribution(
                    deck_size=deck_size,
                    used_previously=used_previously,
                    cards_to_distribute=total_cards_to_players
                ):
                    rule_violations[player_count] = error_msg_body.format(
                        player_count, deck_size, used_previously, player_count, cards_per_player[player_count], hand, total_cards_to_players, hand
                    )

            if rule_violations:
                raise CardDistributionError(
                    error_msg_header + "".join(rule_violations.values())
                )

    # Make sure total cards distributed <= cards left unused
    # Logic is simple: Deck Size - Previously_Used < cards to distribute -> then Rule is Ill-formed
    @model_validator(mode="after")
    def validate_hand_0(self): #TODO: This does not consider whether it receives from trash_pile or not

        # Calculate cards that shouldn't be used first
        used_previously = Rules.__calculate_used_previously(
            distribution_ordering=self.distribution_ordering,
            board_distributed=self.board_distribution_hand_0
        )

        # Then run validations
        cards_to_distribute = self.cards_to_distribute_hand_0

        Rules.__validation_wrapper(
            cards_to_distribute=cards_to_distribute,
            deck_size=self.deck_size,
            used_previously=used_previously,
            max_players=self.player_range[1],
            cards_per_player=self.cards_per_player_hand_0,
            hand="0"
        )
        return self

    # Make sure total cards distributed <= cards left unused
    # Logic is simple: Deck Size - Previously_Used < cards to distribute -> then Rule is Ill-formed
    @model_validator(mode="after")
    def validate_hand_i(self):

        cards_to_distribute = self.cards_to_distribute_hand_i

        # Calculate cards that shouldn't be used first
        stump = self.board_distribution_hand_0
        stump_addition = self.cards_to_distribute_hand_0
        if type(stump_addition) is int:
            used_previously = Rules.__calculate_used_previously(
                distribution_ordering=self.distribution_ordering,
                board_distributed=self.board_distribution_hand_i,
                stump=stump+stump_addition
            )
            Rules.__validation_wrapper(
                cards_to_distribute=cards_to_distribute,
                deck_size=self.deck_size,
                used_previously=used_previously,
                max_players=self.player_range[1],
                cards_per_player=self.cards_per_player_hand_i,
                hand="i"
            )
        elif type(stump_addition) is dict:
            error_msg_header = "Hand i rule violations as follows: \n"
            rule_violations = DefaultDict[PositiveInt, str]()
            for player_count, stump_adder in stump_addition.items():
                used_previously = Rules.__calculate_used_previously(
                    distribution_ordering=self.distribution_ordering,
                    board_distributed=self.board_distribution_hand_i,
                    stump=stump+stump_adder
                )
                try:
                    Rules.__validation_wrapper(
                        cards_to_distribute=cards_to_distribute,
                        deck_size=self.deck_size,
                        used_previously=used_previously,
                        max_players=self.player_range[1],
                        cards_per_player=self.cards_per_player_hand_i,
                        hand="i"
                    )
                except CardDistributionError as e:
                    rule_violations[player_count] = str(e)

            if rule_violations:
                raise CardDistributionError(
                    error_msg_header + "".join(rule_violations.values())
                )
        else:
            raise TypeError("Rule violation: 'cards_to_distribute_hand_0' is neither an int nor dict please check it!")

        return self


    @field_validator("distribution_methods", mode="after")
    @classmethod
    def validate_distribution_methods(cls, distribution_methods: Dict[Distributee, CardDistributionMethod]) -> Dict[Distributee, CardDistributionMethod]:
        """Basically just checks if there are anything that shouldn't be there"""
        for distributee, distribution_method in distribution_methods.items():
            if not isinstance(distributee, Distributee):
                raise UnrecognizedDistributeeError(
                    """
                    Cannot distribute cards to such an entity ('{}')
                    Please check 'distribution_ordering' to see if it contains something that is not in 'player', 'unused', 'board', or 'trash_pile'
                    """.format(distributee)
                )
            if not isinstance(distribution_method, CardDistributionMethod):
                raise DistributionMethodUnrecognizedError(
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
                raise UnrecognizedDistributeeError(
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
