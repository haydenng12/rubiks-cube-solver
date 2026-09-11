# Rubik's Cube Vision Research

[![tests](https://github.com/haydenng12/rubiks-cube-solver/actions/workflows/tests.yml/badge.svg)](https://github.com/haydenng12/rubiks-cube-solver/actions/workflows/tests.yml)

An experimental system for measuring how calibration, color representation,
assignment constraints, and capture strategy affect camera-based reconstruction
of a physical 3x3 Rubik's Cube.

This repository still solves cubes with Kociemba, but solving is not the research
contribution. The central problem is reliably turning two camera observations
into the exact 54-sticker state required by a solver.

## Research question

> How do per-session calibration, perceptual color representation, temporal
> aggregation, and global color-count constraints affect reconstruction under
> real-world illumination and viewpoint changes?

The hypotheses and frozen evaluation rules are in
[`docs/research_protocol.md`](docs/research_protocol.md). The repository provides
the software and protocol; it intentionally does not ship invented camera data
or unsupported results.

## System

1. Capture `U/F/R` using a resolution-independent three-face guide.
2. Capture the opposite `D/B/L` view.
3. Perspective-warp each face and sample all 54 sticker interiors.
4. Use the six centers as per-session color prototypes.
5. Classify in Lab space, independently or with exactly nine labels per color.
6. Apply explicit face-orientation transforms and assemble canonical `URFDLB`.
7. Validate structure and pass valid states to Kociemba.
8. Save predictions so methods can be evaluated on identical observations.

The older contour detector remains an automatic-localization baseline. Fixed
Canny thresholds, strict 27-contour acceptance, and unconstrained k-means
grouping are measurable baselines for the guided/hybrid comparison.

## Current infrastructure

- cube simulation and Kociemba integration;
- guided perspective sampling for both corner views;
- center-calibrated Lab classification;
- independent and balanced nine-per-color assignment;
- explicit face-rotation fusion and confidence margins;
- dataset validation and split-leakage protection;
- sticker accuracy, macro F1, and exact-cube accuracy;
- deterministic experiment runner, condition matrix, CI, and package metadata.

Real-camera collection and final held-out results remain experimental work. A
structurally valid scan is not evidence that the method is accurate; conclusions
must come from labeled held-out data.

## Install

Python 3.10 or newer is supported.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,research]"
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run

```bash
# Existing manual solver
python src/main.py

# One-view guided diagnostic
python -m vision.guided_preview

# Two-view calibrated reconstruction
python -m vision.two_view_preview

# Automatic contour/localization baseline
python -m vision.diagnostic_preview
```

The two-view prototype asks for `U/F/R` followed by `D/B/L`, prints a
canonical candidate state, and identifies the least-confident stickers.
Physical orientation must be verified with known states before formal capture.

## Dataset and experiments

Copy `data/manifest_template.csv` and follow
[`docs/dataset_card.md`](docs/dataset_card.md). Never randomly split adjacent
frames: train and test observations are grouped by both session and scramble.

Saved experiment records contain `sample_id`, a 54-character `labels` value,
54 `samples_bgr` triples in canonical order, and six center
`prototypes_bgr`.

```bash
python -m vision.experiments data/processed/test_samples.json \
  --method independent_lab --output artifacts/independent.csv

python -m vision.experiments data/processed/test_samples.json \
  --method balanced_lab --output artifacts/balanced.csv
```

Report exact-cube accuracy alongside sticker accuracy. Even one wrong sticker
can make an otherwise high-accuracy reconstruction unusable.

## Verification

```bash
python -m pytest -q
python -m pytest --cov=src --cov-report=term-missing
python -m ruff check src tests
```

CI runs the suite on Python 3.10 and 3.12.

## Repository map

```text
configs/                       frozen experiment matrix
data/                          real-data manifest schema
docs/                          research protocol and dataset card
src/vision/color_model.py      Lab classifiers and assignment constraints
src/vision/dataset.py          manifest and leakage validation
src/vision/experiments.py      repeatable evaluation entry point
src/vision/metrics.py          reconstruction metrics
src/vision/reconstruction.py  sampled colors to canonical cube state
src/vision/scan_fusion.py      explicit orientation transforms
tests/                         unit and integration tests
```

## Limitations

- Standard six-color 3x3 cubes only.
- The guide assumes the documented white/green/red and yellow/blue/orange poses.
- Strong glare and incorrect physical rotations can invalidate reconstruction.
- Balanced assignment guarantees color counts, not physical solvability.
- No performance result should be claimed until the real held-out study runs.

Citation metadata is provided in `CITATION.cff`.
