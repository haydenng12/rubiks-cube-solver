import kociemba

SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


def solve_cube(cube_string):
    if cube_string == SOLVED_CUBE:
        return ""

    return kociemba.solve(cube_string)