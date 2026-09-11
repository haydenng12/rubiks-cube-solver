# Research Methodology and Experimental Plan

## 1. Research contribution

The project does not claim a new Rubik's Cube solving algorithm. Kociemba is a
well-established downstream solver. The research contribution is an empirical
study of robust visual state reconstruction: determining which practical
computer-vision choices most reliably transform camera observations into the
exact symbolic state required by the solver.

## 2. Primary research question

> How do session-specific color calibration, perceptual color representation,
> temporal aggregation, and global cube constraints affect the robustness of
> camera-based 3x3 Rubik's Cube reconstruction under realistic imaging changes?

## 3. Supporting questions

1. Does guided localization outperform automatic contour localization?
2. Does center calibration improve performance across cameras and lighting?
3. Does Lab classification outperform an HSV-threshold baseline?
4. Does enforcing nine stickers per color improve exact-cube and solvable-state
   rates?
5. Does aggregating multiple stable frames reduce errors caused by glare and
   sensor noise?
6. Which environmental variable produces the largest accuracy decline?
7. Can confidence and structural checks reject bad scans before an incorrect
   solution is presented?

## 4. Hypotheses

- **H1:** Center-calibrated Lab classification will outperform fixed HSV ranges.
- **H2:** Balanced assignment will improve structurally valid and exact-cube
  reconstruction rates relative to independent classification.
- **H3:** Temporal median aggregation will outperform single-frame sampling in
  glare and dim-light conditions.
- **H4:** Guided and hybrid localization will produce higher full-scan success
  than contour-only localization.
- **H5:** Low classification margins will be associated with incorrect stickers
  and can support useful rejection.

These hypotheses must be recorded before inspecting final test results.

## 5. Experimental unit

The primary unit is one complete physical cube capture session, consisting of
both required views of one legal scramble under one environmental condition.

Individual video frames from a burst are not independent trials. Treating them
as separate samples would make confidence intervals too narrow and allow nearly
identical frames to leak across data splits.

## 6. Dataset design

### 6.1 Suggested initial size

A practical undergraduate study could use:

- 24 legal scrambles;
- 5 lighting conditions;
- 3 viewing-angle categories;
- 2 distances;
- 2 repeated capture sessions for a selected balanced subset.

A full Cartesian product may be unnecessarily large. Use a balanced design in
which every primary method sees the exact same captured observations. Record
the final matrix before collection.

### 6.2 Ground truth

For every scramble:

1. start with a verified solved cube;
2. generate and save a legal move sequence;
3. compute the canonical resulting state using the move engine;
4. physically apply the identical sequence;
5. photograph the unchanged cube in both prescribed poses;
6. manually verify the six centers and several asymmetric corner/edge positions;
7. save the ground truth with the capture record.

Do not infer ground truth from the scanner being evaluated.

### 6.3 Metadata

Each observation records:

- sample, session, and scramble identifiers;
- image or recording paths;
- cube model/finish;
- camera identifier and resolution;
- lighting category;
- distance category;
- view-angle category;
- glare category;
- background category;
- canonical ground-truth state;
- protocol deviations or exclusion reason.

### 6.4 Data split

Use grouped train/validation/test splits.

- Training data may inform implementation choices.
- Validation data selects thresholds and rejection rules.
- Test data is opened only after methods and thresholds are frozen.

All frames from the same session and all repeated observations of the same
scramble should remain in one split when feasible. At minimum, no adjacent
frames or identical session-scramble combination may cross splits.

## 7. Experimental conditions

### Experiment A: color representation and calibration

| Condition | Calibration | Feature space | Decision rule |
|---|---|---|---|
| A0 | None | HSV | Fixed thresholds |
| A1 | Centers | HSV | Nearest prototype |
| A2 | Centers | Lab | Nearest prototype |
| A3 | Centers | Lab | Balanced global assignment |

This experiment isolates the contribution of calibration, feature space, and
assignment constraints.

### Experiment B: temporal aggregation

| Condition | Frames | Aggregation |
|---|---:|---|
| B0 | 1 | None |
| B1 | 3 or 5 | Mean |
| B2 | 3 or 5 | Median |
| B3 | 5 or more | Trimmed mean |

Use identical capture bursts. Do not record a new cube presentation for every
method, because pose differences would confound the comparison.

### Experiment C: localization

| Condition | Localization |
|---|---|
| C0 | Existing contour detector and k-means grouping |
| C1 | Fixed guided quadrilaterals |
| C2 | Guide initialized, locally refined quadrilaterals |

All localization methods should feed the same sampler and classifier.

### Experiment D: rejection and correction

| Condition | Safeguard |
|---|---|
| D0 | None |
| D1 | Confidence threshold |
| D2 | Confidence plus color-count validation |
| D3 | Confidence, counts, and physical-solvability validation |

Rejection creates a coverage/accuracy tradeoff. A method that rejects every
scan is accurate on accepted scans but useless, so both acceptance rate and
conditional accuracy must be reported.

## 8. Environmental factors

Recommended controlled categories include:

- neutral indoor light;
- warm indoor light;
- cool indoor light;
- daylight;
- dim light;
- no, mild, and strong glare;
- near, nominal, and far distance;
- low, medium, and high view angle;
- plain and cluttered backgrounds;
- multiple cameras if available.

Record objective quantities such as exposure or image brightness when possible,
but retain human-readable categories for result interpretation.

## 9. Metrics

### 9.1 Sticker accuracy

```text
correct sticker positions / 54
```

Useful for diagnosing incremental improvements, but insufficient alone. A cube
with 53 correct stickers is usually unusable.

### 9.2 Macro F1

Compute precision and recall separately for each of the six colors, convert
them to F1, and average the six values equally. This prevents a method's strong
performance on easy colors from hiding poor red/orange separation.

### 9.3 Exact-face accuracy

The fraction of faces for which all nine positions are correct.

### 9.4 Exact-cube accuracy

The fraction of sessions for which all 54 positions match ground truth. This is
the primary perception metric.

### 9.5 Structural validity

The fraction with 54 legal symbols, nine per color, and correct centers.

### 9.6 Physical-solvability rate

The fraction accepted by cubie constraints/Kociemba. A solvable prediction can
still represent the wrong physical state, so this is not an accuracy metric.

### 9.7 End-to-end solve success

The fraction of physical trials where following the returned moves solves the
actual cube. This is the most intuitive system metric but is expensive to label
and should complement, not replace, exact-state comparison.

### 9.8 Coverage and rejection quality

Report:

- accepted scans / attempted scans;
- exact-cube accuracy among accepted scans;
- incorrect scans caught by rejection;
- correct scans unnecessarily rejected;
- number of retries required.

### 9.9 Latency

Measure localization, sampling, classification, validation, and total latency.
Report distributions rather than one favorable measurement.

## 10. Statistical analysis

Every method must be evaluated on the same held-out sessions. This paired design
reduces noise because difficult observations are shared.

Report:

- number of independent capture sessions;
- mean metric values;
- standard deviation where meaningful;
- 95% confidence intervals;
- paired difference between methods;
- environmental subgroup results.

Use cluster bootstrap resampling at the capture-session level. If repeated
observations belong to one recording session, resample that cluster as a unit.
For paired method comparison, calculate the per-observation difference first
and bootstrap those clustered differences.

Avoid claiming “statistical significance” from thousands of neighboring video
frames. The effective sample size is the number of independent captures, not
the number of decoded frames.

## 11. Failure taxonomy

Every failed full-cube reconstruction should be assigned one primary cause:

- guide misalignment;
- blur/motion;
- exposure clipping;
- specular glare;
- missed or duplicated contour;
- face grouping failure;
- incorrect cell ordering;
- red/orange confusion;
- white/yellow confusion;
- other color confusion;
- second-view rotation error;
- mirrored preview error;
- invalid ground truth;
- unknown.

Save diagnostic overlays for failed cases. A failure taxonomy often produces
more useful research insight than one aggregate accuracy number.

## 12. Reproducibility record

Every formal experiment should preserve:

- Git commit SHA;
- dataset-manifest hash and version;
- configuration file;
- Python and dependency versions;
- random seed;
- split identifiers;
- raw prediction file;
- aggregate result tables;
- plotting script output;
- runtime environment and camera identifiers.

Prediction files should be append-only artifacts generated by code. Never edit
predictions manually to correct an inconvenient result.

## 13. Research integrity

The project currently contains a method and experimental infrastructure, not a
completed empirical study. Until real labeled captures are collected, the
repository may accurately claim that it implements and tests the algorithms,
but it may not claim improved real-world accuracy.

Negative or neutral results remain valuable. For example, if balanced
assignment improves valid color counts but not exact-cube accuracy, that shows
that global counts repair one failure mode while positional mistakes remain.

All scanner failures and rejected captures count as outcomes. They must not be
excluded merely because the algorithm performed poorly.

## 14. Privacy and dataset publication

Ordinary users do not create or upload a dataset. Their live frames are
processed locally unless a future feature deliberately saves them.

Research recordings should minimize the background, avoid faces and personal
documents, and be reviewed before publication. A public GitHub repository makes
every committed image visible. Prefer publishing cropped cube regions, a small
anonymized sample, aggregate results, or a separately consented dataset release.

## 15. Results structure

When data is available, report results in this order:

1. dataset composition and split;
2. baseline performance;
3. classifier/calibration ablation;
4. temporal aggregation ablation;
5. localization comparison;
6. performance by environmental condition;
7. confidence/rejection tradeoff;
8. latency;
9. qualitative failures;
10. limitations and threats to validity.

Do not select only favorable conditions for the headline table.

## 16. Threats to validity

### Internal validity

- changing poses between method runs;
- tuning thresholds on test observations;
- incorrect ground truth;
- orientation bugs mistaken for color errors;
- frame leakage between splits.

### External validity

- only one cube brand;
- only one camera;
- one room or lighting setup;
- only the standard color scheme;
- captures performed by the developer rather than new users.

### Construct validity

- using solvability as a substitute for correctness;
- reporting sticker accuracy without exact-cube accuracy;
- treating confidence margins as calibrated probabilities;
- ignoring rejected attempts when reporting success.
