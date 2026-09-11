# Implementation and Software Engineering Guide

## 1. Project purpose

This project converts two webcam observations of a physical 3x3 Rubik's Cube
into the exact 54-sticker state required by a cube solver. Kociemba already
solves a correctly encoded state; the engineering challenge is producing that
state reliably from imperfect camera images.

The end-to-end pipeline is:

1. acquire two guided camera views;
2. normalize the perspective of the three visible faces in each view;
3. sample robust color measurements from 54 sticker interiors;
4. calibrate six color prototypes from the six fixed center stickers;
5. assign a face label to every sticker;
6. rotate and fuse observed faces into canonical solver coordinates;
7. validate the reconstructed cube;
8. solve it with Kociemba and play back the moves.

The software also saves a clean boundary between live scanning and offline
experimentation. Classification methods can be rerun on saved observations
without reopening the camera, which is essential for fair comparisons.

## 2. System architecture

### 2.1 Core cube domain

The original non-vision modules form the trusted domain layer:

- `cube.py` creates and serializes cube states.
- `moves.py` applies legal face turns.
- `validation.py` checks state syntax, counts, centers, and optionally physical
  solvability.
- `solver.py` adapts the Kociemba library.
- `playback.py` applies and displays a returned solution.
- `visualizer.py` renders a terminal cube net.
- `main.py` selects manual or camera input and connects it to validation and
  solving.

This layer is intentionally independent of OpenCV. A camera scanner should be
treated as another input adapter, not as a second cube implementation.

### 2.2 Vision acquisition and geometry

- `vision/camera.py` owns camera opening, frame reads, and cleanup.
- `vision/guide_layout.py` generates resolution-independent quadrilateral
  guides for `U/F/R` and `D/B/L` views.
- `vision/guided_overlay.py` displays alignment and capture feedback.
- `vision/guided_preview.py` controls live, review, rescan, and accept states.
- `vision/warp_sampling.py` transforms each quadrilateral into a canonical
  square and samples the nine sticker interiors.
- `vision/alignment.py` scores grid contrast and sticker uniformity.
- `vision/temporal.py` measures frame quality and aggregates repeated samples.

The guided method deliberately trades a small amount of user effort for a
strong geometric prior. It does not need to discover an arbitrary cube pose
from scratch.

### 2.3 Automatic localization baseline

- `vision/sticker_detector.py` detects quadrilateral contour candidates.
- `vision/face_grouping.py` divides candidate centers into three spatial groups.
- `vision/face_geometry.py` estimates a face boundary and orders its 3x3 cells.
- `vision/diagnostic_preview.py` visualizes intermediate detections.

This path is retained as an experimental baseline. Fixed edge thresholds,
strict candidate counts, and positional k-means introduce known sensitivity to
illumination, scale, and false detections. Retaining the baseline enables a
controlled comparison with guided and hybrid localization.

### 2.4 Classification and reconstruction

- `vision/color_model.py` converts BGR samples to Lab, computes prototype
  distances, and implements independent and balanced assignment.
- `vision/face_labeling.py` maps arbitrary color clusters through the centers.
- `vision/scan_fusion.py` applies explicit face rotations and combines views.
- `vision/reconstruction.py` orchestrates classification, fusion, and validation.
- `vision/two_view_preview.py` exposes the full interactive camera prototype.

### 2.5 Research infrastructure

- `vision/dataset.py` validates manifests and prevents train/test leakage.
- `vision/metrics.py` computes sticker, class-balanced, and exact-cube metrics.
- `vision/statistics.py` computes capture-session-aware bootstrap intervals.
- `vision/experiments.py` reruns methods on identical saved observations.
- `configs/experiment_matrix.yaml` records the planned methods and conditions.

## 3. Cube representation

A cube is represented as a mapping from the six canonical faces to nine
row-major stickers:

```python
{
    "U": ["U"] * 9,
    "R": ["R"] * 9,
    "F": ["F"] * 9,
    "D": ["D"] * 9,
    "L": ["L"] * 9,
    "B": ["B"] * 9,
}
```

Serialization uses Kociemba's `URFDLB` order. Each face has its own viewing
orientation. Therefore, recognizing the correct six colors is insufficient:
every observed face must also be rotated into its canonical row/column order.
`CaptureTransform` makes those rotations explicit and testable.

The center at index 4 is fixed on a physical 3x3 cube. Centers provide both:

- the identity of a face; and
- a session-specific sample of how that physical color appears under the
  current camera and lighting.

## 4. Guided two-view capture

### View 1

The user presents:

- white center on top (`U`);
- green center at front-left (`F`);
- red center at right (`R`).

### View 2

The user rotates to the opposite corner and presents:

- yellow center on top (`D`);
- blue center at front-left (`B`);
- orange center at right (`L`).

Together, the two views expose 54 sticker positions. The guides are placed in a
centered square viewport so widescreen camera resolutions do not stretch the
projected cube geometry.

The current protocol assumes the standard color scheme. Supporting arbitrary
schemes would require discovering opposite and adjacent center relationships
rather than hard-coding the capture instructions.

## 5. Perspective normalization

A face viewed obliquely appears as a quadrilateral. Sampling a regular image
grid directly would mix sticker interiors, borders, and neighboring faces.

For every visible face, OpenCV calculates a homography from the guide
quadrilateral to a square image. The square is divided into a 3x3 grid. Only a
central fraction of each cell is sampled, excluding dark borders and most edge
glare.

For source point `p`, a homography `H` produces normalized point `p'`:

```text
p' ~ H p
```

The equality is up to scale because homogeneous image coordinates are used.
The practical result is that downstream code always sees the same 3x3 layout
regardless of normal perspective distortion.

Median color is used instead of a single pixel or ordinary mean. A median is
less sensitive to isolated highlights, camera noise, and small border overlap.

## 6. Color representation and calibration

Camera frames arrive in BGR channel order. Raw channel values are convenient
for display but are not perceptually uniform: the same numerical distance can
represent very different perceived color differences.

The classifier converts samples to CIE Lab:

- `L` approximates lightness;
- `a` spans green to red;
- `b` spans blue to yellow.

For sticker vector `x` and center prototype `c_k`, the baseline cost for class
`k` is Euclidean distance:

```text
d(x, c_k) = sqrt((Lx-Lk)^2 + (ax-ak)^2 + (bx-bk)^2)
```

The prototypes come from the six center stickers in the same scanning session.
This adapts to the user's camera and current illumination without training a
personal machine-learning model.

## 7. Assignment strategies

### 7.1 Independent assignment

Each sticker selects its nearest prototype independently:

```text
predicted(x) = argmin_k d(x, c_k)
```

This is simple but can produce ten red stickers and eight orange stickers,
which is impossible for a standard cube.

### 7.2 Balanced assignment

A valid cube has exactly nine stickers of every color. The balanced method
creates 54 assignment slots—nine for each of six classes—and minimizes total
classification cost subject to every slot being filled once.

With SciPy installed, the Hungarian linear-assignment algorithm finds the
global minimum. A deterministic greedy fallback exists for limited
environments, but formal research runs should use SciPy so the method is truly
optimal under the defined cost.

This constraint guarantees valid color counts. It does not guarantee correct
positions or a physically reachable cube.

## 8. Confidence

For each sticker, costs are sorted and confidence is based on the relative
margin between the best and second-best prototype:

```text
confidence = (second_best - best) / max(second_best, epsilon)
```

A large margin means the best class is well separated. A small margin indicates
ambiguity, often between red/orange or white/yellow. Confidence is a diagnostic
and rejection signal; it is not automatically a calibrated probability.

## 9. Validation layers

Validation is separated into increasingly strong questions:

1. Does the string contain 54 symbols?
2. Are all symbols among `U/R/F/D/L/B`?
3. Does every symbol occur exactly nine times?
4. Does each face contain its expected center?
5. Is the state physically reachable according to cubie constraints/Kociemba?

Separating these stages produces actionable errors. “Wrong number of blue
stickers” suggests classification failure, while balanced counts followed by
an impossible state more often suggests a face rotation or positional error.

## 10. Temporal processing

A camera burst can contain exposure fluctuation, motion blur, and glare. The
temporal module supports:

- median aggregation across repeated 54-sticker measurements;
- trimmed-mean aggregation;
- Laplacian-variance sharpness;
- clipped dark/bright pixel fraction;
- normalized frame-to-frame difference.

The eventual capture controller should accept frames only when geometric
alignment, sharpness, exposure, and motion all meet thresholds determined on a
validation set.

## 11. Error handling and privacy

Camera resources are released in `finally` blocks even when capture fails.
Expected invalid cube states are reported separately from unexpected software
errors. Low-confidence or invalid scans should be rejected instead of silently
presenting a potentially incorrect solution.

The live prototype processes frames locally and does not upload them. Research
images exist only when the researcher deliberately saves them. Real frames
should not be committed to a public repository without review and consent.

## 12. Testing strategy

The test suite covers four levels:

### Unit tests

- face rotations;
- move/inverse relationships;
- Lab classification;
- balanced color counts;
- temporal aggregation;
- metric calculations.

### Geometry tests

- guide scaling;
- perspective-grid ordering;
- contour detection on synthetic frames;
- grouping into face hypotheses.

### Integration tests

- reconstructing a solved cube from six sampled faces;
- combining both views;
- solving a known legal scramble.

### Research-integrity tests

- manifest schema validation;
- unique sample identifiers;
- canonical ground-truth counts;
- train/test session-scramble leakage rejection;
- deterministic bootstrap calculations.

Synthetic tests establish code correctness, not real-world camera accuracy.
Only the labeled held-out dataset can establish robustness.

## 13. Reproduction commands

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,research]"
python -m pytest -q
python -m ruff check src tests
```

Run the complete scanner:

```powershell
python -m vision.two_view_preview
```

Run saved observations through both research conditions:

```powershell
python -m vision.experiments data/processed/test_samples.json `
  --method independent_lab --output artifacts/independent.csv

python -m vision.experiments data/processed/test_samples.json `
  --method balanced_lab --output artifacts/balanced.csv
```

## 14. Important engineering limitations

- Face-orientation transforms require verification with known asymmetric states.
- The fixed guide assumes a standard color arrangement.
- The alignment score is heuristic and not yet calibrated on labeled examples.
- The automatic contour path is resolution- and illumination-sensitive.
- Balanced assignment can force an uncertain sticker into a class solely to
  satisfy counts.
- Physical solvability does not prove that a scan matches the real cube.
- The real dataset and held-out experimental results have not yet been created.
