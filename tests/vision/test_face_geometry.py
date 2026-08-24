import os
import sys
from dataclasses import dataclass

import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from vision.face_geometry import analyze_face_geometry


@dataclass(frozen=True)
class FakeSticker:
    label: int
    center: tuple[float, float]
    corners: tuple[tuple[float, float], ...]


def _perspective_face() -> list[FakeSticker]:
    source = np.array([[0, 0], [300, 0], [300, 300], [0, 300]], dtype=np.float32)
    destination = np.array([[120, 40], [360, 95], [325, 350], [55, 285]], dtype=np.float32)
    transform = cv2.getPerspectiveTransform(source, destination)

    stickers = []
    for row in range(3):
        for col in range(3):
            x0, y0 = col * 100 + 8, row * 100 + 8
            x1, y1 = (col + 1) * 100 - 8, (row + 1) * 100 - 8
            corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float32)
            center = np.array([[[col * 100 + 50, row * 100 + 50]]], dtype=np.float32)
            warped_corners = cv2.perspectiveTransform(corners.reshape(-1, 1, 2), transform).reshape(-1, 2)
            warped_center = cv2.perspectiveTransform(center, transform).reshape(2)
            stickers.append(
                FakeSticker(
                    label=row * 3 + col,
                    center=tuple(float(value) for value in warped_center),
                    corners=tuple(tuple(float(value) for value in point) for point in warped_corners),
                )
            )
    return stickers


def test_orders_a_perspective_face_in_row_major_order():
    stickers = _perspective_face()
    shuffled = [stickers[index] for index in (7, 2, 4, 0, 8, 1, 6, 3, 5)]

    geometry = analyze_face_geometry(shuffled)

    assert [sticker.label for sticker in geometry.ordered_stickers] == list(range(9))
    assert geometry.cell_error < 0.08
    assert len(geometry.outer_corners) == 4


def test_rejects_the_wrong_number_of_stickers():
    try:
        analyze_face_geometry(_perspective_face()[:8])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Expected 9 stickers" in str(exc)


def test_rejects_duplicate_centers():
    stickers = _perspective_face()
    stickers[-1] = FakeSticker(
        label=8,
        center=stickers[0].center,
        corners=stickers[-1].corners,
    )

    try:
        analyze_face_geometry(stickers)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "centers must be unique" in str(exc)
