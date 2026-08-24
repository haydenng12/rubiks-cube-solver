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

## Camera Vision Diagnostic

The computer-vision pipeline can be tested through sticker detection, face grouping, and 3 x 3 geometry recovery before color classification is implemented.

From the repository root, run:

```bash
python -m src.vision.diagnostic_preview
```

Hold the cube so three complete faces are visible. Yellow outlines are raw sticker candidates. When exactly 27 candidates form three valid grids, each face receives a different color and its stickers are numbered from `0` to `8` in row-major order.

Controls:

* `SPACE`: freeze or resume the current frame
* `Q` or `ESC`: close the preview

If camera index `0` is not the webcam you want, use `--camera 1` (or another index). Use `--no-mirror` to display the unmirrored camera frame.

This is a diagnostic tool, not yet a complete camera-to-solver flow. It does not classify colors, label faces, combine opposite-corner scans, or solve the scanned cube.

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
