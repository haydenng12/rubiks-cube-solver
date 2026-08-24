"""Drawing helpers for the guided three-face capture experience."""

from __future__ import annotations

from typing import Sequence

import cv2
import numpy as np

from .alignment import AlignmentConfig, FaceAlignment
from .guide_layout import FaceGuide, interpolate_quad_point
from .warp_sampling import SampledFace


def _contour(points: Sequence[Sequence[float]]) -> np.ndarray:
    return np.asarray(points, dtype=np.int32).reshape(-1, 1, 2)


def _text(frame: np.ndarray, text: str, origin: tuple[int, int], color: tuple[int, int, int]) -> None:
    cv2.putText(frame, text, origin, cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(frame, text, origin, cv2.FONT_HERSHEY_SIMPLEX, 0.58, color, 2, cv2.LINE_AA)


def _cell_polygon(guide: FaceGuide, row: int, col: int) -> np.ndarray:
    u1, u2 = col / 3.0, (col + 1) / 3.0
    v1, v2 = row / 3.0, (row + 1) / 3.0
    return _contour(
        (
            interpolate_quad_point(guide.corners, u1, v1),
            interpolate_quad_point(guide.corners, u2, v1),
            interpolate_quad_point(guide.corners, u2, v2),
            interpolate_quad_point(guide.corners, u1, v2),
        )
    )


def _draw_face_grid(frame: np.ndarray, guide: FaceGuide, color: tuple[int, int, int]) -> None:
    cv2.polylines(frame, [_contour(guide.corners)], True, color, 3)
    for fraction in (1 / 3, 2 / 3):
        vertical = (interpolate_quad_point(guide.corners, fraction, 0), interpolate_quad_point(guide.corners, fraction, 1))
        horizontal = (interpolate_quad_point(guide.corners, 0, fraction), interpolate_quad_point(guide.corners, 1, fraction))
        cv2.line(frame, tuple(map(int, vertical[0])), tuple(map(int, vertical[1])), color, 2, cv2.LINE_AA)
        cv2.line(frame, tuple(map(int, horizontal[0])), tuple(map(int, horizontal[1])), color, 2, cv2.LINE_AA)


def draw_guided_alignment(
    frame: np.ndarray,
    guides: tuple[FaceGuide, ...],
    alignments: tuple[FaceAlignment, ...],
    stable_frames: int,
    config: AlignmentConfig,
) -> np.ndarray:
    overlay = frame.copy()
    alignment_by_face = {item.face: item for item in alignments}

    for guide in guides:
        item = alignment_by_face[guide.face]
        ready = item.score >= config.minimum_face_score
        line_color = (70, 235, 70) if ready else (0, 210, 255)

        center_layer = overlay.copy()
        cv2.fillConvexPoly(center_layer, _cell_polygon(guide, 1, 1), guide.display_bgr)
        cv2.addWeighted(center_layer, 0.28, overlay, 0.72, 0, overlay)
        _draw_face_grid(overlay, guide, line_color)

        center = interpolate_quad_point(guide.corners, 0.5, 0.5)
        label = f"{guide.face}: {guide.expected_color.upper()}  {item.score:.2f}"
        _text(overlay, label, (int(center[0]) - 55, int(center[1]) + 5), line_color)

    panel = overlay.copy()
    cv2.rectangle(panel, (8, 8), (650, 104), (0, 0, 0), -1)
    cv2.addWeighted(panel, 0.78, overlay, 0.22, 0, overlay)
    if stable_frames >= config.stable_frames_required:
        status = "READY - press SPACE to capture"
        status_color = (70, 235, 70)
    elif stable_frames > 0:
        status = f"Hold steady: {stable_frames}/{config.stable_frames_required}"
        status_color = (0, 210, 255)
    else:
        status = "Align cube grids and center colors with the guide"
        status_color = (0, 210, 255)
    _text(overlay, status, (20, 35), status_color)
    _text(overlay, "SPACE: capture anyway   Q/ESC: quit", (20, 64), (255, 255, 255))
    _text(overlay, "Guide: WHITE top, GREEN front-left, RED right", (20, 92), (255, 255, 255))
    return overlay


def draw_capture_review(
    frame: np.ndarray,
    guides: tuple[FaceGuide, ...],
    sampled_faces: tuple[SampledFace, ...],
) -> np.ndarray:
    overlay = frame.copy()
    sample_by_face = {sample.face: sample for sample in sampled_faces}
    color_layer = overlay.copy()

    for guide in guides:
        sampled = sample_by_face[guide.face]
        for sticker in sampled.stickers:
            bgr = tuple(int(round(value)) for value in sticker.median_bgr)
            cv2.fillConvexPoly(color_layer, _cell_polygon(guide, sticker.row, sticker.col), bgr)
        _draw_face_grid(color_layer, guide, (255, 255, 255))

    cv2.addWeighted(color_layer, 0.72, overlay, 0.28, 0, overlay)
    panel = overlay.copy()
    cv2.rectangle(panel, (8, 8), (665, 82), (0, 0, 0), -1)
    cv2.addWeighted(panel, 0.80, overlay, 0.20, 0, overlay)
    _text(overlay, "REVIEW: sampled colors replace the guide cells", (20, 35), (255, 255, 255))
    _text(overlay, "A: accept and exit   R: rescan   Q/ESC: quit", (20, 65), (70, 235, 70))
    return overlay
