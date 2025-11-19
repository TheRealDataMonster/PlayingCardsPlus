"""
Dynamite is a game I made.
Basically you accumulate all 4 cards of the same deck and then it becomes a dynamite you can give to someone.
Once you accumulate all 4 cards you throw away those 4 and then give one of your cards to a player of your choosing
"""
from playingcardsplus.MultiplayerGames.data import CollectibleData
from playingcardsplus.MultiplayerGames.instructions import Instruction, InstructionSet
from playingcardsplus.MultiplayerGames.player import Player
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.game import Game
from playingcardsplus.dealer import CardDistributionMethod

from typing_extensions import List, Optional


#TODO:
# 1) Define Player Action
# 2) Insturction Set Design
# 3) Create Rules
# 4) Define scoring logic

__DynamitePlayerOperations = InstructionSet(
    instructions={
        Instruction(operation="claim"),
        Instruction(operation="throw"),
        Instruction(operation="draw"),
    }
)
# Specific To Dynamite
# 1) claim conditions
# 2) throw conditions - which cards to whom, how many ,etcc..
# Some of this could just be in the take action function tbh as one of the constraints

__DynamiteRules = Rules(
    deck_size=52,
    player_range=(2,5),
    cards_per_player_early_hands=[7],
    cards_per_player_hand_i=0, # players have an option to draw from unused but are not necessarily given one
    board_distribution_early_hands=[0],
    board_distribution_hand_i=0,
    trash_pile_distribution_early_hands=[0], # trash_pile is created as a result of player action but not required by the game
    trash_pile_distribution_hand_i=0,
    distribution_methods={
        Distributee.PLAYER: CardDistributionMethod.LUMP,
        Distributee.TRASH_PILE: CardDistributionMethod.LUMP,
        Distributee.BOARD: CardDistributionMethod.LUMP,
        Distributee.UNUSED: CardDistributionMethod.LUMP,
    },
    distribution_ordering=[
        Distributee.PLAYER, Distributee.BOARD, Distributee.TRASH_PILE, Distributee.UNUSED
    ],

    instructions=__DynamitePlayerOperations,
    instruction_constraints={} # TODO gotta define this better here

)


class DynamitePlayer(Player):
    """
    This wrapper/child class implements variety of functions that are used such that they change player hands information
    """

    def take_action(
        self,
        current_game_state: CollectibleMetaData,
        historical_states: List[CollectibleData],
        cheating_states: Optional[List['Player']]
    ) -> List[Instruction]:
        """
        """


class Dynamite(Game):
    def __keep_score(self): #TODO
        pass
