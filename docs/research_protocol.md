# Research Protocol

## Question

How do per-session calibration, perceptual color representation, balanced
color assignment, and temporal aggregation affect camera-based Rubik's Cube
state reconstruction under changes in illumination and viewpoint?

## Hypotheses

1. Center-calibrated Lab classification will outperform uncalibrated color thresholds.
2. Enforcing nine assignments per color will improve structurally valid and exact-cube rates.
3. Multi-frame median aggregation will reduce glare and sensor-noise errors.
4. Guided/hybrid localization will outperform contour-only localization in full-scan success.

## Scope

The study supports standard six-color 3x3 cubes. The user follows two fixed
capture poses. Picture cubes, nonstandard color schemes, and larger cubes are
out of scope and must not be silently included in headline results.

## Independent variables

- classifier and assignment method;
- localization method;
- illumination category;
- camera distance and view angle;
- glare level;
- single-frame versus temporal aggregation.

## Outcomes

Primary outcomes are exact 54-sticker reconstruction and end-to-end solvable
state rate. Secondary outcomes are sticker accuracy, macro F1, per-color
confusion, localization success, rejection quality, retries, and latency.

## Dataset protocol

Use at least 20 legal scrambles, multiple recording sessions, and repeated
captures across the condition matrix. Generate and save the ground-truth state
before physically applying each scramble. Store consented frames locally and
remove incidental faces or personal material before publishing.

Split by both session and scramble. Adjacent video frames from the same capture
must never be divided between train and test data. Thresholds are frozen using
training/validation data before the held-out test set is evaluated.

## Statistical protocol

Run every method on the same held-out observations. Report means, standard
deviations, and 95% bootstrap confidence intervals. Use paired bootstrap
differences for method comparisons. A frame is not an independent trial when
it belongs to the same capture burst; the capture session is the resampling unit.

## Exclusions

Only unreadable/corrupt files or protocol violations may be excluded. Scanner
rejections, missing detections, invalid cubes, and solver failures are outcomes,
not exclusions.

## Reproducibility

Record the commit SHA, configuration, random seed, environment, prediction
file, and dataset-manifest hash for every run. Never edit final prediction files
by hand and never publish a results table produced from the training split.
