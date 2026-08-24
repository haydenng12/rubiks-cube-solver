"""Resolution-independent layout for guided three-face cube capture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

NormalizedPoint = tuple[float, float]
PixelPoint = tuple[float, float]


@dataclass(frozen=True)
class FaceGuide:
    face: str
    expected_color: str
    display_bgr: tuple[int, int, int]
    corners: tuple[PixelPoint, PixelPoint, PixelPoint, PixelPoint]


@dataclass(frozen=True)
class GuideProfile:
    name: str
    faces: tuple[str, str, str]
    expected_colors: Mapping[str, str]


STANDARD_FIRST_CORNER = GuideProfile(
    name="standard U/F/R corner",
    faces=("U", "F", "R"),
    expected_colors={"U": "white", "F": "green", "R": "red"},
)

COLOR_BGR: dict[str, tuple[int, int, int]] = {
    "white": (245, 245, 245),
    "yellow": (0, 230, 255),
    "green": (40, 190, 40),
    "blue": (230, 120, 30),
    "red": (40, 40, 230),
    "orange": (20, 130, 255),
}

# Corners are ordered top-left, top-right, bottom-right, bottom-left in each
# face's local coordinates. Shared vertices make one coherent cube corner.
_NORMALIZED_GUIDES: dict[str, tuple[NormalizedPoint, ...]] = {
    "U": ((0.50, 0.14), (0.74, 0.30), (0.50, 0.46), (0.26, 0.30)),
    "F": ((0.26, 0.30), (0.50, 0.46), (0.50, 0.78), (0.26, 0.62)),
    "R": ((0.50, 0.46), (0.74, 0.30), (0.74, 0.62), (0.50, 0.78)),
}


def build_face_guides(
    frame_shape: tuple[int, ...],
    profile: GuideProfile = STANDARD_FIRST_CORNER,
) -> tuple[FaceGuide, FaceGuide, FaceGuide]:
    """Scale the configured guide polygons to the current camera frame."""

    height, width = frame_shape[:2]
    guides = []
    for face in profile.faces:
        color_name = profile.expected_colors[face]
        normalized = _NORMALIZED_GUIDES[face]
        corners = (
            (normalized[0][0] * width, normalized[0][1] * height),
            (normalized[1][0] * width, normalized[1][1] * height),
            (normalized[2][0] * width, normalized[2][1] * height),
            (normalized[3][0] * width, normalized[3][1] * height),
        )
        guides.append(FaceGuide(face, color_name, COLOR_BGR[color_name], corners))
    return guides[0], guides[1], guides[2]


def interpolate_quad_point(corners: tuple[PixelPoint, ...], u: float, v: float) -> PixelPoint:
    """Bilinearly interpolate a display point inside a quadrilateral."""

    top_left, top_right, bottom_right, bottom_left = corners
    x = ((1-u)*(1-v)*top_left[0] + u*(1-v)*top_right[0] + u*v*bottom_right[0] + (1-u)*v*bottom_left[0])
    y = ((1-u)*(1-v)*top_left[1] + u*(1-v)*top_right[1] + u*v*bottom_right[1] + (1-u)*v*bottom_left[1])
    return float(x), float(y)
