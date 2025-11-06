from playingcardsplus.card import Rank, Suit, Card, JokerCard, Color

from typing_extensions import List


def create_french_cards(joker_count: int = 0) -> List[Card | JokerCard]:
    cards = []
    for rank in Rank:
        for suit in Suit:
            cards.append(Card(rank=rank.value, suit=suit.value))

    i = 1
    while i <= joker_count:
        for color_member in Color:
            cards.append(JokerCard(color=color_member.value, number=i))
            i += 1
            if i > joker_count:
                break

    return cards
