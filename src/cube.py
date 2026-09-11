def create_solved_cube():
    return {
        "U": ["U"] * 9,
        "R": ["R"] * 9,
        "F": ["F"] * 9,
        "D": ["D"] * 9,
        "L": ["L"] * 9,
        "B": ["B"] * 9,
    }


def cube_to_string(cube):
    order = ["U", "R", "F", "D", "L", "B"]

    cube_string = ""

    for face in order:
        cube_string += "".join(cube[face])

    return cube_string

def is_solved(cube):
    expected = create_solved_cube()
    return set(cube) == set(expected) and all(cube[face] == expected[face] for face in expected)
