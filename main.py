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
        help = 'Solving strategy for solve mode (default: greedy)'
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

def play_demo(game: CountleGame):
    print("Starting demo mode with the default solver...")
    solver = GreedySolver(game)
    success, solution_path = solver.solve()
    
    if success:
        print("Demo completed successfully! Solution path:")
        for i, state in enumerate(solution_path):
            print(f"Step {i}: Numbers: {state.numbers}, Target: {state.target}, Move: {state.move_description}")
    else:
        print("Demo failed to find a solution.")

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
        play_demo(game)
    elif args.mode == 'solve':
        solver_class = STRATEGY_TO_SOLVER.get(args.strategy, GreedySolver)
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

if __name__ == "__main__":
    main()