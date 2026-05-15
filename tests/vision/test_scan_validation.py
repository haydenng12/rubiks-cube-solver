import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from vision.scan_validation import validate_cube_state, validate_partial_scan


SOLVED_CUBE = {
    "U": ["U"] * 9,
    "R": ["R"] * 9,
    "F": ["F"] * 9,
    "D": ["D"] * 9,
    "L": ["L"] * 9,
    "B": ["B"] * 9,
}


def test_validate_partial_scan_u_f_r():
    partial = {"U": ["U"] * 9, "F": ["F"] * 9, "R": ["R"] * 9}
    result = validate_partial_scan(partial, ("U", "F", "R"))
    assert result.valid


def test_validate_cube_state_solved():
    result = validate_cube_state(SOLVED_CUBE)
    assert result.valid
