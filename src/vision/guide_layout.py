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

STANDARD_SECOND_CORNER = GuideProfile(
    name="standard D/B/L corner",
    faces=("D", "B", "L"),
    expected_colors={"D": "yellow", "B": "blue", "L": "orange"},
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
    "U": ((0.50, 0.18), (0.82, 0.34), (0.50, 0.50), (0.18, 0.34)),
    "F": ((0.18, 0.34), (0.50, 0.50), (0.50, 0.82), (0.18, 0.66)),
    "R": ((0.50, 0.50), (0.82, 0.34), (0.82, 0.66), (0.50, 0.82)),
    "D": ((0.50, 0.18), (0.82, 0.34), (0.50, 0.50), (0.18, 0.34)),
    "B": ((0.18, 0.34), (0.50, 0.50), (0.50, 0.82), (0.18, 0.66)),
    "L": ((0.50, 0.50), (0.82, 0.34), (0.82, 0.66), (0.50, 0.82)),
}


def build_face_guides(
    frame_shape: tuple[int, ...],
    profile: GuideProfile = STANDARD_FIRST_CORNER,
) -> tuple[FaceGuide, FaceGuide, FaceGuide]:
    """Scale guides inside a centered square viewport without distortion."""

    height, width = frame_shape[:2]
    viewport_size = float(min(width, height))
    offset_x = (width - viewport_size) / 2.0
    offset_y = (height - viewport_size) / 2.0

    def project(point: NormalizedPoint) -> PixelPoint:
        return (
            offset_x + point[0] * viewport_size,
            offset_y + point[1] * viewport_size,
        )

    guides = []
    for face in profile.faces:
        color_name = profile.expected_colors[face]
        normalized = _NORMALIZED_GUIDES[face]
        corners = (
            project(normalized[0]),
            project(normalized[1]),
            project(normalized[2]),
            project(normalized[3]),
        )
        guides.append(FaceGuide(face, color_name, COLOR_BGR[color_name], corners))
    return guides[0], guides[1], guides[2]


def interpolate_quad_point(corners: tuple[PixelPoint, ...], u: float, v: float) -> PixelPoint:
    """Bilinearly interpolate a display point inside a quadrilateral."""

    top_left, top_right, bottom_right, bottom_left = corners
    x = ((1-u)*(1-v)*top_left[0] + u*(1-v)*top_right[0] + u*v*bottom_right[0] + (1-u)*v*bottom_left[0])
    y = ((1-u)*(1-v)*top_left[1] + u*(1-v)*top_right[1] + u*v*bottom_right[1] + (1-u)*v*bottom_left[1])
    return float(x), float(y)
