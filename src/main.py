from cube import cube_to_string
from validation import is_valid_cube_string
from solver import solve_cube
from playback import play_solution
from input_handler import get_manual_cube, choose_input_mode


def main():
    mode = choose_input_mode()

    if mode == "manual":
        cube = get_manual_cube()
    else:
        from vision.guide_layout import STANDARD_FIRST_CORNER, STANDARD_SECOND_CORNER
        from vision.guided_preview import run_guided_preview
        from vision.reconstruction import reconstruct

        print("Capture 1: WHITE top, GREEN front-left, RED right.")
        first = run_guided_preview(profile=STANDARD_FIRST_CORNER)
        if first is None:
            print("Camera scan cancelled.")
            return
        print("Capture 2: YELLOW top, BLUE front-left, ORANGE right.")
        second = run_guided_preview(profile=STANDARD_SECOND_CORNER)
        if second is None:
            print("Camera scan cancelled.")
            return
        reconstruction = reconstruct(first.sampled_faces, second.sampled_faces)
        if not reconstruction.structurally_valid:
            print(f"Scan rejected: {reconstruction.validation_message}")
            return
        cube = reconstruction.cube
    
    cube_string = cube_to_string(cube)

    valid, message = is_valid_cube_string(cube_string)

    if not valid:
        print(f"Invalid cube: {message}")
        return
    try:
        solution = solve_cube(cube_string)
    except ValueError as exc:
        print(exc)
        return
    
    print(f"Solution: {solution}")
    play_solution(cube, solution)

if __name__ == "__main__":
    main()
