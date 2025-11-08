from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet, Instruction
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.dealer import CardDistributionMethod

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




def test_rules_creation():
    rules_valid = Rules(
        deck_size=52,
        player_range=(2,5),
        cards_per_player_hand_0={
            2: 12,
            3: 8,
            4: 7,
            5: 7,
        },
        cards_per_player_hand_i=1,
        other_card_distribution_hand_0=__correct_other_card_distribution_0,
        other_card_distribution_hand_i=__correct_other_card_distribution_i,
        distribution_methods=__correct_distribution_method,
        distribution_ordering=__correct_distribution_ordering,
        instructions=PlayerDecision_InstructionSet(
            operations = [
                Instruction(op="foo"),
                Instruction(op="bar")
            ]
        ),
        instruction_constraints={
        }
    )

# TODO: multiple object creation?
@pytest.mark.parametrize("args, expected_exception, expected_message", [
    ([], GameUnassignedError, "Game has not been assigned to this Dealer!"),
])
def test_rules_creation_failure():
    # TODO: Come up with a bunch of cases where it can fail and make sure it works that we can catch them
    # 1) Too many cards handed out to players -
    #   -> at hand 0
    #   -> at hand 1
    # 2) Wrong inputs
    #   -> wrong types
    #   -> wrong string matches
    # 3) [Once logic is discovered for other distribution] other distributio nmessing up
    try:
        # TODO add some more that should fail
        rules_overdealt_players_0 = Rules(
            deck_size=52,
            player_range=(3,4),
            cards_per_player_hand_0={
                3: 20, # This should FAIL!
                4: 7,
            },
            cards_per_player_hand_i=1,
            other_card_distribution_hand_0=__correct_other_card_distribution_0,
            other_card_distribution_hand_i=__correct_other_card_distribution_i,
            distribution_methods=__correct_distribution_method,
            distribution_ordering=__correct_distribution_ordering,
            instructions=PlayerDecision_InstructionSet(
                operations = [
                    Instruction(op="foo"),
                    Instruction(op="bar")
                ]
            ),
            instruction_constraints={
            }
        )
    except Exception as e:
        print("frefeferfref erf- errf- erf- er-f -erf- erf- er-")
        print(e)

    try:
        # TODO add some more that should fail
        rules_overdealt_players_1 = Rules(
            deck_size=52,
            player_range=(3,4),
            cards_per_player_hand_0=7,
            cards_per_player_hand_i={
                3: 2,
                4: 10 #SHOULD FAIL!
            },
            other_card_distribution_hand_0=__correct_other_card_distribution_0,
            other_card_distribution_hand_i=__correct_other_card_distribution_i,
            distribution_methods=__correct_distribution_method,
            distribution_ordering=__correct_distribution_ordering,
            instructions=PlayerDecision_InstructionSet(
                operations = [
                    Instruction(op="foo"),
                    Instruction(op="bar")
                ]
            ),
            instruction_constraints={
            }
        )
    except Exception as e:
        print("frefeferfref erf- errf- erf- er-f -erf- erf- er-")
        print(e)
        # assert(e == ) # TODO? catching errors bro


    try:
        # TODO add some more that should fail
        rules_wrong_types = Rules(
            deck_size=52,
            player_range=(3,4),
            cards_per_player_hand_0={
                3: 7,
                4: 7,
            },
            cards_per_player_hand_i=1,
            other_card_distribution_hand_0=__correct_other_card_distribution_0,
            other_card_distribution_hand_i=__correct_other_card_distribution_i,
            distribution_methods=__wrong_distribution_method,
            distribution_ordering=__correct_distribution_ordering,
            instructions=PlayerDecision_InstructionSet(
                operations = [
                    Instruction(op="foo"),
                    Instruction(op="bar")
                ]
            ),
            instruction_constraints={
            }
        )
    except Exception as e:
        print("frefeferfref erf- errf- erf- er-f -erf- erf- er-")
        print(e)
