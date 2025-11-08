from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck, Distributee
from playingcardsplus.MultiplayerGames.player import (
    Player,
    PlayerDecision_InstructionSet,
    Instruction
)
from playingcardsplus.MultiplayerGames.rules import Rules

from playingcardsplus.custom_error import RuleViolationError, RuleIllFormedError, DealerError, GameUnassignedError
from playingcardsplus.card import Card, JokerCard
from playingcardsplus.dealer import CardDistributionMethod

from typing_extensions import Optional, List, Dict, Iterable, Tuple, Deque
from abc import ABC, abstractmethod
# from dataclasses import dataclass
# from typing_extensions import ClassVar
from pydantic import BaseModel, Field, ConfigDict, NonNegativeInt


# TODO: In multi-host env this maybe necessary? Otherwise, the env that hosts the Dealer should control this and prove this
# -> That is to be determined - let's see if this weighs in on the performance at all
class DealerBehavior(BaseModel):
    """
    Defines a behavior that a dealer can take.
    Enables devs to control whether dealers are fair or treats certain players favorably or unfavorably

    For example:
    #    Behaviors:
    #       -> (fair) Default: No info other than Deck & Player count
    #       -> (Unfair) Favoritism: Uses card ordering to advantage certain players
    #       -> (Unfair) Ijime/Bully: Uses card ordering to disadvantage certain players

    Once a "Soul" is attached, it may change its fairness and favored/unfavored player based on its "mood"
    #   - "Soul" attachable:
    #       -> can be paramterized in a way where it really dislikes/likes players or this maybe fickle
    #       -> but a sense of justice may over-ride
    #

    For example, Normal Fair Dealer actually should not contain anything other than the name and fair = True
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(frozen=True)
    fair: bool = True  # If not fair then it also can look up card ordering
    liked_players: Optional[List[Player]] = None
    disliked_players: Optional[List[Player]] = None
    soul: Optional[Dict] = None # Contains variety of behavioral parameter & conditions for change

# @dataclass
# class DealerBehavior:
#     name: str
#     fair: bool = True  # If not fair then it also can look up card ordering
#     liked_players: Optional[List[Player]] = None
#     disliked_players: Optional[List[Player]] = None
#     soul: Optional[Dict] = None # Contains variety of behavioral parameter & conditions for change

#     _immutable_fields: ClassVar[set] = {'name'}

#     def __setattr__(self, name, value):
#         if name in self._immutable_fields:
#             raise AttributeError(f"Cannot modify immutable field '{name}' after initialization")
#         # For all other cases, use the standard setattr behavior
#         object.__setattr__(self, name, value)


class AbstractDealer(ABC):
    """
    Dealer comes in to any Game and should deal based on rules dictated by the Game, which gives the Dealer status about the Game.
    Assumes that the Game object is acting in good faith and is correct.

    When players communicate their action - in instruction sets, Dealers actually execute. When they execute, they're reading getters and setters in MultiPlayerDeck
    """

    def __init__(self, name: str, initial_behavior: DealerBehavior):
        self.__name = name
        self.__behavior = initial_behavior # It's bad practice to change this - should be changed as a result of Soul updating itself
        self.__game_assigned = False # TODO: prob will eventually have to become some sort of handshake/signature signing auth thing

    @property
    def name(self) -> str:
        return self.__name

    @property
    def behavior(self) -> DealerBehavior:
        return self.__behavior

    @property
    def game_assigned(self) -> bool:
        return self.__game_assigned

    def _toggle_game_assignment(self):
        self.__game_assigned = not self.__game_assigned


    # TODO: ok maybe reconsider this later - for better
    # @classmethod
    # def toggle_game_assignment(cls, dealer: 'Dealer', game: Game):
    #     if dealer == game.dealer:
    #         dealer._toggle_game_assignment()
    #

    # def update_behavior(self, new_behavior: DealerBehavior): # might lead to bad practices... Most changes should be programmed to the Soul
    #     self._behavior = new_behavior

    @abstractmethod
    def deal(self, players: List[Player], rules: Rules, deck: MultiPlayerDeck, turn: int) -> Tuple[MultiPlayerDeck, Iterable[Player]]:
        """
        Deals cards to the players + set up the board conditions

        Args:
            players: A list of Player objects to deal to.
            cards_per_player: The number of cards each player should receive.

        Returns:
            A tuple containing the new deck and each Player
        """
        ...

    @abstractmethod  # TODO: may not need to be abstract because rules may not be relevant here... or structure is pre-determined
    def handle_player_actions(self, player: Player, instructions: Iterable[Instruction], instruction_set: PlayerDecision_InstructionSet, deck: MultiPlayerDeck, rules: Dict[str, str | int | float]):
        """
        For each action that a Player takes, execute those based on the provided rules then update the Deck
        """
        ...


class Dealer(AbstractDealer):
    """
    Normal Dealer who is supposed to deal n cards at a time to each player
    """

    @classmethod
    def check_distribution_mistake(
        cls, total_cards_to_distribute: int, cards_distributed: int, distributee: str
    ):
        leftovers = total_cards_to_distribute - cards_distributed
        if leftovers != 0:
            raise DealerError("Cards {} to {}. We have {} {}".format(
                "under-distrubted" if leftovers > 0 else "over-distributed",
                distributee,
                abs(leftovers),
                "leftovers" if leftovers > 0 else "cards that weren't supposed to be distributed",
            ))

    @classmethod
    def discover_dealing_parameters(
        cls, players: List[Player], rules: Rules, turn: int
    ) -> Tuple[int, int, Dict[Distributee, NonNegativeInt]]:

        player_count = len(players)
        # Figure out how many to distribute to each player
        distribution_count_map = rules.cards_per_player_hand_0 if turn == 0 else rules.cards_per_player_hand_i
        if type(distribution_count_map) is int:
            player_distribution_count = distribution_count_map
        elif type(distribution_count_map) is Dict:
            try:
                player_distribution_count = distribution_count_map[player_count]
            except KeyError:
                raise RuleViolationError(
                    "Number of players is out of range! It's suppsoed to support {} ~ {} players but we have {}".format(rules.player_range[0], rules.player_range[1], player_count)
                )
        else:
            raise RuleIllFormedError(
                """Rule about how many cards are supposed to be distributed to each player is illformed."""
                """ Check {} to see if it's formatted in a Positive Integer or a Dictionary of (K,V) = Player Count, Card to be Distributed""".format(
                    "rules.cards_per_player_hand_0" if turn == 0 else "rules.cards_per_player_hand_i"
                )
            ) # Something is not recognized

        other_distribution_map = rules.other_card_distribution_hand_0 if turn == 0 else rules.other_card_distribution_hand_i

        return (player_count, player_distribution_count, other_distribution_map)

    @classmethod
    def distribute_cards_to_players(
        cls,
        distribution_method: CardDistributionMethod,
        cards: Deque[Card | JokerCard],
        players: List[Player],
        cards_distributed: int
    ) -> int:

        if distribution_method.value == "one_at_a_time":
            while len(cards) > 0:
                for player in players:
                    player._accept_card(cards.popleft())
                    cards_distributed += 1
        elif distribution_method.value == "lump":
            while len(cards) > 0:
                for player in players:
                    player._accept_card(cards.popleft())
                    cards_distributed += 1
        else:
            raise RuleIllFormedError(
                """Rule about how to distribute cards to players is ill-formed."""
                """Check rules.distribution_methods["player"] to see if it's one of 'one_at_a_time or 'lump'."""
            )
        return cards_distributed

    @classmethod
    def distribute_cards_to_others(
        cls,
        distribution_method: CardDistributionMethod,
        deck: MultiPlayerDeck,
        total_cards_to_distribute: int,
        cards_distributed: int,
        distributee: str
    ) -> int:

        def distribute(count):
            cards = deck._take_from_unused(used_count = 1)
            if distributee == "board":
                deck._add_to_board(added=cards)
            elif distributee == "trash_pile":
                deck._add_trash(trashed=cards)
            elif distributee == "unused":
                deck._replenish_unused(replenishers=[*cards])
            return len(cards)

        if distribution_method.value == "one_at_a_time":
            for i in range(total_cards_to_distribute):
                cards_distributed += distribute(1)

        elif distribution_method.value == "lump":
            cards_distributed += distribute(total_cards_to_distribute)
        else:
            raise RuleIllFormedError("'{}' Is not recognized as entity cards are meant to be distributed to".format(distributee))

        return cards_distributed


    #TODO: For now behavior is moot
    def deal(self,
        players: List[Player],
        rules: Rules,
        deck: MultiPlayerDeck,
        turn: int
    ) -> Tuple[MultiPlayerDeck, Iterable[Player]]:
        if not self.game_assigned:
            raise GameUnassignedError

        if not deck.dealer_assigned: #It's meant to be set by Game
            deck._toggle_dealer_assignment()

        # Discover some dealing parameters - really just a wrapper...
        player_count, player_distribution_count, other_distribution_map = Dealer.discover_dealing_parameters(
            players=players, rules=rules, turn=turn
        )

        #TODO: this currently doesn't take care of running outta cards

        # Distribute cards in a order that's provided - this may change depending on circumstances
        for distributee in rules.distribution_ordering:
            distribution_method = rules.distribution_methods[distributee]
            cards_distributed = 0
            try:
                total_cards_to_distribute = other_distribution_map[distributee]
            except KeyError:
                if distributee.value == "player":
                    continue
                else:
                    raise RuleIllFormedError("'{}' Is not recognized as entity cards are meant to be distributed to".format(distributee))

            if distributee.value == "player":
                # We stored the card to be a Deque so it has to be a operation wher ewe grab each card at a time
                total_cards_to_distribute = player_distribution_count*player_count # override the above

                #TODO: done in batch or 1 card at a time to actually preserve order?
                # 1) Pop from unused first & make sure deck recors as beign distributed to players
                cards = deck._take_from_unused(used_count = total_cards_to_distribute)
                deck._give_to_players(distributed = cards)

                # 2) Distribute to Each Player
                cards_distributed = Dealer.distribute_cards_to_players(
                    distribution_method=distribution_method,
                    cards=cards,
                    players=players,
                    cards_distributed = cards_distributed
                )

            elif (distributee.value == "board") or (distributee.value == "trash_pile") or (distributee.value == "unused"):
                cards_distributed = Dealer.distribute_cards_to_others(
                    distribution_method=distribution_method,
                    deck=deck,
                    total_cards_to_distribute=total_cards_to_distribute,
                    cards_distributed=cards_distributed,
                    distributee=distributee
                )
            else:
                raise RuleIllFormedError("'{}' Is not recognized as entity cards are meant to be distributed to".format(distributee)) # This is redundant

            # Check for distribution mistakes - it's just a number checker for now
            Dealer.check_distribution_mistake(
                total_cards_to_distribute=total_cards_to_distribute,
                cards_distributed=cards_distributed,
                distributee=distributee
            )
        return (deck, players)

    def handle_player_actions(self,
        player: Player,
        instructions: Iterable[Instruction],
        instruction_set: PlayerDecision_InstructionSet,
        deck: MultiPlayerDeck,
        rules: Dict[str, str | int | float]
    ):
        if not self.game_assigned:
            raise GameUnassignedError

        # TODO: where do I bring in the
        for instruction in instructions:
            for action_str in instruction_set.operations[instruction]:
                if hasattr(player, action_str) and callable(getattr(player, action_str)):
                    res = getattr(player, action_str)(deck)

    def test_action(self):
        if not self.game_assigned:
            raise GameUnassignedError
        return
