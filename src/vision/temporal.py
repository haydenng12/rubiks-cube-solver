"""Robust aggregation and stability measures for capture bursts."""

from __future__ import annotations

from typing import Sequence

import cv2
import numpy as np


def aggregate_bgr(sample_frames: Sequence[Sequence[Sequence[float]]], method="median") -> np.ndarray:
    values = np.asarray(sample_frames, dtype=np.float32)
    if values.ndim != 3 or values.shape[1:] != (54, 3):
        raise ValueError("Expected frames x 54 stickers x 3 BGR channels")
    if method == "median":
        return np.median(values, axis=0)
    if method == "trimmed_mean":
        if len(values) < 3:
            return values.mean(axis=0)
        ordered = np.sort(values, axis=0)
        trim = max(1, int(len(values) * 0.1))
        core = ordered[trim:-trim] if len(values) > 2 * trim else ordered
        return core.mean(axis=0)
    raise ValueError(f"Unknown temporal aggregation method: {method}")


def frame_quality(frame: np.ndarray) -> dict[str, float]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    clipped = float(np.mean((gray <= 3) | (gray >= 252)))
    return {"sharpness": blur_variance, "clipped_fraction": clipped}


def normalized_frame_difference(previous: np.ndarray, current: np.ndarray) -> float:
    if previous.shape != current.shape:
        raise ValueError("Frames must have identical shapes")
    a = cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY).astype(np.float32)
    b = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY).astype(np.float32)
    return float(np.mean(np.abs(a - b)) / 255.0)
