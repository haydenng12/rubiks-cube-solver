# Computer Vision Architecture Decisions

## Status

Accepted. This document records the principal design decisions for the
camera-based cube reconstruction pipeline.

## Context

The solver requires a canonical 54-sticker state in `URFDLB` order. Camera
input introduces uncertainty in pose, perspective, illumination, color
appearance, motion, glare, and face orientation. The vision subsystem is
therefore responsible for acquiring observations, normalizing geometry,
classifying sticker colors, reconstructing canonical face order, and rejecting
unreliable states before solver invocation.

The project supports standard six-color 3x3 cubes. Nonstandard color schemes,
picture cubes, and larger cube sizes are outside the current scope.

## Decision 1: Guided capture is the primary acquisition method

### Decision

The primary workflow uses two prescribed three-face poses:

- first observation: `U/F/R`;
- second observation: `D/B/L`.

Resolution-independent overlays provide a geometric prior for each visible
face. A contour-based automatic detector remains available as an experimental
baseline.

### Rationale

Unconstrained pose discovery requires simultaneous estimation of cube
orientation, visible face identity, grid geometry, and sticker correspondence.
Guided capture reduces this ambiguity while retaining automatic color sampling
and state reconstruction. The two-view protocol also makes face identity and
center-based calibration explicit.

### Consequences

- Capture behavior is more deterministic and testable.
- The user must follow a documented orientation protocol.
- Incorrect physical rotation between views can still produce positional
  errors and must be detected through validation and confidence checks.
- Automatic and hybrid localization can be evaluated against the guided
  baseline using identical downstream components.

## Decision 2: Manual input remains a supported adapter

### Decision

Manual face entry remains available independently of camera support.

### Rationale

Manual input provides a deterministic reference path for validating cube
representation, move application, solver integration, and playback. It also
isolates vision failures from downstream solver failures.

### Consequences

- Core cube behavior can be tested without OpenCV or camera hardware.
- The vision subsystem is implemented as an input adapter rather than a second
  solver architecture.

## Decision 3: Perspective normalization precedes color sampling

### Decision

Each observed face is mapped from a camera-space quadrilateral to a canonical
square using a projective homography. Sticker colors are sampled from the
interiors of the resulting 3x3 cells.

### Rationale

Direct sampling in the original frame is sensitive to perspective distortion
and can mix sticker interiors with borders or adjacent faces. Normalization
provides a consistent coordinate system for cell indexing and downstream
classification.

### Consequences

- Face ordering is deterministic after a valid quadrilateral is established.
- Homography quality depends on accurate guide alignment or face localization.
- Geometry errors can propagate into color measurements and must be retained
  in diagnostic output.

## Decision 4: Robust regions replace single-pixel measurements

### Decision

Sticker appearance is represented by the median color of a central cell region.
The sampled region excludes most grid borders.

### Rationale

Single pixels are sensitive to sensor noise, reflections, compression, and
minor geometric error. Regional medians reduce the influence of isolated
outliers and specular highlights.

### Consequences

- Sampling is more stable under small perturbations.
- Large highlights or substantial misalignment can still bias a region.
- Temporal aggregation is evaluated separately rather than embedded
  implicitly in the single-frame sampler.

## Decision 5: Classification uses session-specific center calibration

### Decision

The six center stickers define the color prototypes for each capture session.
Sticker-to-prototype costs are calculated in CIE Lab space.

### Rationale

Physical centers are fixed and identify the six face classes. Session-specific
prototypes adapt to camera and lighting changes without requiring a personal
training dataset. Lab coordinates provide a more perceptually meaningful
distance than raw BGR differences.

### Consequences

- Ordinary users do not need to train or contribute a dataset.
- Calibration quality depends on correct center sampling.
- Center calibration does not fully eliminate spatially uneven illumination.
- Fixed HSV thresholds and alternative feature spaces remain research
  baselines.

## Decision 6: Global color counts are an experimental constraint

### Decision

The system supports both independent nearest-prototype classification and a
balanced global assignment with exactly nine stickers per color.

### Rationale

A standard cube contains nine stickers of each color. Independent decisions can
violate this invariant. Balanced assignment incorporates known problem
structure by minimizing total classification cost subject to valid counts.

### Consequences

- Balanced assignment guarantees color-count validity.
- It does not guarantee correct positions or physical solvability.
- The constraint can force an ambiguous sample into an incorrect class.
- Independent and constrained methods must be evaluated on the same saved
  observations.

## Decision 7: Face orientation is represented explicitly

### Decision

Camera observations are converted to canonical solver coordinates through
named per-face rotation transforms.

### Rationale

Correct color recognition alone is insufficient. A face that is rotated or
mirrored relative to Kociemba's indexing convention produces an incorrect or
impossible state. Explicit transforms are reviewable, testable, and independent
of classification.

### Consequences

- Orientation behavior is not hidden in list slicing or capture code.
- Known asymmetric cube states are required to validate all transforms.
- Mirror behavior is treated as a separate acquisition setting.

## Decision 8: Validation is layered

### Decision

The reconstructed state passes through syntax, color-count, center, and
physical-solvability checks before solver output is accepted.

### Rationale

Different failure categories require different remediation. Invalid counts
usually indicate classification error; valid counts with an impossible state
may indicate positional or orientation error. Layered validation preserves this
diagnostic distinction.

### Consequences

- Invalid observations are rejected before playback.
- A physically solvable prediction is not assumed to match the physical cube.
- Exact comparison with labeled ground truth remains necessary during
  evaluation.

## Decision 9: Research evaluation is separated from live capture

### Decision

Saved sticker measurements and metadata are evaluated offline through a common
experiment interface.

### Rationale

Recording a new camera presentation for each method would confound algorithm
choice with pose and lighting changes. Replaying identical observations
supports controlled paired comparisons and reproducible result generation.

### Consequences

- Raw observations, predictions, configurations, and metrics can be versioned
  independently.
- Train, validation, and test groups are defined by capture session and
  scramble to prevent adjacent-frame leakage.
- Live demonstrations are not treated as evidence of real-world accuracy.

## Decision 10: Camera data remains local unless deliberately published

### Decision

The live scanner does not upload frames. Research recordings are created only
through an explicit collection workflow and are excluded from public release
unless reviewed and approved for publication.

### Rationale

Camera frames may contain people, documents, or other private background
information. Public source code does not require public raw imagery.

### Consequences

- Dataset collection requires a documented consent and review process.
- Public artifacts should prefer cropped cube regions, anonymized samples,
  metadata, and aggregate results.
- Any committed file in the public repository must be treated as publicly
  accessible.
