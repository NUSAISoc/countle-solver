from game.state import GameState
from game.engine import CountleEngine
from typing import List

# Wraps the Engine with a quasi-gymnasium interface
# Quasi, because it would be a massive pain to create a spec for the environment
# and that isn't an important detail for this project anyway.
class CountleGame:
    def __init__(self, engine_kwargs = None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self.engine_kwargs = engine_kwargs
        self.engine = CountleEngine(**self.engine_kwargs)
    
    def reset(self):
        self.engine.generate_level()
        self.engine.reset_history()
        return self.engine._internal_state

    def step(self, move):

        reward, message = self.engine.execute_move(move)
        terminated = self.engine.is_terminal
        truncated = False  # Not used in this context
        info = {
            "message": message,
            "current_numbers": self.engine.current_numbers,
            "target": self.engine.target
        }

        return self.engine._internal_state, reward, terminated, truncated, info

    def get_valid_moves(self, game_state: GameState):
        return self.engine.get_valid_moves(game_state.numbers)
    
    def make_from_numbers_and_target(self, numbers: List[int], target: int):
        self.engine = CountleEngine.create_from_numbers_and_target(
            numbers, 
            target,
        )
        return self.engine._internal_state