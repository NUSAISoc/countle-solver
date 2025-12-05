from enum import Enum
from typing import Callable, Optional

class MoveType(Enum):
    """Type of move in the game."""
    OPERATION = "operation"
    ROLLBACK = "rollback"


class Operation(Enum):
    """Supported arithmetic operations."""
    ADD = ('+', int.__add__)
    SUBTRACT = ('-', lambda a, b: a - b if a >= b else None)
    MULTIPLY = ('*', int.__mul__)
    DIVIDE = ('/', lambda a, b: a // b if b != 0 and a % b == 0 else None)
    
    def __init__(self, symbol: str, func: Callable):
        self.symbol = symbol
        self.func = func
    
    @classmethod
    def from_symbol(cls, symbol: str) -> Optional['Operation']:
        for op in cls:
            if op.symbol == symbol:
                return op
        return None
    
    @classmethod
    def operation_regex(cls) -> str:
        return r'^(\d+)\s*([+\-*/])\s*(\d+)$'
    
    def apply(self, a: int, b: int) -> Optional[int]:
        return self.func(a, b)