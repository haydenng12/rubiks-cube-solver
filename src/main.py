from cube import cube_to_string
from validation import is_valid_cube_string
from solver import solve_cube
from playback import play_solution
from input_handler import get_manual_cube, choose_input_mode


def main():
    mode = choose_input_mode()

    if mode == "manual":
        cube = get_manual_cube();
    else:
        print("Camera input mode is not implemented yet. Please use manual input.")
        return
    
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