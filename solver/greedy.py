from typing import List, Tuple

from solver.base import BaseSolver
from game.state import GameState
from game.types import MoveType

class GreedySolver(BaseSolver):
    '''
    A simple greedy solver that selects the move which gets closest to the target at each step.

    This obviously sucks as a solver, but is still nontrivial and 
    illustrates how to extend the BaseSolver class.
    '''
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.game = game
    
    def solve(self, initial_state: GameState = None) -> Tuple[bool, List[GameState]]:
        if initial_state is None:
            # Generate a new level if no state provided
            print("No initial state provided, generating a new level.")
            initial_state = self.game.reset()
        
        current_state = initial_state
        solution_path = [current_state]
        
        while current_state.target not in current_state.numbers:
            valid_moves = self.game.get_valid_moves(current_state)
            if not valid_moves:
                print("No valid moves left, failed to reach target.")
                return False, solution_path
            
            # Select the operation that gets closest to the target
            best_move = None
            best_distance = float('inf')
            for move in valid_moves:
                if not move.move_type == MoveType.OPERATION:
                    continue
                result = move.operation.apply(move.op1, move.op2)
                new_state = current_state.numbers.copy()
                new_state.remove(move.op1)
                new_state.remove(move.op2)
                new_state.append(result)
                distance = abs(current_state.target - result)
                if distance < best_distance:
                    best_distance = distance
                    best_move = move
            
            if best_move is None:
                print("No valid operation moves found, failed to reach target.")
                return False, None
            
            # current_state = self.game.apply_move(current_state, best_move)
            current_state, _, _, _, _ = self.game.step(best_move)
            solution_path.append(current_state)
            print(f"Applied move: {best_move}, New numbers: {current_state.numbers}")
        
        return True, solution_path