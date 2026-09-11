FACE_ORDER = "URFDLB"


def validate_cube_string(cube_string, check_solvable=False):
    if len(cube_string) != 54:
        return False, "Cube must have exactly 54 characters"

    valid_chars = set(FACE_ORDER)

    for c in cube_string:
        if c not in valid_chars:
            return False, f"Invalid character found: {c}"

    counts = {face: cube_string.count(face) for face in valid_chars}

    for face, count in counts.items():
        if count != 9:
            return False, f"{face} appears {count} times (should be 9)"

    for index, face in zip((4, 13, 22, 31, 40, 49), FACE_ORDER):
        if cube_string[index] != face:
            return False, f"Center at index {index} must be {face}"

    if check_solvable:
        try:
            import kociemba
            if cube_string != "".join(face * 9 for face in FACE_ORDER):
                kociemba.solve(cube_string)
        except ValueError as exc:
            return False, f"Cube is structurally valid but physically impossible: {exc}"

    return True, "Cube is structurally valid" if not check_solvable else "Cube is physically solvable"


def is_valid_cube_string(cube_string):
    """Backward-compatible structural validation API."""
    return validate_cube_string(cube_string, check_solvable=False)
