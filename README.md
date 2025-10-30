# PlayingCardsPlus
Deck of Regular Playing Cards &amp; Games - Their Back-end Interfaces

This can be used to design new card games or to run variety of both AI-enabled and rules-based simulations for Games

## Starting for Simulators
Your primary interface will be through the Game object, which has functions such as start_game() and next_hand().
This way you can simulate each hand and collect data. You may choose to run analysis at the end of each hand or once the simualtion is done.

## Starting for Game Creators
For each type of Card game - ie. MultiplayerGames - there exists primitives.py where the objects within are parent obejcts that you will use to design your game.
You have 4 tasks to accomplish -
1) To create rules of the game and capture them into a specified JSON file
2) To define tpyes of actions that a player can take
3) To design instruction set that links player actions and how the game handles those actions
4) To define how scores are allocated, winning conditions for players, and stopping conditions for the game
