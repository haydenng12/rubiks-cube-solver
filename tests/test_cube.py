import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cube import create_solved_cube, cube_to_string, is_solved


def test_create_solved_cube_is_solved():
    cube = create_solved_cube()
    assert is_solved(cube)


def test_cube_to_string_order_for_solved_cube():
    cube = create_solved_cube()
    assert cube_to_string(cube) == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"