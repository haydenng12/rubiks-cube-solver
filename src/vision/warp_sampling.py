"""Perspective normalization and robust 3 x 3 color sampling."""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from .guide_layout import FaceGuide


@dataclass(frozen=True)
class SamplingConfig:
    face_size: int = 300
    sample_fraction: float = 0.46


@dataclass(frozen=True)
class StickerSample:
    row: int
    col: int
    median_bgr: tuple[float, float, float]
    median_lab: tuple[float, float, float]
    lab_spread: float


@dataclass(frozen=True)
class SampledFace:
    face: str
    expected_color: str
    stickers: tuple[StickerSample, ...]
    warped_bgr: np.ndarray = field(repr=False, compare=False)


def warp_face(frame: np.ndarray, guide: FaceGuide, face_size: int = 300) -> np.ndarray:
    source = np.asarray(guide.corners, dtype=np.float32)
    last = float(face_size - 1)
    destination = np.array(((0, 0), (last, 0), (last, last), (0, last)), dtype=np.float32)
    transform = cv2.getPerspectiveTransform(source, destination)
    return cv2.warpPerspective(frame, transform, (face_size, face_size))


def _cell_sample_bounds(index: int, cell_size: float, sample_fraction: float) -> tuple[int, int]:
    center = (index + 0.5) * cell_size
    radius = cell_size * sample_fraction / 2.0
    return int(round(center - radius)), int(round(center + radius))


def _triple(values: np.ndarray) -> tuple[float, float, float]:
    return float(values[0]), float(values[1]), float(values[2])


def sample_warped_face(
    warped_bgr: np.ndarray,
    face: str,
    expected_color: str,
    config: SamplingConfig | None = None,
) -> SampledFace:
    if config is None:
        config = SamplingConfig(face_size=warped_bgr.shape[0])
    if warped_bgr.ndim != 3 or warped_bgr.shape[2] != 3:
        raise ValueError("Expected a BGR image with three color channels.")
    if not 0.1 <= config.sample_fraction <= 0.9:
        raise ValueError("sample_fraction must be between 0.1 and 0.9.")

    lab = cv2.cvtColor(warped_bgr, cv2.COLOR_BGR2LAB)
    height, width = warped_bgr.shape[:2]
    samples = []
    for row in range(3):
        y1, y2 = _cell_sample_bounds(row, height / 3.0, config.sample_fraction)
        for col in range(3):
            x1, x2 = _cell_sample_bounds(col, width / 3.0, config.sample_fraction)
            bgr_patch = warped_bgr[y1:y2, x1:x2]
            lab_patch = lab[y1:y2, x1:x2]
            if bgr_patch.size == 0:
                raise ValueError(f"Empty sample region for cell ({row}, {col}).")
            median_bgr = np.median(bgr_patch, axis=(0, 1))
            median_lab = np.median(lab_patch, axis=(0, 1))
            distances = np.linalg.norm(lab_patch.astype(np.float32) - median_lab.astype(np.float32), axis=2)
            samples.append(StickerSample(row, col, _triple(median_bgr), _triple(median_lab), float(np.median(distances))))

    return SampledFace(face, expected_color, tuple(samples), warped_bgr)


def sample_guided_face(frame: np.ndarray, guide: FaceGuide, config: SamplingConfig | None = None) -> SampledFace:
    if config is None:
        config = SamplingConfig()
    return sample_warped_face(warp_face(frame, guide, config.face_size), guide.face, guide.expected_color, config)
