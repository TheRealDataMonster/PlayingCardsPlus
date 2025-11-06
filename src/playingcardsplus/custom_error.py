"""
Various custom errors to help debug
"""

class DeckNotEqualError(Exception):
    """Use it when you are mixing decks that are not the same"""

    def __init__(self, message: str = "Decks being mixed are not same!"):
        self.message = message
        super().__init__(self.message)


class DuplicateCardError(Exception):
    """Error to raise when a Duplicate Card ina deck has been spotted"""

    def __init__(self, message: str = "Duplicate Card is being used somewhere!"):
        self.message = message
        super().__init__(self.message)


class DeckInlclusionError(Exception):
    """Error to raise when a Card is not included in the Deck"""

    def __init__(self,message: str = "The Card you are adding or removing is currently not available!"):
        self.message = message
        super().__init__(self.message)


class UnrecognizedCardError(Exception):
    """Card being added or removed is not recognized in the Deck"""

    def __init__(self, message: str = "Unknown Card is being added/removed!"):
        self.message = message
        super().__init__(self.message)


class DealerUnassignedError(Exception):
    """Dealer not assigned to the Deck"""

    def __init__(self, message: str = "Dealer has not been assigned to this Deck"):
        self.message = message
        super().__init__(self.message)

class GameUnassignedError(Exception):
    """Game not assigned to the Dealer"""

    def __init__(self, message: str = "Game has not been assigned to this Dealer!"):
        self.message = message
        super().__init__(self.message)

class GameAssignmentPermissionError(Exception):
    def __init__(self, message: str = "Cannot assign Game for this Dealer with the current permission. Must be done within Game object"):
        self.message = message
        super().__init__(self.message)


class RuleViolationError(Exception):
    def __init__(self, message: str = "Rule of the game is violated!"):
        self.message = message
        super().__init__(self.message)

class RuleIllFormedError(Exception):
    def __init__(self, message: str = "Particular object i nthe Rule is IllFormed!"):
        self.message = message
        super().__init__(self.message)

class DealerError(Exception):
    def __init__(self, message: str = "Ooops! Something werid happened while dealing"):
        self.message = message
        super().__init__(self.message)
