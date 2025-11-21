from playingcardsplus.MultiplayerGames.player import Player
from playingcardsplus.MultiplayerGames.instructions import Instruction, InstructionSet, InstructionSetImplementer
from playingcardsplus.MultiplayerGames.dealer import DealerBehavior, Dealer
from playingcardsplus.MultiplayerGames.deck import Distributee, MultiPlayerDeck
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.game import Game
from playingcardsplus.dealer import CardDistributionMethod

# from typing_extensions import Dict, Iterable, Optional, Tuple

__HoldemPlayerOperations = InstructionSet(
    instructions={
        Instruction(operation="bet"), # includes raising
        Instruction(operation="fold"),
        Instruction(operation="check"),
    }
)

class HoldemInstructionSet(InstructionSetImplementer):

__HoldemRules = Rules(
    deck_size=52,
    player_range=(2,10),
    cards_per_player_early_hands=[2, 0], # pre-flop and flop
    cards_per_player_hand_i=0, # turn, river
    board_distribution_early_hands=[0, 3],
    board_distribution_hand_i=1,
    trash_pile_distribution_early_hands=[0, 1],
    trash_pile_distribution_hand_i=1,
    distribution_methods= {
        Distributee.PLAYER: CardDistributionMethod.LUMP,
        Distributee.TRASH_PILE: CardDistributionMethod.LUMP,
        Distributee.BOARD: CardDistributionMethod.LUMP,
        Distributee.UNUSED: CardDistributionMethod.LUMP,
    },
    distribution_ordering=[
        Distributee.TRASH_PILE, Distributee.PLAYER, Distributee.BOARD, Distributee.UNUSED
    ], # at most hands, you burn 1 card first then
    instructions=__HoldemPlayerOperations,
    instruction_constraints={}
)



class TexasHoldem(Game):
    pass
