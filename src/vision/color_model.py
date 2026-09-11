"""Color-classification baselines used by the reconstruction experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import cv2
import numpy as np

COLOR_ORDER = ("U", "R", "F", "D", "L", "B")


@dataclass(frozen=True)
class ClassificationResult:
    labels: tuple[str, ...]
    confidence: tuple[float, ...]
    costs: np.ndarray


def bgr_to_lab(colors: Sequence[Sequence[float]]) -> np.ndarray:
    pixels = np.clip(np.asarray(colors), 0, 255).astype(np.uint8).reshape(1, -1, 3)
    return cv2.cvtColor(pixels, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)


def distance_matrix(samples_bgr: Sequence[Sequence[float]], prototypes_bgr: Mapping[str, Sequence[float]]):
    samples = bgr_to_lab(samples_bgr)
    prototypes = bgr_to_lab([prototypes_bgr[label] for label in COLOR_ORDER])
    return np.linalg.norm(samples[:, None, :] - prototypes[None, :, :], axis=2)


def _confidence(costs: np.ndarray) -> tuple[float, ...]:
    ordered = np.sort(costs, axis=1)
    margins = (ordered[:, 1] - ordered[:, 0]) / np.maximum(ordered[:, 1], 1e-6)
    return tuple(float(value) for value in np.clip(margins, 0.0, 1.0))


def classify_independent(samples_bgr, prototypes_bgr) -> ClassificationResult:
    costs = distance_matrix(samples_bgr, prototypes_bgr)
    labels = tuple(COLOR_ORDER[index] for index in np.argmin(costs, axis=1))
    return ClassificationResult(labels, _confidence(costs), costs)


def classify_balanced(samples_bgr, prototypes_bgr, count_per_color=9) -> ClassificationResult:
    """Minimum-cost labeling subject to an equal count for every cube color."""
    costs = distance_matrix(samples_bgr, prototypes_bgr)
    if len(costs) != len(COLOR_ORDER) * count_per_color:
        raise ValueError("Balanced classification requires six equally sized color classes")
    try:
        from scipy.optimize import linear_sum_assignment

        slots = np.repeat(np.arange(len(COLOR_ORDER)), count_per_color)
        expanded = costs[:, slots]
        rows, columns = linear_sum_assignment(expanded)
        assigned = np.empty(len(costs), dtype=int)
        assigned[rows] = slots[columns]
    except ImportError:
        # Deterministic dependency-free fallback. It improves count validity but is
        # not guaranteed globally optimal; research runs should install [research].
        assigned = np.full(len(costs), -1, dtype=int)
        remaining = np.full(len(COLOR_ORDER), count_per_color, dtype=int)
        for row in np.argsort(np.min(costs, axis=1)):
            valid = np.where(remaining > 0)[0]
            choice = valid[np.argmin(costs[row, valid])]
            assigned[row] = choice
            remaining[choice] -= 1
    labels = tuple(COLOR_ORDER[index] for index in assigned)
    return ClassificationResult(labels, _confidence(costs), costs)


def prototypes_from_centers(samples_bgr, center_indices: Mapping[str, int]):
    return {label: tuple(samples_bgr[index]) for label, index in center_indices.items()}
