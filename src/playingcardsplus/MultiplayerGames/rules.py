from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.custom_error import PlayerRangeError, CardDistributionError

from typing_extensions import Dict, Tuple, List, DefaultDict
from pydantic import BaseModel, PositiveInt, NonNegativeInt, ConfigDict, Field, field_validator, model_validator, computed_field, ValidationError


# TODO prob the most important thing to add is make sure the instruction set covers soem condition on how many cards to be distributed frokm non-unused as this is entirely game dependent
class Rules(BaseModel): # Requires a pretty sphisticated validation
    """
    Rules parametrized. Mostly covers number of players, how many cards should be distributed to from the unused pile &
    whetehr it allows distribution of cards from other entities in the deck that's not the unused pile to other piles.

    """
    model_config = ConfigDict(frozen=True)

    # Basic Settings About The Game
    deck_size: PositiveInt
    player_range: Tuple[PositiveInt, PositiveInt] # (min_player, max_player)


    # Rules for how dealers should distribute cards (unused -> others...)
    cards_per_player_hand_0: Dict[PositiveInt, NonNegativeInt] | NonNegativeInt # if dict then number is arange for each of player count other wise it's an int
    cards_per_player_hand_i: Dict[PositiveInt, NonNegativeInt] | NonNegativeInt
    board_distribution_hand_0: NonNegativeInt
    board_distribution_hand_i: NonNegativeInt
    trash_pile_distribution_hand_0: NonNegativeInt = Field(default=0)
    trash_pile_distribution_hand_i: NonNegativeInt = Field(default=0)
    distribution_methods: Dict[Distributee, CardDistributionMethod]
    distribution_ordering: List[Distributee] #TODO: maybe this should be order preserving & circular

    # Rules for how players can treat their cards wrt changing their distrtibution (ie. players -> trash / trash-> unused / board -> players)
    # Much of this isvery game dependent so lot of will be more or less of permissions for the dealer to look at and comply
    allow_board_to_players: bool = Field(default=False)
    allow_trash_pile_to_players: bool = Field(default=False)

    allow_players_to_board: bool = Field(default=False)
    allow_trash_pile_to_board: bool = Field(default=False)

    allow_players_to_trash_pile: bool = Field(default=False)
    allow_board_to_trash_pile: bool = Field(default=False)

    allow_players_to_unused: bool = Field(default=False)
    allow_board_to_unused: bool = Field(default=False)
    allow_trash_pile_to_unused: bool = Field(default=False)


    # Rules for how player actions should be interpretted by the Game & Dealer
    instructions: PlayerDecision_InstructionSet
    instruction_constraints: Dict | None #TODO: not exactly sure what this'd look like yet TBH

    @computed_field
    @property
    def total_cards_distributed_hand_0(self) -> NonNegativeInt | Dict[PositiveInt, NonNegativeInt]:
        # counter = None
        if type(self.cards_per_player_hand_0) is int:
           return self.cards_per_player_hand_0*self.player_range[1] + self.board_distribution_hand_0 + self.trash_pile_distribution_hand_0

        elif type(self.cards_per_player_hand_0) is dict:
            counter = dict()
            for player_count, card_count in self.cards_per_player_hand_0.items():
                counter[player_count] = card_count*player_count + self.board_distribution_hand_0 + self.trash_pile_distribution_hand_0
            return counter
        else:
            raise ValidationError #TODO this is just for my IDE to not think there's sth wrong. let's see if this cuases UX issue...


    @computed_field
    @property
    def total_cards_distributed_hand_i(self) -> NonNegativeInt | Dict[PositiveInt, NonNegativeInt]:
        #TODO: eventually need to consider unused pile being restocked
        """
        Calculate total cards being handed out by . For trash_pile usage
        """

        used_previously = self.total_cards_distributed_hand_0
        if type(self.cards_per_player_hand_i) is int:
            used_at_hand_0 = used_previously[self.player_range[1]] if type(used_previously) is dict else used_previously
            used_at_hand_1 = self.cards_per_player_hand_i*self.player_range[1] + self.board_distribution_hand_i
            trash_pile_distribution = self.trash_pile_distribution_hand_i if self.distribution_ordering[-1] != Distributee.TRASH_PILE \
                else self.deck_size - used_at_hand_0 - used_at_hand_1
            trash_pile_distribution = min(trash_pile_distribution, self.trash_pile_distribution_hand_i)

            return used_at_hand_1 + trash_pile_distribution

        elif type(self.cards_per_player_hand_i) is dict:
            counter = dict()
            for player_count, card_count in self.cards_per_player_hand_i.items():
                used_at_hand_0 = used_previously[player_count] if type(used_previously) is dict else used_previously
                used_at_hand_1 = card_count*player_count + self.board_distribution_hand_i
                trash_pile_distribution = self.trash_pile_distribution_hand_i if self.distribution_ordering[-1] != Distributee.TRASH_PILE \
                    else self.deck_size - used_at_hand_0 - used_at_hand_1
                trash_pile_distribution = min(trash_pile_distribution, self.trash_pile_distribution_hand_i)

                counter[player_count] = used_at_hand_1 + trash_pile_distribution
            return counter
        else:
            raise ValidationError #TODO this is just for my IDE to not think there's sth wrong. let's see if this cuases UX issue...

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
    def __validate_card_distribution(cls, deck_size: int, used_previously: int, cards_to_distribute: int):
        return deck_size - used_previously >= cards_to_distribute

    @classmethod
    def __validation_wrapper(cls,
        cards_to_distribute: NonNegativeInt | Dict[PositiveInt, NonNegativeInt],
        deck_size: PositiveInt,
        used_previously: PositiveInt,
        max_players: PositiveInt,
        cards_per_player: NonNegativeInt | Dict[PositiveInt, NonNegativeInt],
        hand: str,
        cards_to_board: NonNegativeInt, cards_to_trash: NonNegativeInt
    ):
        if type(cards_to_distribute) is int:
            if not Rules.__validate_card_distribution(
                deck_size=deck_size,
                used_previously=used_previously,
                cards_to_distribute=cards_to_distribute
            ):
                raise CardDistributionError(
                    """More cards are being handed out to players than there are cards available. The math follows:"""
                    """\n {} (deck_size) - {} (previously used cards) < {} (max_player_count) X {} (cards_per_player_hand_{}) + {} (cards to board) + {} (cards to trash pile) = {} (cards_to_distribute_hand_{})""".format(
                        deck_size, used_previously, max_players, cards_per_player, hand, cards_to_board, cards_to_trash, cards_to_distribute, hand
                    )
                )
        elif type(cards_to_distribute) is dict:
            rule_violations = DefaultDict[PositiveInt, str]()
            error_msg_header = """More cards are beign handed out to players than there are cards available at the following configs: \n"""
            error_msg_body = \
            """ Player Count = {} | {} (deck_size) - {} (previously used cards) < {} (player_count) X {} (cards_per_player_hand_{}) + {} (cards to board) + {} (cards to trash pile) = {} (cards_to_distribute_hand_{}) \n"""
            for player_count, total_cards_to_players in cards_to_distribute.items():
                if not Rules.__validate_card_distribution(
                    deck_size=deck_size,
                    used_previously=used_previously,
                    cards_to_distribute=total_cards_to_players
                ):
                    rule_violations[player_count] = error_msg_body.format(
                        player_count, deck_size, used_previously, player_count, cards_per_player[player_count], hand, cards_to_board, cards_to_trash, total_cards_to_players, hand
                    )

            if rule_violations:
                raise CardDistributionError(
                    error_msg_header + "".join(rule_violations.values())
                )

    # Make sure total cards distributed <= cards left unused
    # Logic is simple: Deck Size - Previously_Used < cards to distribute -> then Rule is Ill-formed
    @model_validator(mode="after")
    def validate_hand_0(self): #TODO: This does not consider whether it receives from trash_pile or not
        """Simply compare whether the number of cards used in hand 0 is below the deck size so we may play
        """

        # Then run validations
        cards_to_distribute = self.total_cards_distributed_hand_0

        Rules.__validation_wrapper(
            cards_to_distribute=cards_to_distribute,
            deck_size=self.deck_size,
            used_previously=0, # it's the first hand, nothing's been used
            max_players=self.player_range[1],
            cards_per_player=self.cards_per_player_hand_0,
            hand="0",
            cards_to_board=self.board_distribution_hand_0, cards_to_trash=self.trash_pile_distribution_hand_0
        )
        return self

    # Make sure total cards distributed <= cards left unused
    # Logic is simple: Deck Size - Previously_Used < cards to distribute -> then Rule is Ill-formed
    @model_validator(mode="after")
    def validate_hand_i(self):

        cards_to_distribute = self.total_cards_distributed_hand_i

        # Calculate cards that shouldn't be used first
        used_previously = self.total_cards_distributed_hand_0
        if type(used_previously) is int:
            Rules.__validation_wrapper(
                cards_to_distribute=cards_to_distribute,
                deck_size=self.deck_size,
                used_previously=used_previously,
                max_players=self.player_range[1],
                cards_per_player=self.cards_per_player_hand_i,
                hand="i",
                cards_to_board=self.board_distribution_hand_i, cards_to_trash=self.trash_pile_distribution_hand_i
            )
        elif type(used_previously) is dict:
            error_msg_header = "Hand i rule violations as follows: \n"
            rule_violations = DefaultDict[PositiveInt, str]()
            for player_count, used_card_count in used_previously.items():

                try:
                    Rules.__validation_wrapper(
                        cards_to_distribute=cards_to_distribute,
                        deck_size=self.deck_size,
                        used_previously=used_card_count,
                        max_players=self.player_range[1],
                        cards_per_player=self.cards_per_player_hand_i,
                        hand="i",
                        cards_to_board=self.board_distribution_hand_i, cards_to_trash=self.trash_pile_distribution_hand_i
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
                raise ValidationError(
                    """
                    Cannot distribute cards to such an entity ('{}')
                    Please check 'distribution_ordering' to see if it contains something that is not in 'player', 'unused', 'board', or 'trash_pile'
                    """.format(distributee)
                )
            if not isinstance(distribution_method, CardDistributionMethod):
                raise ValidationError(
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
                raise ValidationError(
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
