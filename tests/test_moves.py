import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cube import create_solved_cube, cube_to_string
from moves import apply_move


def test_inverse_move(move):
    cube = create_solved_cube()
    original = cube_to_string(cube)

    cube = apply_move(cube, move)
    cube = apply_move(cube, move + "'")

    result = cube_to_string(cube)

    if result == original:
        print(f"PASS: {move} followed by {move}' returns to original")
    else:
        print(f"FAIL: {move} followed by {move}' did not return to original")
        print("Expected:", original)
        print("Got:     ", result)


def test_double_move(move):
    cube = create_solved_cube()
    original = cube_to_string(cube)

    cube = apply_move(cube, move + "2")
    cube = apply_move(cube, move + "2")

    result = cube_to_string(cube)

    if result == original:
        print(f"PASS: {move}2 followed by {move}2 returns to original")
    else:
        print(f"FAIL: {move}2 followed by {move}2 did not return to original")
        print("Expected:", original)
        print("Got:     ", result)


def main():
    moves = ["R", "L", "U", "D", "F", "B"]

    for move in moves:
        test_inverse_move(move)
        test_double_move(move)


if __name__ == "__main__":
    main()