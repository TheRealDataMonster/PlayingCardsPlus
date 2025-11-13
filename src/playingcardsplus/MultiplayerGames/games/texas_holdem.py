from playingcardsplus.custom_error import GameUnassignedError
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet, Player, Instruction
from playingcardsplus.MultiplayerGames.dealer import DealerBehavior, Dealer
from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.game import Game

from typing_extensions import Dict, Iterable, Optional, Tuple

#TODO: in heold'em you distributethe cards at turn 0 to players first then at turn 1 you put 3 cards on the board, and then so on....
__HoldemRules = Rules(
    deck_size=52,
    player_range=(2,10),
    cards_per_player_hand_0=2,
    cards_per_player_hand_i=0,
    board_distribution_hand_0=3,
    board_distribution_hand_i=1,
    trash_pile_distribution_hand_0=1,
    trash_pile_distribution_hand_i=1,
    distribution_methods=,
    distribution_ordering=,
    allow_board_to_players=,
    allow_trash_pile_to_players=,
    allow_players_to_board=,
    allow_trash_pile_to_board=,
    allow_players_to_trash_pile=,
    allow_board_to_trash_pile=,
    allow_players_to_unused=,
    allow_board_to_unused=,
    allow_trash_pile_to_unused=,
    instructions=,
    instruction_constraints=,
)



class TexasHoldem(Game):
    pass
