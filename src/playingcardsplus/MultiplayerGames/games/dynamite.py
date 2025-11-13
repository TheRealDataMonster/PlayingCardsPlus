"""
Dynamite is a game I made.
Basically you accumulate all 4 cards of the same deck and then it becomes a dynamite you can give to someone.
Once you accumulate all 4 cards you throw away those 4 and then give one of your cards to a player of your choosing
"""
from playingcardsplus.custom_error import GameUnassignedError
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet, Player, Instruction
from playingcardsplus.MultiplayerGames.dealer import DealerBehavior, Dealer
from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.game import Game

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


#TODO: remains a choice whether this is wrapper or inheritance...
class DynamitePlayer(Player):
    def take_action(self, crucial_game_state: Dict, historical_state: Iterable[Dict], cheat_codes: Optional[str | int | float]) -> Iterable[PlayerDecision_InstructionSet]:
        """
        """
        # this will involve some sort of a model making a decision and that decision space will be the space of instruction set
        return


class Dynamite(Game):
    def __keep_score(self): #TODO
        pass
