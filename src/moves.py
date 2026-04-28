def copy_cube(cube):
    return {
        face: stickers.copy()
        for face, stickers in cube.items()
    }


def rotate_face_clockwise(face):
    return [
        face[6], face[3], face[0],
        face[7], face[4], face[1],
        face[8], face[5], face[2],
    ]


def rotate_face_counterclockwise(face):
    return [
        face[2], face[5], face[8],
        face[1], face[4], face[7],
        face[0], face[3], face[6],
    ]


def rotate_face_180(face):
    return [
        face[8], face[7], face[6],
        face[5], face[4], face[3],
        face[2], face[1], face[0],
    ]

def repeat_move(cube, move_function, times):
    for _ in range(times):
        cube = move_function(cube)
    return cube

def apply_R(cube):
    new_cube = copy_cube(cube)

    new_cube["R"] = rotate_face_clockwise(cube["R"])

    new_cube["U"][2] = cube["F"][2]
    new_cube["U"][5] = cube["F"][5]
    new_cube["U"][8] = cube["F"][8]

    new_cube["F"][2] = cube["D"][2]
    new_cube["F"][5] = cube["D"][5]
    new_cube["F"][8] = cube["D"][8]

    new_cube["D"][2] = cube["B"][6]
    new_cube["D"][5] = cube["B"][3]
    new_cube["D"][8] = cube["B"][0]

    new_cube["B"][6] = cube["U"][2]
    new_cube["B"][3] = cube["U"][5]
    new_cube["B"][0] = cube["U"][8]

    return new_cube

def apply_L(cube):
    new_cube = copy_cube(cube)

    new_cube["L"] = rotate_face_clockwise(cube["L"])

    new_cube["U"][0] = cube["B"][8]
    new_cube["U"][3] = cube["B"][5]
    new_cube["U"][6] = cube["B"][2]

    new_cube["F"][0] = cube["U"][0]
    new_cube["F"][3] = cube["U"][3]
    new_cube["F"][6] = cube["U"][6]

    new_cube["D"][0] = cube["F"][0]
    new_cube["D"][3] = cube["F"][3]
    new_cube["D"][6] = cube["F"][6]

    new_cube["B"][8] = cube["D"][0]
    new_cube["B"][5] = cube["D"][3]
    new_cube["B"][2] = cube["D"][6]

    return new_cube

def apply_U(cube):
    new_cube = copy_cube(cube)

    new_cube["U"] = rotate_face_clockwise(cube["U"])

    new_cube["F"][0:3] = cube["R"][0:3]
    new_cube["R"][0:3] = cube["B"][0:3]
    new_cube["B"][0:3] = cube["L"][0:3]
    new_cube["L"][0:3] = cube["F"][0:3]

    return new_cube

def apply_D(cube):
    new_cube = copy_cube(cube)

    new_cube["D"] = rotate_face_clockwise(cube["D"])

    new_cube["F"][6:9] = cube["L"][6:9]
    new_cube["L"][6:9] = cube["B"][6:9]
    new_cube["B"][6:9] = cube["R"][6:9]
    new_cube["R"][6:9] = cube["F"][6:9]

    return new_cube

def apply_F(cube):
    new_cube = copy_cube(cube)

    new_cube["F"] = rotate_face_clockwise(cube["F"])

    new_cube["U"][6] = cube["L"][8]
    new_cube["U"][7] = cube["L"][5]
    new_cube["U"][8] = cube["L"][2]

    new_cube["R"][0] = cube["U"][6]
    new_cube["R"][3] = cube["U"][7]
    new_cube["R"][6] = cube["U"][8]

    new_cube["D"][2] = cube["R"][0]
    new_cube["D"][1] = cube["R"][3]
    new_cube["D"][0] = cube["R"][6]

    new_cube["L"][8] = cube["D"][2]
    new_cube["L"][5] = cube["D"][1]
    new_cube["L"][2] = cube["D"][0]

    return new_cube

def apply_B(cube):
    new_cube = copy_cube(cube)

    new_cube["B"] = rotate_face_clockwise(cube["B"])

    new_cube["U"][0] = cube["R"][2]
    new_cube["U"][1] = cube["R"][5]
    new_cube["U"][2] = cube["R"][8]

    new_cube["L"][0] = cube["U"][2]
    new_cube["L"][3] = cube["U"][1]
    new_cube["L"][6] = cube["U"][0]

    new_cube["D"][8] = cube["L"][0]
    new_cube["D"][7] = cube["L"][3]
    new_cube["D"][6] = cube["L"][6]

    new_cube["R"][2] = cube["D"][8]
    new_cube["R"][5] = cube["D"][7]
    new_cube["R"][8] = cube["D"][6]

    return new_cube

BASE_MOVES = {
    "R": apply_R,
    "L": apply_L,
    "U": apply_U,
    "D": apply_D,
    "F": apply_F,
    "B": apply_B,
}


def apply_move(cube, move):
    base_move = move[0]

    if base_move not in BASE_MOVES:
        raise ValueError(f"Unsupported move: {move}")

    move_function = BASE_MOVES[base_move]

    if len(move) == 1:
        return move_function(cube)
    elif move[1] == "'":
        return repeat_move(cube, move_function, 3)
    elif move[1] == "2":
        return repeat_move(cube, move_function, 2)
    else:
        raise ValueError(f"Invalid move format: {move}")
    
def apply_sequence(cube, moves):
    for move in moves:
        cube = apply_move(cube, move)
    return cube

