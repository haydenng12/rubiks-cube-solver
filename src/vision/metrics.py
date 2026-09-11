"""Research metrics with no reporting-library dependency."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class ReconstructionMetrics:
    sticker_accuracy: float
    macro_f1: float
    exact_cube_accuracy: float
    samples: int


def evaluate_predictions(truth, predictions) -> ReconstructionMetrics:
    if len(truth) != len(predictions) or not truth:
        raise ValueError("Truth and predictions must be non-empty and equally sized")
    labels = "URFDLB"
    correct = total = exact = 0
    tp, fp, fn = Counter(), Counter(), Counter()
    for expected, predicted in zip(truth, predictions):
        if len(expected) != 54 or len(predicted) != 54:
            raise ValueError("Every cube state must contain 54 labels")
        exact += expected == predicted
        for e, p in zip(expected, predicted):
            total += 1
            correct += e == p
            if e == p:
                tp[e] += 1
            else:
                fp[p] += 1
                fn[e] += 1
    f1s = []
    for label in labels:
        denom = 2 * tp[label] + fp[label] + fn[label]
        f1s.append((2 * tp[label] / denom) if denom else 0.0)
    return ReconstructionMetrics(correct / total, sum(f1s) / len(f1s), exact / len(truth), len(truth))
