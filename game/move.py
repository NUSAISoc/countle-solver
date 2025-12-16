from dataclasses import dataclass
from game.types import MoveType, Operation

@dataclass(frozen=True)
class GameMove:
    move_type: MoveType
    op1: int = None
    op2: int = None
    operation: Operation = None
    
    def __str__(self):
        if self.move_type == MoveType.OPERATION:
            return f"{self.op1} {self.operation.symbol} {self.op2}"
        elif self.move_type == MoveType.ROLLBACK:
            return f"Rollback step {self.op1}"
        return "Unknown Move"
    