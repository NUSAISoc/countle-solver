import re
import random

from typing import List, Tuple, Optional

from game.state import GameState
from game.types import MoveType, Operation
from game.move import GameMove

class CountleEngine:
    '''
    Core engine for Countle game logic.

    Noting that all Countle numbers are non-negative integers,
    we include checks to ensure all results remain in this domain.

    The abstraction is probably not very good, but it will do for now.
    '''
    ROLLBACK_REGEX = r'^(?:rb|rollback)\s+(\d+)$'
    
    def __init__(self, 
        num_numbers: int, 
        min_moves: int, 
        max_number: int = 100, 
        seed: int = 42
    ):

        # Some validation
        assert num_numbers >= 2, "num_numbers must be at least 2"
        assert min_moves >= 0, "min_moves must be non-negative"
        assert max_number >= 1, "max_number must be at least 1"

        assert min_moves <= num_numbers - 1, "min_moves cannot exceed num_numbers - 1"
        self.n = num_numbers
        self.min_moves = min_moves
        self.max_number = max_number

        self.REWARDS = {
            'invalid': -1,
            'step': -1,
            'success': self.n,
            'terminate': 0,
        }
        self.total_reward = 0
        self.won = False
        self.move_count = 0

        self.seed = seed
        self.rng = random.Random(seed)
        
    @property
    def current_numbers(self) -> List[int]:
        """Get current available numbers."""
        return self._internal_state.numbers
    
    @property
    def target(self) -> int:
        """Get current target number."""
        return self._internal_state.target
    
    @property
    def is_terminal(self) -> bool:
        """Check if game is in terminal state."""
        return self.won or len(self.current_numbers) == 1
    
    def get_valid_moves(self, numbers: Optional[List[int]] = None) -> List[GameMove]:
        """
        Get all valid moves from current state.
        
        Args:
            numbers: Optional list of numbers to use. If None, uses current_numbers.
            
        Returns:
            List of GameMove tuples
        """
        if numbers is None:
            numbers = self.current_numbers
            
        # So long as move history is not empty, there are valid moves.
        valid_moves = [
            GameMove(MoveType.ROLLBACK, op1 = i)
            for i in range(1, self.n - len(numbers))
        ]
        
        # Try all pairs of numbers
        for i in range(len(numbers)):
            for j in range(len(numbers)):
                if i == j:
                    continue
                
                num1, num2 = numbers[i], numbers[j]
                
                # Try all operations
                for op in Operation:
                    result = op.apply(num1, num2)
                    # i.e. result is valid.
                    if result is not None:
                        valid_moves.append(
                            GameMove(
                                MoveType.OPERATION, 
                                op1 = num1, 
                                op2 = num2, 
                                operation = op
                            ),
                        )
        
        return valid_moves
    
    def execute_operation(self, num1: int, num2: int, op_symbol: str) -> Tuple[int, str]:
        """
        Execute an arithmetic operation.
        
        Args:
            num1: First operand (must be in current_numbers)
            num2: Second operand (must be in current_numbers)
            op_symbol: Operation symbol (+, -, *, /)
            
        Returns:
            (reward, message) tuple
        """
        if self.is_terminal:
            return self.REWARDS['terminate'], "Game is already over!"
        
        # Step 1: Validate operands
        try:
            idx1 = self.current_numbers.index(num1)
            # If num1 == num2, we need to find the second occurrence
            if num1 == num2:
                idx2 = self.current_numbers.index(num2, start = idx1 + 1)
            else:
                idx2 = self.current_numbers.index(num2)
        except ValueError:
             return (
                 self.REWARDS['invalid'], 
                 f"Operands {num1}, {num2} not available in {self.current_numbers}"
             )

        # Step 2: Lookup operation
        operation = Operation.from_symbol(op_symbol)
        if operation is None:
            return (
                self.REWARDS['invalid'],
                f"Invalid operation: {op_symbol}"
            )

        # Step 3: Validate and compute result
        result = operation.apply(num1, num2)
        
        if result is None:
            reward = self.REWARDS['invalid']
            if operation == Operation.SUBTRACT:
                message = f"Invalid: {num1} - {num2} would be negative"
            elif operation == Operation.DIVIDE:
                if num2 == 0:
                    message = f"Invalid: Cannot divide by zero"
                else:
                    message = f"Invalid: {num1} / {num2} is not a whole number"
            else:
                message = f"Invalid operation"
            return reward, message
        
        # Step 4: Update state
        reward = self.REWARDS['step']
        self.move_count += 1
        
        # Create new numbers list
        new_numbers = list(self.current_numbers)
        # Remove by index to handle duplicates correctly
        # Remove larger index first to avoid shifting
        if idx1 > idx2:
            new_numbers.pop(idx1)
            new_numbers.pop(idx2)
        else:
            new_numbers.pop(idx2)
            new_numbers.pop(idx1)
            
        new_numbers.append(result)
        
        # Create new state
        move_desc = f"{num1} {op_symbol} {num2} = {result}"
        new_state = GameState(
            numbers = new_numbers, 
            move_history = self.history + [move_desc],
            move_description = move_desc,
            target = self._internal_state.target,
        )
        self._internal_state = new_state
        self.history.append(new_state)
        
        # Check if won
        if result == self._internal_state.target:
            self.won = True
            reward += self.REWARDS['success']
            message = f"{move_desc} -> WON! (Reached {self._internal_state.target})"
        else:
            message = f"Valid Move: {move_desc}"
        
        self.total_reward += reward
        return reward, message
    
    def execute_rollback(self, step_index: int) -> Tuple[int, str]:
        """
        Rollback to a previous step.
        
        Args:
            step_index: Step index to rollback to (0-indexed)
                       Deletes all operations up to and INCLUDING this step
        
        Returns:
            (reward, message) tuple
        """

        # Step 1a: Step index validation
        if step_index < 0:
            return self.REWARDS['invalid'], "Invalid step index (must be >= 0)"
        
        if step_index > len(self.history) - 1:
            return self.REWARDS['invalid'], f"Invalid step index (max: {len(self.history) - 1})"
        
        # Step 1b: Calculate steps to delete
        steps_to_delete = len(self.history) - 1 - step_index
        
        # Step 2: Rollback
        self._internal_state = self.history[step_index]
        self.history = self.history[:step_index + 1]
        self.won = False  # Reset win state
        
        reward = self.REWARDS['step']
        self.total_reward += reward
        self.move_count += 1
        
        message = f"Rolled back {steps_to_delete} step(s) to step {step_index}"
        return reward, message
    
    def execute_move(self, move: GameMove) -> Tuple[int, str]:
        """
        Execute a parsed move.
        
        Args:
            move: (MoveType, data) tuple from parse_human_input or structured input
            
        Returns:
            (reward, message) tuple
        """

        # Step 1: Route action based on move type
        if move.move_type == MoveType.OPERATION:
            return self.execute_operation(
                move.op1, 
                move.op2, 
                move.operation.symbol
            )
        elif move.move_type == MoveType.ROLLBACK:
            return self.execute_rollback(move.op1)
        else:
            return self.REWARDS['invalid'], "Unknown move type"
    
    def get_state_summary(self) -> str:
        """Get a summary of current game state."""
        lines = [
            "----- Current Game State -----",
            f"Target: {self._internal_state.target}",
            f"Current numbers: {self._internal_state.numbers}",
            f"Moves made: {self.move_count}",
            f"Total reward: {self.total_reward}"
        ]
        
        if self.won:
            lines.append("Status: WON!")
        elif self.is_terminal:
            lines.append("Status: Game Over (no more moves)")
        
        return "\n".join(lines)
    
    def get_history_summary(self) -> str:
        """Get a summary of move history."""
        if len(self.history) == 1:
            return "No moves yet"
        
        lines = ["Move history:"]
        for i, state in enumerate(self.history[1:], 1):
            lines.append(f"  {i}. {state.move_description}")
        return "\n".join(lines)

    def generate_target(self, numbers, max_mc_steps = 1_000) -> int:
        '''
        To prevent cheesing and creating overly easy targets, we WANT TO generate
        the target by computing the "numerical closure" of the generated numbers
        under valid operations.

        However, that would require exponential time/space in the worst case to compute.
        So instead, we will sample the closure by performing Monte Carlo random walks
        through the space of reachable numbers.

        This way a solution is guaranteed, and it is increasingly unlikely
        that some trivial target is chosen as we increase the number of steps.
        '''
        current_numbers = numbers.copy()

        howtomake = {tuple(current_numbers): None}

        approx_closure = {n: 0 for n in current_numbers}
        for _ in range(max_mc_steps):
            temp_numbers = current_numbers.copy()
            
            for step in range(self.n - 1):
                valid_moves = self.get_valid_moves(temp_numbers)
                if not valid_moves:
                    break
                move = self.rng.choice(list(filter(lambda m: m.move_type == MoveType.OPERATION, valid_moves)))
                
                # Update current numbers
                result = move.operation.apply(move.op1, move.op2)
                assert result >= 0 and isinstance(result, int), "Generated invalid result in closure computation"
                old_numbers = temp_numbers.copy()
                temp_numbers.remove(move.op1)
                temp_numbers.remove(move.op2)
                temp_numbers.append(result)
                
                if tuple(temp_numbers) not in howtomake:
                    howtomake[tuple(temp_numbers)] = {}
                howtomake[tuple(temp_numbers)][str(move)] = tuple(old_numbers)
                
                # Track the result in the approx closure
                if result < approx_closure.get(result, float('inf')):
                    approx_closure[result] = step + 1  # Store the step count when first reached
        
        candidates = [num for num, step in approx_closure.items() if self.min_moves <= step < self.n]
        
        tgt = self.rng.choice(list(set(candidates) - set(numbers)))
        return tgt
    
    def generate_level(self) -> GameState:
        '''
        Generate a new level with random numbers and a target.
        
        Returns:
            (numbers, target) tuple
        '''
        numbers = [self.rng.randint(1, self.max_number) for _ in range(self.n)]
        target = self.generate_target(numbers)

        self._internal_state = GameState(
            numbers = numbers, 
            move_history = None, 
            target = target
        )

        return self._internal_state
    
    def reset_history(self):
        '''
        Reset the move history to the current internal state.
        '''
        self.history = [self._internal_state]

    '''

    INTERFACE 

    '''

    def load_state(self, state: GameState, total_reward: int = 0, move_count: int = 0):
        """Load a given game state into the engine."""
        self._internal_state = state
        self.won = (self._internal_state.numbers == [self._internal_state.target])
        self.total_reward = total_reward
        self.move_count = move_count
        self.reset_history()


    @classmethod
    def create_from_numbers_and_target(
        cls, 
        numbers: List[int], 
        target: int, 
        seed: int = 42
    ) -> 'CountleEngine':
        '''
        Create a CountleEngine instance from given numbers and target.
        '''
        engine = cls(
            num_numbers = len(numbers),
            min_moves = 0,  # min_moves is not relevant here
            max_number = max(numbers + [target]),
            seed = seed
        )
        state = GameState(
            numbers = numbers,
            move_history = None,
            target = target
        )
        engine.load_state(state)
        return engine
    
    @classmethod
    def create_from_state(cls, state: GameState, seed: int = 42) -> 'CountleEngine':
        '''
        Create a CountleEngine instance from a given GameState.
        '''
        engine = cls(
            num_numbers = len(state.numbers),
            min_moves = 0,  # min_moves is not relevant here
            max_number = max(state.numbers + [state.target]),
            seed = seed
        )
        engine.load_state(state)
        return engine

    
    def parse_human_input(self, input_str: str) -> Optional[Tuple[MoveType, Tuple]]:
        """
        Parse human input string into structured move.
        
        Formats:
        - Operation: "a op b" (e.g., "25 + 50")
        - Rollback: "rb x" or "rollback x" (e.g., "rb 2")
        
        Args:
            input_str: Human input string
            
        Returns:
            (MoveType, data) where data is:
                - For OPERATION: (num1, num2, op_symbol)
                - For ROLLBACK: (step_index,)
            Returns None if parsing fails
        """
        input_str = input_str.strip()
        
        # Check for rollback
        rb_match = re.match(self.ROLLBACK_REGEX, input_str, re.IGNORECASE)
        if rb_match:
            step = int(rb_match.group(1))
            return (MoveType.ROLLBACK, (step,))
        
        # Check for operation
        op_match = re.match(Operation.operation_regex(), input_str)
        if op_match:
            num1 = int(op_match.group(1))
            op_symbol = op_match.group(2)
            num2 = int(op_match.group(3))
            return (MoveType.OPERATION, (num1, num2, op_symbol))
        
        return None