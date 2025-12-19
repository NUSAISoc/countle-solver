import argparse
from solver import AStarSolver, BFSSolver, GreedySolver, RandomSolver

from game.game import CountleGame

STRATEGY_TO_SOLVER = {
    'greedy': GreedySolver,
    'random': RandomSolver,
    'astar': AStarSolver,
    'bfs': BFSSolver,
}

def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description = "Countle Solver"
    )

    parser.add_argument(
        '--mode', 
        choices = ['interactive', 'demo', 'solve'], 
        default = 'interactive',
        help = 'Game mode (default: interactive)'
    )

    parser.add_argument(
        '--strategy', 
        choices = STRATEGY_TO_SOLVER.keys(), 
        default = 'greedy',
        help = 'Solving strategy for demo and solve mode (default: greedy)'
    )
    assert 'greedy' in STRATEGY_TO_SOLVER, "Default strategy must be in STRATEGY_TO_SOLVER"

    parser.add_argument(
        '--seed', 
        type = int, 
        default = None,
        help = 'Random seed for reproducibility'
    )

    parser.add_argument(
        '--numbers', 
        type = int, 
        default = 6,
        help = 'Number of starting numbers (default: 6)'
    )

    parser.add_argument(
        '--max-number', 
        type = int, 
        default = 20,
        help = 'Maximum value for starting numbers (default: 20)'
    )

    parser.add_argument(
        '--min-moves', 
        type = int, 
        default = 3,
        help = 'Minimum number of moves to reach the target (default: 3)'
    )
    
    return parser

def play_interactive(game: CountleGame):
    print("Welcome to Countle!")
    print("Type 'help' for a list of commands.")
    while True:
        print("\nCurrent Numbers:", game.current_numbers)
        print("Target:", game.current_target)
        user_input = input("Enter your command: ").strip().lower()
        
        if user_input == 'help':
            print("Available commands:")
            print("  move <num1> <op> <num2> - Apply operation (op) between num1 and num2")
            print("  undo - Undo the last move")
            print("  reset - Reset the game to initial state")
            print("  solve [strategy] - Solve the game using specified strategy (default: greedy)")
            print("  exit - Exit the game")
        elif user_input.startswith('move'):
            parts = user_input.split()
            if len(parts) != 4:
                print("Invalid move command. Usage: move <num1> <op> <num2>")
                continue
            try:
                num1 = int(parts[1])
                op = parts[2]
                num2 = int(parts[3])
                move = (num1, op, num2)
                game.apply_move(move)
                if game.won:
                    print("Congratulations! You've reached the target!")
                    break
            except Exception as e:
                print(f"Error applying move: {e}")
        elif user_input == 'undo':
            try:
                game.undo_move()
            except Exception as e:
                print(f"Error undoing move: {e}")
        elif user_input == 'reset':
            game.reset_game()
        elif user_input.startswith('solve'):
            parts = user_input.split()
            strategy = parts[1] if len(parts) > 1 else 'greedy'
            
            solver_class = STRATEGY_TO_SOLVER.get(strategy, GreedySolver)
            solver = solver_class(game)
            solver.solve(game.current_state)
            
            if game.won:
                break
        elif user_input == 'exit':
            print("Exiting the game. Goodbye!")
            break
        else:
            print("Unknown command. Type 'help' for a list of commands.")

def play_demo(game: CountleGame, strategy: str):
    print(f"Giving demo using strategy: {strategy}")
    solver_class = STRATEGY_TO_SOLVER.get(strategy, GreedySolver)
    solver = solver_class(game)
    success, solution_path = solver.solve()
    
    if success:
        print("Solution found! Steps:")
        for i, state in enumerate(solution_path[1:]):
            print(
                f"Step {i + 1}: Numbers: {state.numbers}, "
                f"Target: {state.target}, "
                f"Move: {state.move_description}"
            )
    else:
        print("Failed to find a solution.")

def play_solve(game: CountleGame, strategy: str):
    # TODO: Would be funny if we can actually connect to countle.org and solve it.

    print(f"Solving using strategy: {strategy}")

    # Lowkey breaking abstraction, but oh well.
    initial_state = game.engine._internal_state
    
    solver_class = STRATEGY_TO_SOLVER.get(strategy, GreedySolver)
    solver = solver_class(game)
    success, solution_path = solver.solve(initial_state)
    
    if success:
        print("Solution found! Steps:")
        for i, state in enumerate(solution_path[1:]):
            print(
                f"Step {i + 1}: Numbers: {state.numbers}, "
                f"Target: {state.target}, "
                f"Move: {state.move_description}"
            )
    else:
        print("Failed to find a solution.")
    

def main():
    parser = get_argparser()
    args = parser.parse_args()

    game = CountleGame(
        engine_kwargs = {
            'num_numbers': args.numbers,
            'max_number': args.max_number,
            'min_moves': args.min_moves,
            'seed': args.seed
        }
    )
    if args.mode == 'interactive':
        play_interactive(game)
    elif args.mode == 'demo':
        play_demo(game, args.strategy)
    elif args.mode == 'solve':
            initialization = input(
                "Enter n+1 numbers (n numbers, 1 target) separated by spaces " 
                "to begin (e.g. 1 2 3 4 5 6 means 6 is the target): "
            ).strip()

            all_numbers = list(map(int, initialization.split()))
            assert len(all_numbers) >= 3, "At least three numbers (two initial numbers, one target) are required."
            game.make_from_numbers_and_target(
                numbers = all_numbers[:-1],
                target = all_numbers[-1]
            )
            play_solve(game, args.strategy)

    

if __name__ == "__main__":
    main()