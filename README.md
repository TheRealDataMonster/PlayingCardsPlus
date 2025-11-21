# PlayingCardsPlus
Deck of Regular Playing Cards &amp; Games - Their Back-end Interfaces

This can be used to design new card games or to run variety of both AI-enabled and rules-based simulations for Games

## Disclaimer
This is not yet production ready. Some work remains to make it compatible for plugging in RL agents - specifically how they see the data & testing it on a self-designed card game. At the current stage, you're more than welcome to fork it and develop those parts on your own. The workflow, hopefully, is fairly simple enough as it takes handful number of tasks to design a game and run simulations.

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
