"""Validation helpers and shared data contracts for the vision scanning pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .types import FACE_ORDER, VALID_FACE_SET, ValidationResult


@dataclass(frozen=True)
class FaceScan:
    """Contract for one labeled face captured by vision."""

    face_label: str
    stickers: tuple[str, ...]


def validate_face_stickers(stickers: Sequence[str]) -> ValidationResult:
    if len(stickers) != 9:
        return ValidationResult(False, f"Face must contain 9 stickers, got {len(stickers)}")

    for sticker in stickers:
        if sticker not in VALID_FACE_SET:
            return ValidationResult(False, f"Invalid face symbol in stickers: {sticker}")

    return ValidationResult(True, "Face stickers are valid")


def validate_partial_scan(scan: Mapping[str, Sequence[str]], expected_faces: Sequence[str]) -> ValidationResult:
    missing = [face for face in expected_faces if face not in scan]
    if missing:
        return ValidationResult(False, f"Missing expected faces: {', '.join(missing)}")

    unexpected = [face for face in scan.keys() if face not in expected_faces]
    if unexpected:
        return ValidationResult(False, f"Unexpected faces in scan: {', '.join(unexpected)}")

    for face in expected_faces:
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

        if cube[face][4] != face:
            return ValidationResult(False, f"Center sticker mismatch on {face}: expected {face}, got {cube[face][4]}")

    all_symbols = "".join("".join(cube[face]) for face in FACE_ORDER)
    for face in FACE_ORDER:
        count = all_symbols.count(face)
        if count != 9:
            return ValidationResult(False, f"{face} appears {count} times (should be 9)")

    return ValidationResult(True, "Cube state is structurally valid")
