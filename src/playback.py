from moves import apply_move
from visualizer import print_cube_2d


def play_solution(cube, solution):
    moves = solution.split()

    if len(moves) == 0:
        print("Cube is already solved.")
        print_cube_2d(cube)
        return cube

    print("Starting cube:")
    print_cube_2d(cube)

    for i, move in enumerate(moves):
        input(f"Press Enter for step {i + 1}: {move}")

        cube = apply_move(cube, move)

        print(f"After move {i + 1}: {move}")
        print_cube_2d(cube)

    return cube