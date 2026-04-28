# Rubik's Cube Solver

This project is an interactive Rubik's Cube solving assistant. It allows users to input a cube state, validate it, compute a solution, and step through the solution move-by-move with a visual representation of the cube. The long-term goal is to extend this into a full system that scans a real cube using a camera and animates the solution in 3D.

Although this is a modest project, I hope that eventually I can deploy it as a website, possibly with a speed-cubing ranked system where players can solve a unique virtual cube daily, like Wordle but for cubes. This would be one feature among many. That may be slightly complicated though, since kociemba, the solver library I'm using, is Python/C-based. I might have to migrate to a JS cube solver library, but this whole spiel can be for another day. Computer vision is probably as far as I'll go for this project for simplicity's sake.

---

## Features (as of 4/27)

* Cube representation and simulation engine
* Full move support (`R, L, U, D, F, B` + `'` and `2`)
* Validation of cube input
* Solver integration using Kociemba’s algorithm
* Step-by-step playback of solution
* 2D cube visualizer for debugging and understanding

---

## Planned Features

* Camera-based cube scanning (OpenCV)
* 3D animated solution playback
* Scramble generator
* Timer and practice mode (maybe)
* Move explanations / learning mode (maybe)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/haydenng12/rubiks-cube-solver.git
cd rubiks-cube-solver
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Microsoft C++ Build Tools (Windows only)

Required for installing the `kociemba` package.

Download:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

During installation, select:

* Desktop development with C++

---

## Usage

Run the main program:

```bash
python src/main.py
```

You will be prompted to enter each face of the cube manually.

Example input for a solved cube:

```
U: UUUUUUUUU
R: RRRRRRRRR
F: FFFFFFFFF
D: DDDDDDDDD
L: LLLLLLLLL
B: BBBBBBBBB
```

The program will:

1. Validate the cube
2. Compute a solution
3. Display the solution step-by-step
4. Show the cube state after each move

---

## Running Tests

From the project root:

```bash
python tests/test_moves.py
python tests/test_solver.py
```

These tests are rudimentary with few test cases but they are intended to verify:

* Move correctness (inverse and double moves)
* Solver correctness (solution returns cube to solved state)

---

## Technologies Used

* Python
* Kociemba algorithm (`kociemba` library)
* OpenCV (planned for computer vision)

---

## Future Direction

The ultimate goal is to build a system that:

* Scans a real cube using a camera
* Automatically detects colors
* Computes an optimal solution
* Animates the solution in an interactive 3D interface

```
```
