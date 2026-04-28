def print_face_row(face, row):
    start = row * 3
    return f"{face[start]} {face[start + 1]} {face[start + 2]}"


def print_cube_2d(cube):
    # U face
    print("        " + print_face_row(cube["U"], 0))
    print("        " + print_face_row(cube["U"], 1))
    print("        " + print_face_row(cube["U"], 2))

    print()

    # L, F, R, B faces
    for row in range(3):
        left = print_face_row(cube["L"], row)
        front = print_face_row(cube["F"], row)
        right = print_face_row(cube["R"], row)
        back = print_face_row(cube["B"], row)

        print(f"{left}   {front}   {right}   {back}")

    print()

    # D face
    print("        " + print_face_row(cube["D"], 0))
    print("        " + print_face_row(cube["D"], 1))
    print("        " + print_face_row(cube["D"], 2))