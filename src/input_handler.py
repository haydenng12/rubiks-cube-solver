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

def choose_input_mode():
    print("\nChoose input mode:")
    print("1. Manual input")
    print("2. Camera scan (coming soon)")
    choice = input("Select 1 or 2: ").strip()

    if choice == "1":
        return "manual"
    if choice == "2":
        return "camera"
    
    print("Invalid selection. Please enter 1 or 2.")