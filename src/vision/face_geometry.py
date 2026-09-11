"""Recover a canonical 3 x 3 grid from one grouped cube face.

The grouping stage deliberately returns unordered sticker candidates.  This
module estimates the visible face boundary, maps it to a unit square, and
orders the candidates from top-left to bottom-right in that local coordinate
system.  Downstream sampling can therefore ignore camera rotation and
perspective.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import cv2
import numpy as np

DetectedSticker = Any
Point = tuple[float, float]


@dataclass(frozen=True)
class FaceGeometryConfig:
    expected_stickers: int = 9
    hull_epsilon_ratio: float = 0.04
    max_cell_error: float = 0.24
    min_quad_area: float = 100.0


@dataclass(frozen=True)
class FaceGeometry:
    ordered_stickers: tuple[DetectedSticker, ...]
    outer_corners: tuple[Point, Point, Point, Point]
    cell_error: float
    homography: np.ndarray = field(repr=False, compare=False)


def _order_quad(points: np.ndarray) -> np.ndarray:
    """Order four points as top-left, top-right, bottom-right, bottom-left."""

    pts = np.asarray(points, dtype=np.float32).reshape(4, 2)
    center = pts.mean(axis=0)
    angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
    ordered = pts[np.argsort(angles)]

    # The angle sort is cyclic.  Start at the most top-left point.
    start = int(np.argmin(ordered.sum(axis=1)))
    ordered = np.roll(ordered, -start, axis=0)

    # In image coordinates a clockwise traversal from TL visits TR next.
    first = ordered[1] - ordered[0]
    second = ordered[2] - ordered[1]
    cross = first[0] * second[1] - first[1] * second[0]
    if cross < 0:
        ordered = ordered[[0, 3, 2, 1]]
    return ordered


def _estimate_outer_quad(stickers: Sequence[DetectedSticker], config: FaceGeometryConfig) -> np.ndarray:
    all_corners = np.array(
        [corner for sticker in stickers for corner in sticker.corners],
        dtype=np.float32,
    )
    hull = cv2.convexHull(all_corners)
    perimeter = cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, config.hull_epsilon_ratio * perimeter, True)

    if len(approx) == 4 and cv2.isContourConvex(approx):
        quad = approx.reshape(4, 2)
    else:
        # A noisy hull may contain more than four vertices.  A minimum-area
        # rectangle is a deterministic fallback rather than an immediate loss
        # of an otherwise usable capture.
        quad = cv2.boxPoints(cv2.minAreaRect(all_corners))

    quad = _order_quad(quad)
    if abs(float(cv2.contourArea(quad))) < config.min_quad_area:
        raise ValueError("Face boundary is too small or degenerate.")
    return quad


def analyze_face_geometry(
    stickers: Sequence[DetectedSticker],
    config: FaceGeometryConfig | None = None,
) -> FaceGeometry:
    """Validate and order one face's sticker candidates.

    ``ordered_stickers`` is row-major in the face's normalized image:
    top-left through bottom-right.
    """

    if config is None:
        config = FaceGeometryConfig()
    if len(stickers) != config.expected_stickers:
        raise ValueError(
            f"Expected {config.expected_stickers} stickers for one face, got {len(stickers)}."
        )

    centers = np.asarray([sticker.center for sticker in stickers], dtype=np.float32)
    if len(np.unique(centers, axis=0)) != config.expected_stickers:
        raise ValueError("Sticker centers must be unique.")

    quad = _estimate_outer_quad(stickers, config)
    target = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],
        dtype=np.float32,
    )
    homography = cv2.getPerspectiveTransform(quad, target)
    normalized = cv2.perspectiveTransform(centers.reshape(-1, 1, 2), homography).reshape(-1, 2)

    expected_axis = np.array([1.0 / 6.0, 0.5, 5.0 / 6.0], dtype=np.float32)
    cells: dict[tuple[int, int], tuple[DetectedSticker, float]] = {}
    for sticker, point in zip(stickers, normalized):
        col = int(np.argmin(np.abs(expected_axis - point[0])))
        row = int(np.argmin(np.abs(expected_axis - point[1])))
        error = float(np.linalg.norm(point - np.array([expected_axis[col], expected_axis[row]])))
        key = (row, col)
        if key in cells:
            raise ValueError(f"Multiple stickers map to grid cell {key}.")
        if error > config.max_cell_error:
            raise ValueError(
                f"Sticker at {tuple(sticker.center)} is too far from its expected grid cell."
            )
        cells[key] = (sticker, error)

    expected_cells = {(row, col) for row in range(3) for col in range(3)}
    if set(cells) != expected_cells:
        missing = sorted(expected_cells - set(cells))
        raise ValueError(f"Detected stickers do not form a complete 3 x 3 grid; missing {missing}.")

    ordered = tuple(cells[(row, col)][0] for row in range(3) for col in range(3))
    mean_error = float(np.mean([entry[1] for entry in cells.values()]))
    outer_corners = tuple((float(x), float(y)) for x, y in quad)
    return FaceGeometry(
        ordered_stickers=ordered,
        outer_corners=outer_corners,  # type: ignore[arg-type]
        cell_error=mean_error,
        homography=homography,
    )


def analyze_face_group(group: Any, config: FaceGeometryConfig | None = None) -> FaceGeometry:
    """Convenience adapter for :class:`vision.face_grouping.FaceGroup`."""

    return analyze_face_geometry(group.stickers, config)
