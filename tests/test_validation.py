import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from validation import is_valid_cube_string


SOLVED = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


def test_valid_cube_string():
    valid, _ = is_valid_cube_string(SOLVED)
    assert valid


def test_invalid_length():
    valid, message = is_valid_cube_string(SOLVED[:-1])
    assert not valid
    assert "54" in message


def test_invalid_character():
    broken = "X" + SOLVED[1:]
    valid, message = is_valid_cube_string(broken)
    assert not valid
    assert "Invalid character" in message


def test_invalid_face_count():
    broken = "U" * 10 + SOLVED[10:]
    valid, message = is_valid_cube_string(broken)
    assert not valid
    assert "should be 9" in message
