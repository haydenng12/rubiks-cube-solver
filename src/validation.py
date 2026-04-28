def is_valid_cube_string(cube_string):
    if len(cube_string) != 54:
        return False, "Cube must have exactly 54 characters"

    valid_chars = set("UDFBLR")

    for c in cube_string:
        if c not in valid_chars:
            return False, f"Invalid character found: {c}"

    counts = {face: cube_string.count(face) for face in valid_chars}

    for face, count in counts.items():
        if count != 9:
            return False, f"{face} appears {count} times (should be 9)"

    return True, "Cube is valid"