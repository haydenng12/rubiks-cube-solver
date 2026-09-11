"""End-to-end reconstruction from two guided SampledFace collections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .color_model import ClassificationResult, classify_balanced, classify_independent
from .scan_fusion import CaptureTransform, fuse_views
from .warp_sampling import SampledFace

FACE_ORDER = ("U", "R", "F", "D", "L", "B")


@dataclass(frozen=True)
class ReconstructionResult:
    cube: dict[str, list[str]]
    cube_string: str
    classification: ClassificationResult
    structurally_valid: bool
    validation_message: str


def _face_map(faces: Iterable[SampledFace]) -> dict[str, SampledFace]:
    result = {face.face: face for face in faces}
    if len(result) != 6 or set(result) != set(FACE_ORDER):
        raise ValueError("Reconstruction requires exactly one observation of every face")
    return result


def reconstruct(
    first_faces: Iterable[SampledFace],
    second_faces: Iterable[SampledFace],
    balanced=True,
    transforms: Mapping[str, CaptureTransform] | None = None,
) -> ReconstructionResult:
    faces = _face_map((*tuple(first_faces), *tuple(second_faces)))
    samples = [sample.median_bgr for face in FACE_ORDER for sample in faces[face].stickers]
    prototypes = {face: faces[face].stickers[4].median_bgr for face in FACE_ORDER}
    classification = (classify_balanced if balanced else classify_independent)(samples, prototypes)
    classified = {face: list(classification.labels[i * 9:(i + 1) * 9]) for i, face in enumerate(FACE_ORDER)}
    cube = fuse_views(
        {face: classified[face] for face in ("U", "F", "R")},
        {face: classified[face] for face in ("D", "B", "L")},
        transforms,
    )
    cube_string = "".join("".join(cube[face]) for face in FACE_ORDER)
    from validation import validate_cube_string
    valid, message = validate_cube_string(cube_string)
    return ReconstructionResult(cube, cube_string, classification, valid, message)
