def capture_face(face_name):
    while True:
        stickers = input(f"Enter {face_name} face: ").upper().strip()

        if len(stickers) != 9:
            print("Must be exactly 9 characters.")
            continue

        return list(stickers)


def get_manual_cube():
    cube = {}

    print("Enter each face as 9 letters.")
    print("Use only: U R F D L B")
    print("Example: UUUUUUUUU")

    for face in ["U", "R", "F", "D", "L", "B"]:
        cube[face] = capture_face(face)

    return cube