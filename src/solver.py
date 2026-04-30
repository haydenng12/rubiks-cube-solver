import kociemba

SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


def solve_cube(cube_string):
    if cube_string == SOLVED_CUBE:
        return ""
    try:
        return kociemba.solve(cube_string)
    except Exception as exc:
        raise ValueError(f"Cube state is not physically solvable: {exc}") from exc
