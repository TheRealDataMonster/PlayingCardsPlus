# Multiplayer games have similar structure
Most multiplayer card games typically have a concept of - the board, unused cards, a trash pile (of used cards that may never be used again unless recycling is one of the rules), and hands that players have. All 52 cards of a deck are distributed across these 4.

This directory contains primitives.py - for defining atomic components that various developers can use to develop a new multiplayer card game - and various multiplayer games that's been developed.

## What is primitives.py?
primitives.py defines obejcts to be used throughout developing different types of multiplayer games.

It intends to separate different entities such as Players, Dealers, and Game while intended to carrying through a single Deck object. Each entity is intended to communicate via use specified protocol(s) - ie. RPC, HTTPS - to enable them to be hosted across different instances. You may host them all lcoally.

If you are into creating a whole new concept of a card game, feel free to fork and add on new concepts to define your own primitives.

# Structure


All games need to have a well defined JSON that contains - rules of engagement - which included various values attached, well defined actions, way to track current state of the game, player limits, cards dealt and how to deal more cards to players' hands and the board, etc...
