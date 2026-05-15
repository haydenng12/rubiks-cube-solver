"""Overlay helpers for guided scanner preview."""

from __future__ import annotations

from typing import Iterable, Sequence

import cv2
import numpy as np


def draw_guide_markers(frame: np.ndarray) -> np.ndarray:
    """Draw a central target marker to help users center the cube."""

    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    size = min(h, w) // 8

    over = frame.copy()
    cv2.rectangle(over, (cx - size, cy - size), (cx + size, cy + size), (0, 255, 255), 2)
    cv2.line(over, (cx - size, cy), (cx + size, cy), (0, 255, 255), 1)
    cv2.line(over, (cx, cy - size), (cx, cy + size), (0, 255, 255), 1)
    return over


def draw_instructions(frame: np.ndarray, expected_faces: Iterable[str], status_lines: Sequence[str] | None = None) -> np.ndarray:
    """Render scanner instructions and controls on the preview frame."""

    over = draw_guide_markers(frame)
    lines = [
        f"Show faces: {'/'.join(expected_faces)}",
        "SPACE: capture",
        "R: rescan",
        "Q: quit",
    ]
    if status_lines:
        lines.extend(status_lines)

    y = 30
    for line in lines:
        cv2.putText(over, line, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        y += 28

    return over
