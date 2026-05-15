"""Validation helpers and shared data contracts for the vision scanning pipeline.

Phase 0 intentionally focuses on data shape guarantees only. These validators
are used by the scanner orchestration layer before any solve attempt.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence

FACE_ORDER = ("U", "R", "F", "D", "L", "B")
VALID_FACE_SET = set(FACE_ORDER)


@dataclass(frozen=True)
class ValidationResult:
    """Result object used by scan validators.

    Attributes:
        valid: Whether the checked object satisfies the contract.
        message: Human-readable reason for pass/failure.
    """

    valid: bool
    message: str


@dataclass(frozen=True)
class StickerCandidate:
    """Minimal geometry/color contract for a detected sticker candidate."""

    center_x: float
    center_y: float
    area: float
    avg_h: float
    avg_s: float
    avg_v: float


@dataclass(frozen=True)
class FaceScan:
    """Contract for one labeled face captured by vision.

    stickers is expected to be length-9 in row-major order.
    """

    face_label: str
    stickers: tuple[str, ...]


CubeState = Dict[str, list[str]]


def validate_face_stickers(stickers: Sequence[str]) -> ValidationResult:
    if len(stickers) != 9:
        return ValidationResult(False, f"Face must contain 9 stickers, got {len(stickers)}")

    for sticker in stickers:
        if sticker not in VALID_FACE_SET:
            return ValidationResult(False, f"Invalid face symbol in stickers: {sticker}")

    return ValidationResult(True, "Face stickers are valid")


def validate_partial_scan(scan: Mapping[str, Sequence[str]], expected_faces: Iterable[str]) -> ValidationResult:
    expected = list(expected_faces)

    missing = [face for face in expected if face not in scan]
    if missing:
        return ValidationResult(False, f"Missing expected faces: {', '.join(missing)}")

    unexpected = [face for face in scan.keys() if face not in expected]
    if unexpected:
        return ValidationResult(False, f"Unexpected faces in scan: {', '.join(unexpected)}")

    for face in expected:
        result = validate_face_stickers(scan[face])
        if not result.valid:
            return ValidationResult(False, f"Face {face} invalid: {result.message}")

    return ValidationResult(True, "Partial scan is valid")


def validate_cube_state(cube: Mapping[str, Sequence[str]]) -> ValidationResult:
    missing = [face for face in FACE_ORDER if face not in cube]
    if missing:
        return ValidationResult(False, f"Cube state missing faces: {', '.join(missing)}")

    for face in FACE_ORDER:
        result = validate_face_stickers(cube[face])
        if not result.valid:
            return ValidationResult(False, f"Face {face} invalid: {result.message}")

    all_symbols = "".join("".join(cube[face]) for face in FACE_ORDER)
    for face in FACE_ORDER:
        count = all_symbols.count(face)
        if count != 9:
            return ValidationResult(False, f"{face} appears {count} times (should be 9)")

    return ValidationResult(True, "Cube state is structurally valid")
