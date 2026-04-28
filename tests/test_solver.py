import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cube import create_solved_cube, cube_to_string, is_solved
from solver import solve_cube
from moves import apply_sequence


def main():
    cube = create_solved_cube()

    scramble = ["R", "U", "R'", "U'"]

    cube = apply_sequence(cube, scramble)

    scrambled_string = cube_to_string(cube)
    print("Scrambled cube:")
    print(scrambled_string)

    solution = solve_cube(scrambled_string)
    print("Solution:")
    print(solution)

    cube = apply_sequence(cube, solution.split())

    if is_solved(cube):
        print("PASS: Solver solution returned cube to solved state")
    else:
        print("FAIL: Solver solution did not return cube to solved state")
        print("Final cube:")
        print(cube_to_string(cube))


if __name__ == "__main__":
    main()