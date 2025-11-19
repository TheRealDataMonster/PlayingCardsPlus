"""
Testing Rules. Largely there are 2 case scenarios
1) Ill-formatted Rules, which should just result in Valdiation Error
2) CardDistributionError cases where the way the cards are beign handed out is invalid, meaning they'd run out of cards without being able to finish
distributing hand i at least once.


Note that technically, the right way to test the CardDistributionError cases is to test small card usage cases, overly large cases that'll obvious fail
Then test all the borders. Borders meaning solution to the following problem
"mu*(a*x1 + x2 + x3) + (b*y1 + y2 + y3) <= deck_size"
Finding solutions that satisfies this is an Integer Programming problem which is NP-Hard.
It could be done I think we can get away by constraining some x and y values and finding single solutions which is just a linear equation
"""


from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.instructions import InstructionSet, Instruction
from playingcardsplus.MultiplayerGames.deck import Distributee
from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.custom_error import RuleIllFormedError, PlayerRangeError, CardDistributionError

from typing_extensions import Tuple, Dict, List
from pydantic import ValidationError
import itertools

import pytest
from contextlib import nullcontext as does_not_raise


__correct_distribution_method = {
    Distributee.PLAYER: CardDistributionMethod.LUMP,
    Distributee.TRASH_PILE: CardDistributionMethod.LUMP,
    Distributee.BOARD: CardDistributionMethod.LUMP,
    Distributee.UNUSED: CardDistributionMethod.LUMP,
}
__wrong_distribution_method = {
    Distributee.PLAYER: CardDistributionMethod.LUMP,
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
__correct_distribution_ordering_permutations = list(itertools.permutations(__correct_distribution_ordering))


__wrong_distribution_ordering = [
    "player", "wut",  Distributee.BOARD, Distributee.TRASH_PILE
]

@pytest.mark.skip("not a test but a helper to run tests")
def foo():
    return "foo!"

@pytest.mark.skip("not a test but a helper to run tests")
def bar():
    return "foobar!"

# Test cases:
# 1) early hands size = 1
# 2) early hands size > 1
# 3) repeat for all allowed permutations? - distribution ordering & distribution methods?
@pytest.mark.skip("not a test but a helper to write tests")
def __generate_rules(
    early_hands_counts: Tuple,
    player_early_hands_dict: bool = False,
    distribution_method: Dict[Distributee, CardDistributionMethod] = __correct_distribution_method,
    distribution_ordering: List[Distributee] = __correct_distribution_ordering,
    player_range: Tuple[int, int] = (2, 5),
    player_0_multiplier: int = 1,
    board_0_multiplier: int = 1,
    trash_0_multiplier: int = 1,
    player_i_multiplier: int = 1,
    board_i_multiplier: int = 1,
    trash_i_multiplier: int = 1
):
    return {
        "deck_size": 52,
        "player_range": player_range,
        "cards_per_player_early_hands": [{
            2: 1*player_0_multiplier,
            3: 1,
            4: 1
        }] * early_hands_counts[0] if player_early_hands_dict else [1*player_0_multiplier] * early_hands_counts[0],
        "cards_per_player_hand_i": 1*player_i_multiplier,
        "board_distribution_early_hands": [1 * board_0_multiplier] * early_hands_counts[1],
        "board_distribution_hand_i": 1*board_i_multiplier,
        "trash_pile_distribution_early_hands": [1*trash_0_multiplier] * early_hands_counts[2],
        "trash_pile_distribution_hand_i": 1*trash_i_multiplier,
        "distribution_methods": distribution_method,
        "distribution_ordering": distribution_ordering,
        "instructions":InstructionSet(
            {Instruction(operation="foo"), Instruction(operation="bar")}
        ),
        "instruction_constraints":{}
    }

params_valid = [__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=ordering) for ordering in __correct_distribution_ordering_permutations]
params_valid.extend([__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=ordering) for ordering in __correct_distribution_ordering_permutations])
params_valid = [__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=True, distribution_method=__correct_distribution_method, distribution_ordering=ordering) for ordering in __correct_distribution_ordering_permutations]
params_valid.extend([__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=True, distribution_method=__correct_distribution_method, distribution_ordering=ordering) for ordering in __correct_distribution_ordering_permutations])


@pytest.mark.parametrize("kwargs", params_valid)
def test_rules_creation(kwargs):
    rules_valid = Rules(**kwargs)
    assert(rules_valid)
    assert(rules_valid.model_dump())


params_invalid_card_distribution = [
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_0_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_0_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_0_multiplier=100), pytest.raises(CardDistributionError)),

    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_i_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_i_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_i_multiplier=100), pytest.raises(CardDistributionError)),

    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_0_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_0_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_0_multiplier=100), pytest.raises(CardDistributionError)),

    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_i_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_i_multiplier=100), pytest.raises(CardDistributionError)),
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_i_multiplier=100), pytest.raises(CardDistributionError))
]
params_invalid_deck_size = [
    (__generate_rules(early_hands_counts=(1,1,1)), pytest.raises(ValidationError)) for _ in range(3)
]
params_invalid_deck_size[0][0]["deck_size"] = "hello"
params_invalid_deck_size[1][0]["deck_size"] = 52.7
params_invalid_deck_size[2][0]["deck_size"] = -10

params_invalid_player_range = [
    (__generate_rules(early_hands_counts=(1,1,1)), pytest.raises(ValidationError)) for _ in range(3)
]

params_invalid_player_range[0][0]["player_range"] = "Frefe"
params_invalid_player_range[1][0]["player_range"] = (0.1, 4.3)
params_invalid_player_range[2][0]["player_range"] = (-1, 4)
params_invalid_player_range.append(
    (__generate_rules(early_hands_counts=(1,1,1)), pytest.raises(PlayerRangeError))
)
params_invalid_player_range[3][0]["player_range"] = (4,2)

params_invalid_distribution_method_and_ordering = [
    (__generate_rules(early_hands_counts=(1,1,1), distribution_method=distribution_method), pytest.raises(ValidationError)) for distribution_method in [__wrong_distribution_method, __wrong_distribution_method2]
]
params_invalid_distribution_method_and_ordering.append(
    (__generate_rules(early_hands_counts=(1,1,1), distribution_ordering=__wrong_distribution_ordering), pytest.raises(ValidationError))
)




params_invalid = []
params_invalid.extend(params_invalid_card_distribution)
params_invalid.extend(params_invalid_deck_size)
params_invalid.extend(params_invalid_player_range)
params_invalid.extend(params_invalid_distribution_method_and_ordering)
params_invalid.append(
    #early hands size doesn't match
    (__generate_rules(early_hands_counts=(1,2,1)), pytest.raises(RuleIllFormedError))
)


@pytest.mark.parametrize("kwargs, expected_exception", params_invalid)
def test_rules_creation_failure(kwargs, expected_exception):
    with expected_exception:
        Rules(**kwargs)



# Let's test some cases that are really close but should be valid rules
#
#
#
#
#  -> so I get a sort of a probabilistic estimation here on the correct ness
# I need to test variety of cases where these kind of threshold are almost met
#  -> things blowing up at x
#  -> thngs blowing up at y


params_almost_invalid = [
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_0_multiplier=8), does_not_raise()), # (5 * 8 + 1 + 1) + (5 * 1 + 1 + 1) = 49
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_0_multiplier=39), does_not_raise()), # (5 * 1 + 39 + 1) + (5 * 1 + 1 + 1) = 52
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_0_multiplier=39), does_not_raise()), # (5 * 1 + 1 + 39) + (5 * 1 + 1 + 1) = 52

    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_i_multiplier=8), does_not_raise()), # (5 * 1 + 1 + 1) + (5 * 8 + 1 + 1)  = 49
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_i_multiplier=39), does_not_raise()), # (5 * 1 + 1 + 1) + (5 * 1 + 39 + 1) = 52
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_i_multiplier=39), does_not_raise()), # (5 * 1 + 1 + 1) + (5 * 1 + 1 + 39) = 52

    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_0_multiplier=2), does_not_raise()), # 3*(5 * 2 + 1 + 1) + (5 * 1 + 1 + 1) = 43
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_0_multiplier=9), does_not_raise()), # 3*(5 * 1 + 9 + 1) + (5 * 1 + 1 + 1) = 52
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_0_multiplier=9), does_not_raise()), # 3*(5 * 1 + 1 + 9) + (5 * 1 + 1 + 1) = 52

    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_i_multiplier=5), does_not_raise()), # 3*(5 * 1 + 1 + 1) + (5 * 5 + 1 + 1) = 48
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_i_multiplier=25), does_not_raise()), # 3*(5 * 1 + 1 + 1) + (5 * 1 + 25 + 1) = 52
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_i_multiplier=25), does_not_raise()) # 3*(5 * 1 + 1 + 1) + (5 * 1 + 1 + 26) = 52
]

params_almost_valid = [
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_0_multiplier=9), pytest.raises(CardDistributionError)), # (5 * 8 + 1 + 1) + (5 * 1 + 1 + 1) = 49 -> 49 + 5*1 = 53
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_0_multiplier=40), pytest.raises(CardDistributionError)), # (5 * 1 + 39 + 1) + (5 * 1 + 1 + 1) = 52 -> 52 + 1 = 53
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_0_multiplier=40), pytest.raises(CardDistributionError)), # (5 * 1 + 1 + 39) + (5 * 1 + 1 + 1) = 52 -> 52 + 1 = 53

    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_i_multiplier=9), pytest.raises(CardDistributionError)), # (5 * 1 + 1 + 1) + (5 * 8 + 1 + 1) = 49 -> 49 + 5*1 = 53
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_i_multiplier=40), pytest.raises(CardDistributionError)), # (5 * 1 + 1 + 1) + (5 * 1 + 39 + 1) = 52 -> 52 + 1 = 53
    (__generate_rules(early_hands_counts=(1,1,1), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_i_multiplier=40), pytest.raises(CardDistributionError)), # (5 * 1 + 1 + 1) + (5 * 1 + 1 + 39) = 52 -> 52 + 1 = 53

    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_0_multiplier=3), pytest.raises(CardDistributionError)), # 3*(5 * 2 + 1 + 1) + (5 * 1 + 1 + 1) = 43 -> 43 + 3*5*1 = 58
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_0_multiplier=10), pytest.raises(CardDistributionError)), # 3*(5 * 1 + 9 + 1) + (5 * 1 + 1 + 1) = 52 -> 52 + 3*1 = 55
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_0_multiplier=10), pytest.raises(CardDistributionError)), # 3*(5 * 1 + 1 + 9) + (5 * 1 + 1 + 1) = 52 -> 52 + 3*1 = 55

    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        player_i_multiplier=6), pytest.raises(CardDistributionError)), # 3*(5 * 1 + 1 + 1) + (5 * 5 + 1 + 1) = 48 -> 48 + 5*1 = 53
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        board_i_multiplier=26), pytest.raises(CardDistributionError)), # 3*(5 * 1 + 1 + 1) + (5 * 1 + 25 + 1) = 52 -> 52 + 1 = 53
    (__generate_rules(early_hands_counts=(3,3,3), player_early_hands_dict=False, distribution_method=__correct_distribution_method, distribution_ordering=__correct_distribution_ordering,
        trash_i_multiplier=26), pytest.raises(CardDistributionError)) # 3*(5 * 1 + 1 + 1) + (5 * 1 + 1 + 26) = 52 -> 52 + 1 = 53
]
params_border = []
params_border.extend(params_almost_invalid)
params_border.extend(params_almost_valid)

@pytest.mark.parametrize("kwargs, expected_exception", params_border)
def test_borderline_rules(kwargs, expected_exception):
    with expected_exception:
        Rules(**kwargs)
