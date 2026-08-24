"""Live camera diagnostic for the early computer-vision pipeline.

Run from the repository root with::

    python -m src.vision.diagnostic_preview

This intentionally stops after sticker detection, face grouping, and 3 x 3
geometry recovery.  It is a development tool, not a complete cube scanner.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence

import cv2
import numpy as np

from .camera import CameraError, close_camera, open_camera, read_frame
from .face_geometry import FaceGeometry, analyze_face_group
from .face_grouping import FaceGroup, group_stickers_into_faces
from .sticker_detector import DetectedSticker, find_sticker_candidates


WINDOW_NAME = "Rubik's Cube Vision Diagnostic"
FACE_COLORS = ((80, 220, 80), (255, 140, 40), (210, 80, 230))


@dataclass(frozen=True)
class DiagnosticResult:
    candidates: tuple[DetectedSticker, ...]
    groups: tuple[FaceGroup, ...] = ()
    geometries: tuple[FaceGeometry, ...] = ()
    error: str | None = None

    @property
    def valid(self) -> bool:
        return len(self.candidates) == 27 and len(self.geometries) == 3 and self.error is None


def analyze_diagnostic_frame(frame: np.ndarray) -> DiagnosticResult:
    """Run the implemented vision stages without allowing errors to end preview."""

    candidates = tuple(find_sticker_candidates(frame))
    if len(candidates) != 27:
        return DiagnosticResult(
            candidates=candidates,
            error=f"Need exactly 27 sticker candidates; detected {len(candidates)}.",
        )

    try:
        groups = tuple(group_stickers_into_faces(candidates))
        geometries = tuple(analyze_face_group(group) for group in groups)
    except (ValueError, cv2.error) as exc:
        return DiagnosticResult(candidates=candidates, error=str(exc))

    return DiagnosticResult(candidates=candidates, groups=groups, geometries=geometries)


def _as_int_contour(points: Sequence[Sequence[float]]) -> np.ndarray:
    return np.asarray(points, dtype=np.int32).reshape(-1, 1, 2)


def _draw_text(frame: np.ndarray, text: str, origin: tuple[int, int], color: tuple[int, int, int]) -> None:
    cv2.putText(frame, text, origin, cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(frame, text, origin, cv2.FONT_HERSHEY_SIMPLEX, 0.58, color, 2, cv2.LINE_AA)


def draw_diagnostic_overlay(frame: np.ndarray, result: DiagnosticResult, frozen: bool = False) -> np.ndarray:
    """Draw candidate polygons, grouped grids, indices, and status information."""

    overlay = frame.copy()

    # Yellow means the contour detector accepted a sticker but the candidate
    # has not necessarily survived grouping and grid validation.
    for candidate in result.candidates:
        cv2.polylines(overlay, [_as_int_contour(candidate.corners)], True, (0, 220, 255), 1)

    for group_index, geometry in enumerate(result.geometries):
        color = FACE_COLORS[group_index % len(FACE_COLORS)]
        cv2.polylines(overlay, [_as_int_contour(geometry.outer_corners)], True, color, 3)
        for cell_index, sticker in enumerate(geometry.ordered_stickers):
            cv2.polylines(overlay, [_as_int_contour(sticker.corners)], True, color, 2)
            x, y = sticker.center
            cv2.circle(overlay, (int(x), int(y)), 3, color, -1)
            _draw_text(overlay, str(cell_index), (int(x) + 5, int(y) - 5), color)

    panel_height = 112 + 24 * len(result.geometries)
    cv2.rectangle(overlay, (8, 8), (min(overlay.shape[1] - 8, 610), panel_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.84, frame, 0.16, 0, overlay)

    state = "VALID 3-FACE GRID" if result.valid else "ADJUST CUBE"
    state_color = (80, 240, 80) if result.valid else (80, 180, 255)
    _draw_text(overlay, f"Status: {state}", (20, 34), state_color)
    _draw_text(overlay, f"Candidates: {len(result.candidates)}/27", (20, 60), (255, 255, 255))

    if result.error:
        message = result.error if len(result.error) <= 82 else result.error[:79] + "..."
        _draw_text(overlay, message, (20, 86), state_color)
    else:
        _draw_text(overlay, "Faces: 3/3", (20, 86), (255, 255, 255))

    for index, geometry in enumerate(result.geometries):
        _draw_text(
            overlay,
            f"Face {index + 1} geometry error: {geometry.cell_error:.3f}",
            (20, 112 + index * 24),
            FACE_COLORS[index % len(FACE_COLORS)],
        )

    controls = "SPACE: freeze/resume   Q or ESC: quit"
    if frozen:
        controls = "FROZEN   " + controls
    _draw_text(overlay, controls, (20, overlay.shape[0] - 20), (255, 255, 255))
    return overlay


def run_diagnostic_preview(
    camera_index: int = 0,
    width: int | None = 1280,
    height: int | None = 720,
    mirror: bool = True,
) -> None:
    """Open the webcam and display live diagnostics until the user quits."""

    cap = open_camera(camera_index, width=width, height=height)
    frozen = False
    frozen_frame: np.ndarray | None = None

    try:
        while True:
            if not frozen or frozen_frame is None:
                frame = read_frame(cap)
                if mirror:
                    frame = cv2.flip(frame, 1)
                frozen_frame = frame

            result = analyze_diagnostic_frame(frozen_frame)
            preview = draw_diagnostic_overlay(frozen_frame, result, frozen=frozen)
            cv2.imshow(WINDOW_NAME, preview)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord(" "):
                frozen = not frozen
    finally:
        close_camera(cap)
        cv2.destroyAllWindows()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview Rubik's Cube sticker and face detection.")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0).")
    parser.add_argument("--width", type=int, default=1280, help="Requested frame width.")
    parser.add_argument("--height", type=int, default=720, help="Requested frame height.")
    parser.add_argument("--no-mirror", action="store_true", help="Do not mirror the webcam preview.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        run_diagnostic_preview(
            camera_index=args.camera,
            width=args.width,
            height=args.height,
            mirror=not args.no_mirror,
        )
    except CameraError as exc:
        print(f"Camera error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
