"""
Dynamite is a game I made.
Basically you accumulate all 4 cards of the same deck and then it becomes a dynamite you can give to someone.
Once you accumulate all 4 cards you throw away those 4 and then give one of your cards to a player of your choosing
"""

from playingcardsplus.MultiplayerGames.instructions import Instruction, InstructionSet, InstructionSetImplementer
from playingcardsplus.MultiplayerGames.player import Player
from playingcardsplus.MultiplayerGames.dealer import Dealer
from playingcardsplus.MultiplayerGames.deck import Distributee, MultiPlayerDeck
from playingcardsplus.MultiplayerGames.rules import Rules
from playingcardsplus.MultiplayerGames.game import Game
from playingcardsplus.MultiplayerGames.data import CollectibleData

from playingcardsplus.dealer import CardDistributionMethod
from playingcardsplus.card import Card, JokerCard


from typing_extensions import Deque, Dict, OrderedDict


__DynamitePlayerOperations = InstructionSet(
    instructions={
        Instruction(operation="claim"), # player has a card in a number that they like to claim
        Instruction(operation="throw"), # another player has claimed a number that a player would like to throw theirs to
        Instruction(operation="draw"), # player wold rather draw from the unused stack
        Instruction(operation="eliminate"), # player has collected all 4 of the same number and is eliminating it
    }
)

#TODO:
# 1) Define Player Action
# 2) Insturction Set Design
# 3) Create Rules
# 4) Define scoring logic
class DynamiteInstructionSet(InstructionSetImplementer):
    """
    Specific To Dynamite
    1) claim
    -> Player: Claim amongst player hands / it becomes publicly known
    -> Dealer: nothing particularly changes
    2) throw
    -> Player: Throw amongst player hands & choose to whom to give it to /
    -> Dealer: Nothing particualrly changes since dealer doesn't track who has what hands
    3) draw
    -> Player: receives a card
    -> Dealer: gives a card to player from unused
    Some of this could just be in the take action function tbh as one of the constraints
    4) eliminate: only doable once 4 cards of the same number are collected
    -> Player: I got all 4 cards throw them all away
    -> Dealer: i mean yeah ...

    """
    def claim(self, player: Player, dealer: Dealer, deck: MultiPlayerDeck, aux) -> Deque[Card | JokerCard]:
        # TODO: might need some processing for aux here? - depends on the model really!

        claimed_cards = Deque[Card | JokerCard]()
        for card in aux: # TODO make sure they include only cards of the same number!
            if player.hand[card]:
                claimed_cards.append(card) # aux picks which card to claim!
        return claimed_cards
        # TODO: need some way to keep track of who claimed what card

    def throw(self, player: Player, dealer: Dealer, deck: MultiPlayerDeck, aux) -> None:
        # TODO: might need some processing for aux here? - depends on the model really!
        # ok this is wrong
        # 1) select cards to throw
        removed = OrderedDict[Card | JokerCard, bool]()
        for card in aux:
            player.hand[card] = False
            removed[card] = True
        # 2) move around in the deck
        taken_cards = deck._take_from_players(removed=removed)
        # TODO: give to a player who claimed that number!


    def draw(self, player: Player, dealer: Dealer, deck: MultiPlayerDeck, aux) -> Deque:
        # TODO: might need some processing for aux here? - depends on the model really!
        used_cards = deck._take_from_unused(used_count=1)
        deck._give_to_players(used_cards)
        player._accept_card(used_cards[0])
        return used_cards

    def eliminate(self, player: Player, dealer: Dealer, deck: MultiPlayerDeck, aux):
        # 1) select cards to eliminate
        removed = OrderedDict[Card | JokerCard, bool]()
        for card in aux: # TODO: need to make sure that the cards being emlinated are 4 of the same number
            player.hand[card] = False
            removed[card] = True
        # 2) move aroudn in the deck
        taken_cards = deck._take_from_players(removed=removed)
        deck._add_trash(trashed=taken_cards.keys())


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






class Dynamite(Game):
    def calculate_score(self) -> Dict[Player, int]: #TODO: implement how to score dynamite and hoiw to allcoate
        # Honestly, I think this is jsut number of cards left per player because that's what the yget rated by here.
        res = dict()
        for player in self.roster:
            res[player] = sum(player.hand.values())
        return res
