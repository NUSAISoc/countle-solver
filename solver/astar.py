# Solver using A* search algorithm for Countle game
from typing import List, Tuple, Dict, Optional
import heapq

from game.state import GameState
from game.types import Operation
from game.engine import CountleEngine
from solver.base import BaseSolver

class AStarSolver(BaseSolver):
    def __init__(self, game: CountleEngine, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.game = game

    def heuristic(self, numbers: Tuple[int, ...], target: int) -> int:
        # Placing the trivial heuristic here for now.
        return 0

    def solve(self, initial_state: GameState = None) -> Tuple[bool, List[GameState]]:
        if initial_state is None:
            # Generate a new level if no state provided
            print("No initial state provided, generating a new level.")
            numbers, target = self.game.generate_level()
            initial_state = GameState(numbers=numbers, target=target)
        
        target = initial_state.target
        start_numbers = tuple(sorted(initial_state.numbers))
        
        # Priority queue: (f_score, g_score, numbers)
        pq = [(0, 0, start_numbers)]
        
        # came_from: current_numbers -> (parent_numbers, move_description)
        came_from: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {
            start_numbers: (None, None)
        }
        
        g_score: Dict[Tuple[int, ...], int] = {start_numbers: 0}
        
        solution_found = False
        final_numbers = None
        
        while pq:
            f, g, current = heapq.heappop(pq)
            
            # Check if target is reached
            if target in current:
                solution_found = True
                final_numbers = current
                break
            
            # If we found a path longer than current best known to this node, skip
            if g > g_score.get(current, float('inf')):
                continue
            
            # Generate neighbors
            current_list = list(current)
            for i in range(len(current_list)):
                for j in range(len(current_list)):
                    if i == j:
                        continue
                    
                    num1 = current_list[i]
                    num2 = current_list[j]
                    
                    # Try all operations
                    for op in Operation:
                        # Pruning/Optimization:
                        # 1. + and * are commutative.
                        if op in [Operation.ADD, Operation.MULTIPLY] and i > j:
                            continue
                            
                        result = op.apply(num1, num2)
                        
                        if result is not None:
                            # Create new numbers tuple
                            # Remove num1 and num2, add result, sort
                            new_nums_list = []
                            for k, n in enumerate(current_list):
                                if k != i and k != j:
                                    new_nums_list.append(n)
                            new_nums_list.append(result)
                            new_nums = tuple(sorted(new_nums_list))
                            
                            tentative_g = g + 1
                            
                            if tentative_g < g_score.get(new_nums, float('inf')):
                                came_from[new_nums] = (current, f"{num1} {op.symbol} {num2} = {result}")
                                g_score[new_nums] = tentative_g
                                # Heuristic: 0 for Dijkstra (guarantees shortest path)
                                f_score = tentative_g 
                                heapq.heappush(pq, (f_score, tentative_g, new_nums))
        
        if solution_found:
            # Reconstruct path
            path = []
            curr = final_numbers
            while curr != start_numbers:
                parent, move_desc = came_from[curr]
                state = GameState(numbers=list(curr), move_description=move_desc, target=target)
                path.append(state)
                curr = parent
            
            # Add initial state
            path.append(initial_state)
            path.reverse()
            return True, path
        else:
            return False, []
