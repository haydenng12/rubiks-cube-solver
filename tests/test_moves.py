import sys
import os

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cube import create_solved_cube, cube_to_string
from moves import apply_move

@pytest.mark.parametrize("move", ["R", "L", "U", "D", "F", "B"])
def test_inverse_move(move):
    cube = create_solved_cube()
    original = cube_to_string(cube)

    cube = apply_move(cube, move)
    cube = apply_move(cube, move + "'")

    assert cube_to_string(cube) == original

@pytest.mark.parametrize("move", ["R", "L", "U", "D", "F", "B"])
def test_double_move(move):
    cube = create_solved_cube()
    original = cube_to_string(cube)

    cube = apply_move(cube, move + "2")
    cube = apply_move(cube, move + "2")

    assert cube_to_string(cube) == original


def main():
    moves = ["R", "L", "U", "D", "F", "B"]

    for move in moves:
        test_inverse_move(move)
        test_double_move(move)


if __name__ == "__main__":
    main()