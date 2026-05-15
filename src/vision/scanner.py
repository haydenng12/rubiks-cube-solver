"""High-level scan orchestration for guided two-corner capture.

Phase 3 note: grouping implementation is in face_grouping.py; this module keeps
orchestration and scan fusion responsibilities.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from .camera import CameraError, close_camera, open_camera, read_frame
from .scan_validation import validate_cube_state, validate_partial_scan
from .types import CaptureFn, CubeState, PartialScan
from .ui_overlay import draw_instructions


class ScanError(RuntimeError):
    """Raised when scan capture, shape checks, or fusion fails."""


def _normalize_scan(scan: Mapping[str, Sequence[str]]) -> PartialScan:
    return {face: list(stickers) for face, stickers in scan.items()}


def preview_until_capture(expected_faces: Sequence[str], window_name: str = "Cube Scanner", camera_index: int = 0):
    import cv2

    cap = open_camera(camera_index)
    try:
        while True:
            frame = read_frame(cap)
            overlay = draw_instructions(frame, expected_faces)
            cv2.imshow(window_name, overlay)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):
                return "capture", frame
            if key in (ord("r"), ord("R")):
                return "rescan", frame
            if key in (ord("q"), ord("Q")):
                return "quit", frame
    finally:
        close_camera(cap)
        cv2.destroyWindow(window_name)


def combine_scans(first_scan: Mapping[str, Sequence[str]], second_scan: Mapping[str, Sequence[str]]) -> CubeState:
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


def scan_corner_view(capture_fn: CaptureFn, expected_faces: Sequence[str]) -> PartialScan:
    raw_scan = capture_fn(expected_faces)
    result = validate_partial_scan(raw_scan, expected_faces)
    if not result.valid:
        raise ScanError(f"Corner scan invalid: {result.message}")
    return _normalize_scan(raw_scan)


def scan_cube(capture_fn: CaptureFn) -> CubeState:
    first_scan = scan_corner_view(capture_fn, ("U", "F", "R"))
    second_scan = scan_corner_view(capture_fn, ("D", "B", "L"))
    return combine_scans(first_scan, second_scan)


def scan_cube_with_preview(capture_fn: CaptureFn, camera_index: int = 0) -> CubeState:
    for expected in (("U", "F", "R"), ("D", "B", "L")):
        try:
            action, _ = preview_until_capture(expected, camera_index=camera_index)
        except CameraError as exc:
            raise ScanError(str(exc)) from exc

        if action == "quit":
            raise ScanError("Scan cancelled by user")

    return scan_cube(capture_fn)
