"""Orientation-explicit fusion of two guided three-face observations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

FACE_ORDER = ("U", "R", "F", "D", "L", "B")


def rotate_face(stickers: Sequence[str], quarter_turns: int) -> list[str]:
    if len(stickers) != 9:
        raise ValueError("A face must have nine stickers")
    values = list(stickers)
    for _ in range(quarter_turns % 4):
        values = [values[6], values[3], values[0], values[7], values[4], values[1], values[8], values[5], values[2]]
    return values


@dataclass(frozen=True)
class CaptureTransform:
    face: str
    quarter_turns: int = 0


def fuse_views(
    first: Mapping[str, Sequence[str]],
    second: Mapping[str, Sequence[str]],
    transforms: Mapping[str, CaptureTransform] | None = None,
) -> dict[str, list[str]]:
    if set(first) & set(second):
        raise ValueError("Capture views must not contain duplicate faces")
    observed = dict(first)
    observed.update(second)
    if set(observed) != set(FACE_ORDER):
        raise ValueError(f"Expected faces {FACE_ORDER}; received {tuple(observed)}")
    transforms = transforms or {face: CaptureTransform(face) for face in FACE_ORDER}
    result = {}
    for face in FACE_ORDER:
        transform = transforms[face]
        if transform.face != face:
            raise ValueError(f"Transform key {face} targets {transform.face}")
        result[face] = rotate_face(observed[face], transform.quarter_turns)
    return result
