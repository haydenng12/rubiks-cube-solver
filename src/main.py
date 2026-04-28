from cube import cube_to_string
from validation import is_valid_cube_string
from solver import solve_cube
from playback import play_solution
from input_handler import get_manual_cube


def main():
    cube = get_manual_cube()
    cube_string = cube_to_string(cube)

    valid, message = is_valid_cube_string(cube_string)

    if not valid:
        print("Invalid cube:", message)
        return

    solution = solve_cube(cube_string)

    print("Solution:", solution)
    play_solution(cube, solution)


if __name__ == "__main__":
    main()