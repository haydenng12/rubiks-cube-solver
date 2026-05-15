"""Camera lifecycle and preview utilities for guided cube scanning."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np


class CameraError(RuntimeError):
    """Raised when the camera cannot be opened or read."""


def open_camera(camera_index: int = 0, width: Optional[int] = None, height: Optional[int] = None) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise CameraError(f"Unable to open camera index {camera_index}")

    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


def read_frame(cap: cv2.VideoCapture) -> np.ndarray:
    ok, frame = cap.read()
    if not ok or frame is None:
        raise CameraError("Failed to read frame from camera")
    return frame


def close_camera(cap: cv2.VideoCapture) -> None:
    cap.release()
