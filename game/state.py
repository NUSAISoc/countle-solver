from dataclasses import dataclass
from typing import Optional, List, Tuple

from game.types import MoveType

@dataclass
class GameState:
    """Represents a single state in the game."""
    numbers: List[int]
    move_history: Optional[List[Tuple[MoveType, List[int]]]] = None
    target: int = 0
    move_description: Optional[str] = None
