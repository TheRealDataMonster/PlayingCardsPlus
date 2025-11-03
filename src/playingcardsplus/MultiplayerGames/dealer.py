from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.player import Player, PlayerDecision_InstructionSet

from typing_extensions import Optional, List, Dict, Iterable, Tuple
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field



class DealerBehavior(BaseModel):
    """
    Defines a behavior that a dealer can take. Normally, it should be instantiated within the Game object so it can track Players

    Enables devs to control whether devs are fair or treats certain players favorably or unfavorably

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
    """
    name: str = Field(frozen=True)
    fair: bool = True # If not fair then it also can look up card ordering
    liked_players: Optional[List[Player]]
    disliked_players: Optional[List[Player]]
    soul: Optional[Dict]


class Dealer(BaseModel, ABC):
    """
    Dealer comes in to any Game and should deal based on rules dictated by the Game, which gives the Dealer status about the Game.
    Assumes that the Game object is acting in good faith and is correct.

    When players communicate their action - in instruction sets, Dealers actually execute. When they execute, they're reading getters and setters in MultiPlayerDeck
    """
    #TODO: need a way to track and verify here that a Dealer is indeed dealing for a specific game
    #TODO: And that it has indeed received status about the Game from the Game object

    name: str = Field(frozen=True)
    _behavior: DealerBehavior
    _game_assigned: bool = False # TODO: prob will eventually have to become some sort of handshake/signature signing auth thing

    @property
    def behavior(self) -> DealerBehavior:
        return self._behavior

    @property
    def game_assigned(self) -> bool:
        return self._game_assigned

    # @behavior.setter
    # def update_behavior(self, new_behavior: DealerBehavior): # might lead to bad practices... Most changes should be programmed to the Soul
    #     self._behavior = new_behavior

    @game_assigned.setter
    def __assign_game(self):
        self._game_assigned = True

    @game_assigned.setter
    def _unassign_game(self):
        self._game_assigned = False

    #TODO: making sure these are only callable by the Game Object
    @abstractmethod
    def _deal(self, players: Iterable[Player], rules: Dict[str, str | int | float], deck: MultiPlayerDeck) -> Tuple[MultiPlayerDeck, Iterable[Player]]:
        """
        Deals cards to the players + set up the board conditions

        Args:
            players: A list of Player objects to deal to.
            cards_per_player: The number of cards each player should receive.

        Returns:
            A tuple containing the new deck and each Player
        """
        ...

    @abstractmethod #TODO: may not need to be abstract because rules may not be relevant here... or structure is pre-determined
    def _handle_player_actions(self, player: Player, actions: Iterable[PlayerDecision_InstructionSet], deck: MultiPlayerDeck, rules: Dict[str, str | int | float]):
        """
        For each action that a Player takes, execute those based on the provided rules then update the Deck
        """
        ...
