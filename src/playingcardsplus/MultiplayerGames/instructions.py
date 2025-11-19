from abc import ABC
from typing_extensions import NamedTuple, Set


class Instruction(NamedTuple):
    operation: str

class InstructionSet(NamedTuple):
    instructions: Set[Instruction]

class InstructionSetImplementer(ABC):
    """Will be used to implement vairety of functions in the insturction set in each game"""
    def __init__(self, instruction_set:InstructionSet):
        self.__instruction_set = instruction_set

def validate_instruction_set(values: set) -> InstructionSet:
    if not isinstance(values, set):
        raise TypeError("Not a Set!")
    if any(not isinstance(v, Instruction) for v in values):
        raise ValueError("Only Instruction allowed")

    return InstructionSet(values)
