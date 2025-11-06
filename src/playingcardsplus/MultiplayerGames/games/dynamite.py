"""
Dynamite is a game I made.
Basically you accumulate all 4 cards of the same deck and then it becomes a dynamite you can give to someone.
Once you accumulate all 4 cards you throw away those 4 and then give one of your cards to a player of your choosing
"""
from playingcardsplus.custom_error import GameUnassignedError
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet, Player
from playingcardsplus.MultiplayerGames.dealer import DealerBehavior, Dealer
from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.game import Game, Rules

from typing_extensions import Dict, Iterable, Optional, Tuple


#TODO:
# 1) Define Player Action
# 2) Insturction Set Design
# 3) Create Rules
# 4) Define scoring logic

# ops = PlayerDecision_InstructionSet(
#     operations={
#         "claim": ?, # claim means I will now reveal one of my cards,
#         "load": ?, # take a card from the unused,
#         "throw": ? # throw a card or two away to those who have
#     }
# )
# Specific To Dynamite
# 1) claim conditions
# 2) throw conditions - which cards to whom, how many ,etcc..
# Some of this could just be in the take action function tbh as one of the constraints

dynamite_rules = Rules(
    deck_size=52,
    player_range=(2,5),
    cards_per_player_hand_0={
        2: 12,
        3: 8,
        4: 7,
        5: 7
    },
    cards_per_player_hand_i=1,
    other_card_distribution_hand_0={
        "board":,
        "trash_pile":
    },
    instructions=,
    instruction_constraints=
)


rules = {
    # Essential Info for all games
    # 1) player range - tuple
    # 2) cards dealt per player at Hand 0 - if dict then number is arange for each of player count other wise it's an int
    # 3) cards dealt per player at Hand i, i>0
    # 4) each operation mapped into functions -= IsntructionSet
    # 5) conditions where each operation is viable


    "player_range": (2, 5),
    "cards_per_player_hand_0": {
        2: 12,
        3: 8,
        4: 7,
        5: 7
    },
    "cards_per_player_hand_i": 1,


}
class DynamitePlayer(Player):
    def take_action(self, crucial_game_state: Dict, historical_state: Iterable[Dict], cheat_codes: Optional[str | int | float]) -> Iterable[PlayerDecision_InstructionSet]:
        """
        """
        # this will involve some sort of a model making a decision and that decision space will be the space of instruction set
        return

class DynamiteDealer(Dealer):
    def _deal(self, players: Iterable[Player], rules: Dict[str, str | int | float], deck: MultiPlayerDeck) -> Tuple[MultiPlayerDeck, Iterable[Player]]:
        if self._game_assigned is False: #TODO: eventually should be some kinda auth
            raise GameUnassignedError
        for player in players:

            card_count = ?# TODO: rules would be figuring out how to deal cards here
            player._hand[] # add to player hand
            deck._take_from_unused(used_count)
            deck.__give_to_players(?)

        # TODO: have to make changes to the deck accordingly here

        pass

    def _handle_player_actions(self, player: Player, actions: Iterable[PlayerDecision_InstructionSet], deck: MultiPlayerDeck, rules: Dict[str, Any]):
        pass #TODO:


class Dynamite(Game):
    def __keep_score(self): #TODO
        pass
