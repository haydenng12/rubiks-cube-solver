"""Structural alignment scoring for guided cube-face regions."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .warp_sampling import SampledFace


@dataclass(frozen=True)
class AlignmentConfig:
    grid_band_fraction: float = 0.035
    minimum_face_score: float = 0.35
    stable_frames_required: int = 12


@dataclass(frozen=True)
class FaceAlignment:
    face: str
    score: float
    grid_contrast: float
    uniformity: float


def _grid_pixels(lightness: np.ndarray, band_fraction: float) -> np.ndarray:
    size = lightness.shape[0]
    half_band = max(1, int(round(size * band_fraction / 2.0)))
    bands = []
    for boundary in (size // 3, 2 * size // 3):
        bands.append(lightness[:, boundary-half_band:boundary+half_band])
        bands.append(lightness[boundary-half_band:boundary+half_band, :])
    return np.concatenate([band.reshape(-1) for band in bands])


def score_face_alignment(sampled_face: SampledFace, config: AlignmentConfig | None = None) -> FaceAlignment:
    if config is None:
        config = AlignmentConfig()
    lab = cv2.cvtColor(sampled_face.warped_bgr, cv2.COLOR_BGR2LAB)
    lightness = lab[:, :, 0].astype(np.float32)
    interior_l = float(np.median([sample.median_lab[0] for sample in sampled_face.stickers]))
    grid_l = float(np.median(_grid_pixels(lightness, config.grid_band_fraction)))
    contrast = float(np.clip((interior_l - grid_l) / 80.0, 0.0, 1.0))
    spread = float(np.median([sample.lab_spread for sample in sampled_face.stickers]))
    uniformity = float(np.clip(1.0 - spread / 45.0, 0.0, 1.0))
    score = 0.72 * contrast + 0.28 * uniformity
    return FaceAlignment(sampled_face.face, float(score), contrast, uniformity)


def all_faces_ready(alignments: tuple[FaceAlignment, ...], config: AlignmentConfig | None = None) -> bool:
    if config is None:
        config = AlignmentConfig()
    return len(alignments) == 3 and all(item.score >= config.minimum_face_score for item in alignments)
