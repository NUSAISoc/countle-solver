from game.state import GameState
from game.engine import CountleEngine

# Wraps the Engine with a quasi-gymnasium interface
class CountleGame:
    def __init__(self, engine_kwargs = None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self.engine = CountleEngine(**engine_kwargs)
    
    def reset(self):
        self.engine.generate_level()
        self.engine.reset_history()
        return self.engine._internal_state

    def step(self, move):
        # print(f"Before: {self.engine._internal_state}")

        reward, message = self.engine.execute_move(move)
        terminated = self.engine.is_terminal
        truncated = False  # Not used in this context
        info = {
            "message": message,
            "current_numbers": self.engine.current_numbers,
            "target": self.engine.target
        }

        print(info)

        return self.engine._internal_state, reward, terminated, truncated, info

    def get_valid_moves(self, game_state: GameState):
        return self.engine.get_valid_moves(game_state.numbers)