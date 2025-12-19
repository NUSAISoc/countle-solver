# Abstract class for Countle solvers

from abc import ABC, abstractmethod
from typing import List, Tuple
from game.state import GameState

class BaseSolver(ABC):
    def __init__(self, game, *args, **kwargs):
        pass

    @abstractmethod
    def solve(self, initial_state: GameState = None) -> Tuple[List[GameState], bool]:
        """
        Solve the Countle game.

        Returns:
            A tuple containing:
            - Boolean indicating whether the solution was successful.
            - If successful, a list of GameState instances representing the solution path.
            - If unsuccessful, None.
        """
        pass