from collections import deque
from typing import List, Tuple, Dict, Optional

from game.state import GameState
from game.types import MoveType
from game.engine import CountleEngine
from solver.base import BaseSolver

class BFSSolver(BaseSolver):
    '''
    Uses Breadth-First Search to solve the Countle game.

    Tantamount to bruteforcing, but BFS guarantees the shortest path solution.
    '''
    def __init__(
        self, 
        game: CountleEngine, 
        *args, 
        **kwargs
    ):
        super().__init__(
            game, 
            *args, 
            **kwargs
        )
        self.game = game

    def solve(
        self, 
        initial_state: GameState = None
    ) -> Tuple[bool, List[GameState]]:
        
        if initial_state is None:
            # Generate a new level if no state provided
            print("No initial state provided, generating a new level.")
            initial_state = self.game.reset()
        
        target = initial_state.target
        start_numbers = tuple(sorted(initial_state.numbers))
        
        # Deque: (Cost, State)
        queue = deque([(0, initial_state)])
        
        # came_from: current_numbers -> (parent_numbers, move_description)
        came_from: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {
            start_numbers: (None, None)
        }
        
        solution_found = False
        final_numbers = None
        
        while queue:
            cost, current_state = queue.popleft()
            
            # Check if target is reached
            if target in current_state.numbers:
                solution_found = True
                final_numbers = tuple(sorted(current_state.numbers))
                break

            # Else check if we went too far.
            if len(current_state.numbers) == 1:
                continue
            
            # Generate neighbors
            valid_moves = self.game.get_valid_moves(
                current_state
            )
            for move in valid_moves:
                # We don't actually need to rollback if we are doing BFS.
                # If the path is unsuccessful, we just discard it.
                if move.move_type != MoveType.OPERATION:
                    continue
                
                result = move.operation.apply(move.op1, move.op2)
                new_numbers = current_state.numbers.copy()
                new_numbers.remove(move.op1)
                new_numbers.remove(move.op2)
                new_numbers.append(result)
                new_numbers_tuple = tuple(sorted(new_numbers))
                
                if new_numbers_tuple not in came_from:
                    came_from[new_numbers_tuple] = (
                        tuple(sorted(current_state.numbers)), 
                        f"{move} = {result}"
                    )
                    new_state = GameState(
                        numbers=new_numbers, 
                        move_history=(current_state.move_history or []) + [new_numbers],
                        target=target
                    )
                    queue.append((cost + 1, new_state))
        
        if solution_found:
            # Reconstruct path
            path = []
            curr = final_numbers
            while curr != start_numbers:
                print(f"Reconstructing step: {curr}")
                parent, move_desc = came_from[curr]
                state = GameState(
                    numbers=list(curr), 
                    move_description=move_desc, 
                    target=target
                )
                path.append(state)
                curr = parent
            
            # Add initial state
            path.append(initial_state)
            path.reverse()
            return True, path
        else:
            print(f"No solution found using BFS. State: {initial_state}, Target: {target}")
            return False, None
