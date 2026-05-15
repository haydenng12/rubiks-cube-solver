"""Sticker candidate detection utilities (Phase 2).

This module detects square-like sticker candidates from a camera frame and
returns geometry + color metadata for downstream grouping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class StickerDetectionConfig:
    blur_kernel: Tuple[int, int] = (5, 5)
    canny_low: int = 60
    canny_high: int = 160
    min_area: float = 250.0
    max_area: float = 20000.0
    approx_epsilon_ratio: float = 0.04
    min_aspect_ratio: float = 0.6
    max_aspect_ratio: float = 1.4
    min_fill_ratio: float = 0.55
    sample_radius: int = 6


@dataclass(frozen=True)
class DetectedSticker:
    contour: np.ndarray
    corners: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]
    center: Tuple[int, int]
    area: float
    bbox: Tuple[int, int, int, int]
    avg_bgr: Tuple[float, float, float]
    avg_hsv: Tuple[float, float, float]


def preprocess_frame(frame: np.ndarray, config: StickerDetectionConfig) -> tuple[np.ndarray, np.ndarray]:
    blurred = cv2.GaussianBlur(frame, config.blur_kernel, 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    return gray, hsv


def _order_corners_tl_tr_br_bl(points: np.ndarray) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """Return corners in deterministic top-left, top-right, bottom-right, bottom-left order."""

    pts = points.reshape(-1, 2).astype(np.float32)
    sums = pts.sum(axis=1)
    diffs = np.diff(pts, axis=1).reshape(-1)

    top_left = pts[np.argmin(sums)]
    bottom_right = pts[np.argmax(sums)]
    top_right = pts[np.argmin(diffs)]
    bottom_left = pts[np.argmax(diffs)]

    return (
        (int(top_left[0]), int(top_left[1])),
        (int(top_right[0]), int(top_right[1])),
        (int(bottom_right[0]), int(bottom_right[1])),
        (int(bottom_left[0]), int(bottom_left[1])),
    )


def _mean_color_near_center(frame_bgr: np.ndarray, frame_hsv: np.ndarray, center: Tuple[int, int], radius: int) -> tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    h, w = frame_bgr.shape[:2]
    cx, cy = center
    x1 = max(0, cx - radius)
    y1 = max(0, cy - radius)
    x2 = min(w, cx + radius + 1)
    y2 = min(h, cy + radius + 1)

    patch_bgr = frame_bgr[y1:y2, x1:x2]
    patch_hsv = frame_hsv[y1:y2, x1:x2]

    bgr_mean = patch_bgr.mean(axis=(0, 1))
    hsv_mean = patch_hsv.mean(axis=(0, 1))

    avg_bgr: Tuple[float, float, float] = (
        float(bgr_mean[0]),
        float(bgr_mean[1]),
        float(bgr_mean[2]),
    )
    avg_hsv: Tuple[float, float, float] = (
        float(hsv_mean[0]),
        float(hsv_mean[1]),
        float(hsv_mean[2]),
    )
    return avg_bgr, avg_hsv


def _passes_geometry_filters(contour: np.ndarray, quad: np.ndarray, config: StickerDetectionConfig) -> bool:
    area = cv2.contourArea(contour)
    if area < config.min_area or area > config.max_area:
        return False

    if not cv2.isContourConvex(quad):
        return False

    x, y, w, h = cv2.boundingRect(quad)
    if h == 0:
        return False

    aspect_ratio = w / float(h)
    if not (config.min_aspect_ratio <= aspect_ratio <= config.max_aspect_ratio):
        return False

    box_area = float(w * h)
    if box_area <= 0:
        return False

    fill_ratio = area / box_area
    if fill_ratio < config.min_fill_ratio:
        return False

    return True


def find_sticker_candidates(frame: np.ndarray, config: StickerDetectionConfig | None = None) -> List[DetectedSticker]:
    if config is None:
        config = StickerDetectionConfig()

    gray, hsv = preprocess_frame(frame, config)
    edges = cv2.Canny(gray, config.canny_low, config.canny_high)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    candidates: List[DetectedSticker] = []

    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0:
            continue

        epsilon = config.approx_epsilon_ratio * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) != 4:
            continue

        if not _passes_geometry_filters(contour, approx, config):
            continue

        moments = cv2.moments(approx)
        if moments["m00"] == 0:
            continue

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        avg_bgr, avg_hsv = _mean_color_near_center(frame, hsv, (cx, cy), config.sample_radius)

        area = float(cv2.contourArea(contour))
        bbox = cv2.boundingRect(approx)
        corners = _order_corners_tl_tr_br_bl(approx)

        candidates.append(
            DetectedSticker(
                contour=contour,
                corners=corners,
                center=(cx, cy),
                area=area,
                bbox=(int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])),
                avg_bgr=avg_bgr,
                avg_hsv=avg_hsv,
            )
        )

    return candidates
