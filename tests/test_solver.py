import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cube import create_solved_cube, cube_to_string, is_solved
from solver import solve_cube
from moves import apply_sequence


def test_solver_solves_known_scramble():
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

    assert is_solved(cube)


def test_solved_cube_needs_no_moves():
    assert solve_cube(cube_to_string(create_solved_cube())) == ""


if __name__ == "__main__":
    test_solver_solves_known_scramble()
