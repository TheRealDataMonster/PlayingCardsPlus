from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.player import PlayerDecision_InstructionSet, Instruction
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.custom_error import PlayerRangeError, CardDistributionError

from pydantic import ValidationError

import pytest
from contextlib import nullcontext as does_not_raise

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
__wrong_distribution_method2 = {
    Distributee.PLAYER: 124,
    "trash_pile": CardDistributionMethod.LUMP,
    Distributee.BOARD: CardDistributionMethod.LUMP,
    Distributee.UNUSED: CardDistributionMethod.LUMP,
}

__correct_distribution_ordering = [
    Distributee.PLAYER, Distributee.BOARD, Distributee.TRASH_PILE, Distributee.UNUSED
]

__wrong_distribution_ordering = [
    "player", "wut",  Distributee.BOARD, Distributee.TRASH_PILE
]




def test_rules_creation():
    rules_valid = Rules(
        deck_size=52,
        player_range=(2,5),

        allow_trash_pile_addition=False,
        cards_per_player_hand_0={
            2: 12,
            3: 8,
            4: 7,
            5: 7,
        },
        cards_per_player_hand_i=1,
        board_distribution_hand_0=2,
        board_distribution_hand_i=3,
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
    assert(rules_valid)
    assert(rules_valid.model_dump())


@pytest.mark.parametrize("kwargs, expected_exception",
    [
        (
            {
                "deck_size":52,
                "player_range":(2,5),
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":{
                    2: 30, # Too many Cards!!!!
                    3: 30,
                    4: 7,
                    5: 7,
                },
                "cards_per_player_hand_i":1,
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(CardDistributionError)
        ),

        (
            {
                "deck_size":52,
                "player_range":(2,5),
                "allow_trash_pile_addition":False,
                "cards_per_player_hand_0":7,
                "cards_per_player_hand_i": 30, # Too many Cards!!!!
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(CardDistributionError)
        ),

        (
            {
                "deck_size":52,
                "player_range":(2,5),
                "allow_trash_pile_addition":False,
                "cards_per_player_hand_0":{
                    2: 8,
                    3: 8,
                    4: 7,
                    5: 7,
                },
                "cards_per_player_hand_i": {
                    2: 1, # Too many Cards!!!!
                    3: 3, # Too many Cards!!!!
                    4: 7,
                    5: 70,
                },
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(CardDistributionError)
        ),

        (
            {
                "deck_size":52,
                "player_range":(5,4), # uho no
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":{
                    2: 8,
                    3: 8,
                    4: 7,
                    5: 7,
                },
                "cards_per_player_hand_i":1,
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(PlayerRangeError)
        ),

        (
            {
                "deck_size":52,
                "player_range":(5,5), # This should not throw an error
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":{
                    2: 8,
                    3: 8,
                    4: 7,
                    5: 7,
                },
                "cards_per_player_hand_i":1,
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, does_not_raise()
        ),

        (
            {
                "deck_size":52,
                "player_range":(5,6),
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":"hello",
                "cards_per_player_hand_i":1,
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(ValidationError)
        ),
        (
            {
                "deck_size":"52",
                "player_range":(5,5),
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":"5",
                "cards_per_player_hand_i":"1", #apparently this is ok
                "board_distribution_hand_0":"2",
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, does_not_raise()
        ),

        (
            {
                "deck_size":"52",
                "player_range":(5,5),
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":"5",
                "cards_per_player_hand_i":"1", #apparently this is ok
                "board_distribution_hand_0":"2",
                "board_distribution_hand_i":3,
                "distribution_methods":__wrong_distribution_method,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(ValidationError)
        ),
        (
            {
                "deck_size":"52",
                "player_range":(5,5),
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":"5",
                "cards_per_player_hand_i":"1", #apparently this is ok
                "board_distribution_hand_0":"2",
                "board_distribution_hand_i":3,
                "distribution_methods":__wrong_distribution_method2,
                "distribution_ordering":__correct_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(ValidationError)
        ),
        (
            {
                "deck_size":52,
                "player_range":(5,7),
                "allow_trash_pile_addition": False,
                "cards_per_player_hand_0":5,
                "cards_per_player_hand_i":1, #apparently this is ok
                "board_distribution_hand_0":2,
                "board_distribution_hand_i":3,
                "distribution_methods":__correct_distribution_method,
                "distribution_ordering":__wrong_distribution_ordering,
                "instructions": PlayerDecision_InstructionSet(operations=[Instruction(op="foo"),Instruction(op="bar")]),
                "instruction_constraints":{}
            }, pytest.raises(ValidationError)
        ),
    ]
)
def test_rules_creation_failure(kwargs, expected_exception):
    with expected_exception:
        Rules(**kwargs)


    # assert expected_exception == error.value
