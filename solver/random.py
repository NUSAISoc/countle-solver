from typing import List, Tuple

from solver.base import BaseSolver
from game.state import GameState

class RandomSolver(BaseSolver):
    '''
    Select a random valid move at each step until the target is reached.
    Not really useful outside of debugging.
    '''
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.game = game
    
    def solve(self, initial_state: GameState = None) -> Tuple[bool, List[GameState]]:
        if initial_state is None:
            # Generate a new level if no state provided
            print("No initial state provided, generating a new level.")
            numbers, target = self.game.reset()
            initial_state = GameState(numbers=numbers, target=target)
        
        current_state = initial_state
        solution_path = [current_state]
        
        import random
        
        while current_state.target not in current_state.numbers:
            valid_moves = self.game.get_valid_moves(current_state)
            if not valid_moves:
                print("No valid moves left, failed to reach target.")
                return False, solution_path
            
            move = random.choice(valid_moves)
            current_state = self.game.apply_move(current_state, move)
            solution_path.append(current_state)
        
        return True, solution_path