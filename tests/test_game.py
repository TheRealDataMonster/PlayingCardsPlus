from playingcardsplus.MultiplayerGames.deck import MultiPlayerDeck, Distributee
from playingcardsplus.MultiplayerGames.dealer import Dealer, DealerBehavior, CardDistributionMethod
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet, Instruction
from playingcardsplus.MultiplayerGames.game import Game

from playingcardsplus.custom_error import GameUnassignedError

import pytest

__correct_other_card_distribution_0 = {
    Distributee.BOARD: 1,
    Distributee.TRASH_PILE: 0,
    Distributee.UNUSED: 0
}

__correct_other_card_distribution_i = {
    Distributee.BOARD: 1,
    Distributee.TRASH_PILE: 0,
    Distributee.UNUSED: 0
}

__correct_distribution_method = {
    Distributee.PLAYER: CardDistributionMethod.LUMP,
    Distributee.TRASH_PILE: CardDistributionMethod.LUMP,
    Distributee.BOARD: CardDistributionMethod.LUMP,
    Distributee.UNUSED: CardDistributionMethod.LUMP,
}
__wrong_distribution_method = {
    Distributee.PLAYER: 124,
    Distributee.TRASH_PILE: "Fre",
    Distributee.BOARD: CardDistributionMethod.LUMP,
    Distributee.UNUSED: CardDistributionMethod.LUMP,
}

__correct_distribution_ordering = [
    Distributee.PLAYER, Distributee.BOARD, Distributee.TRASH_PILE, Distributee.UNUSED
]

# def test_game_creation():
#     deck = MultiPlayerDeck(name="French_Multi_Player_Deck_NoJocker", joker_count=0)
#     normal_behavior = DealerBehavior(name="Normal Fair", fair=True)
#     dealer = Dealer(name="Ordinary Dealer", initial_behavior=normal_behavior)

#     rules_valid = Rules(
#         deck_size=52,
#         player_range=(2,5),
#         cards_per_player_hand_0={
#             2: 12,
#             3: 8,
#             4: 7,
#             5: 7,
#         },
#         cards_per_player_hand_i=1,
#         other_card_distribution_hand_0=__correct_other_card_distribution_0,
#         other_card_distribution_hand_i=__correct_other_card_distribution_i,
#         distribution_methods=__correct_distribution_method,
#         distribution_ordering=__correct_distribution_ordering,
#         instructions=PlayerDecision_InstructionSet(
#             operations = [
#                 Instruction(op="foo"),
#                 Instruction(op="bar")
#             ]
#         ),
#         instruction_constraints={
#         }
#     )

    # game = Game(name="Game")



# class TestGameCreation(unittest.TestCase):
#     def create_game(self):
#         # assert Game creation states like Dealer,  Deck, Roster scoreboard
#         pass
#     def rotate_roster(self): # Ds check
#         pass
