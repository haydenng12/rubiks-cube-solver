"""High-level scan orchestration for guided two-corner capture.

Phase 0 delivers contracts and orchestration scaffolding, not camera/CV logic.
Concrete detection components will be injected in later phases.
"""

from typing import Callable, Dict, Iterable, Mapping, Sequence

from .scan_validation import ValidationResult, validate_cube_state, validate_partial_scan

PartialScan = Dict[str, list[str]]
CubeState = Dict[str, list[str]]
CaptureFn = Callable[[Iterable[str]], Mapping[str, Sequence[str]]]


class ScanError(RuntimeError):
    """Raised when scan capture, shape checks, or fusion fails."""


def _normalize_scan(scan: Mapping[str, Sequence[str]]) -> PartialScan:
    """Copy a scan mapping into mutable list-based cube face arrays."""

    normalized: PartialScan = {}
    for face, stickers in scan.items():
        normalized[face] = list(stickers)
    return normalized


def combine_scans(first_scan: Mapping[str, Sequence[str]], second_scan: Mapping[str, Sequence[str]]) -> CubeState:
    """Merge first and second guided corner scans into one cube dictionary.

    first_scan is expected to contain U/F/R faces.
    second_scan is expected to contain D/B/L faces.
    """

    first_expected = ("U", "F", "R")
    second_expected = ("D", "B", "L")

    first_result = validate_partial_scan(first_scan, first_expected)
    if not first_result.valid:
        raise ScanError(f"First scan invalid: {first_result.message}")

    second_result = validate_partial_scan(second_scan, second_expected)
    if not second_result.valid:
        raise ScanError(f"Second scan invalid: {second_result.message}")

    cube: CubeState = {}
    cube.update(_normalize_scan(first_scan))
    cube.update(_normalize_scan(second_scan))

    cube_result = validate_cube_state(cube)
    if not cube_result.valid:
        raise ScanError(f"Combined cube invalid: {cube_result.message}")

    return cube


def scan_corner_view(capture_fn: CaptureFn, expected_faces: Iterable[str]) -> PartialScan:
    """Capture one guided corner using an injected capture function.

    `capture_fn` is a boundary that later phases will implement with camera,
    sticker detection, grouping, warping, and color modeling.
    """

    raw_scan = capture_fn(expected_faces)
    result = validate_partial_scan(raw_scan, expected_faces)
    if not result.valid:
        raise ScanError(f"Corner scan invalid: {result.message}")

    return _normalize_scan(raw_scan)


def scan_cube(capture_fn: CaptureFn) -> CubeState:
    """Guided two-corner scan orchestration entrypoint.

    This function is the future integration point for camera mode in main.py.
    """

    first_scan = scan_corner_view(capture_fn, ("U", "F", "R"))
    second_scan = scan_corner_view(capture_fn, ("D", "B", "L"))

    return combine_scans(first_scan, second_scan)
