"""Runnable guided capture and 27-sticker sampling preview.

Run from the repository root:

    python -m src.vision.guided_preview
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

import cv2
import numpy as np

from .alignment import AlignmentConfig, FaceAlignment, all_faces_ready, score_face_alignment
from .camera import CameraError, close_camera, open_camera, read_frame
from .guide_layout import FaceGuide, build_face_guides
from .guided_overlay import draw_capture_review, draw_guided_alignment
from .warp_sampling import SampledFace, sample_guided_face


WINDOW_NAME = "Rubik's Cube Guided Capture"


@dataclass(frozen=True)
class GuidedCornerCapture:
    guides: tuple[FaceGuide, ...]
    sampled_faces: tuple[SampledFace, ...]
    alignments: tuple[FaceAlignment, ...]
    frame: np.ndarray = field(repr=False, compare=False)


def analyze_guided_frame(frame: np.ndarray) -> tuple[tuple[FaceGuide, ...], tuple[SampledFace, ...], tuple[FaceAlignment, ...]]:
    guides = build_face_guides(frame.shape)
    sampled_faces = tuple(sample_guided_face(frame, guide) for guide in guides)
    alignments = tuple(score_face_alignment(sampled) for sampled in sampled_faces)
    return guides, sampled_faces, alignments


def run_guided_preview(
    camera_index: int = 0,
    width: int = 1280,
    height: int = 720,
    mirror: bool = False,
) -> GuidedCornerCapture | None:
    """Guide, capture, review, and return one U/F/R corner observation."""

    config = AlignmentConfig()
    cap = open_camera(camera_index, width=width, height=height)
    stable_frames = 0
    review: GuidedCornerCapture | None = None

    try:
        while True:
            if review is None:
                frame = read_frame(cap)
                if mirror:
                    frame = cv2.flip(frame, 1)
                guides, sampled_faces, alignments = analyze_guided_frame(frame)
                if all_faces_ready(alignments, config):
                    stable_frames = min(stable_frames + 1, config.stable_frames_required)
                else:
                    stable_frames = 0

                preview = draw_guided_alignment(frame, guides, alignments, stable_frames, config)
                cv2.imshow(WINDOW_NAME, preview)
                key = cv2.waitKey(1) & 0xFF

                if key in (ord("q"), 27):
                    return None
                if key == ord(" "):
                    review = GuidedCornerCapture(guides, sampled_faces, alignments, frame.copy())
                continue

            preview = draw_capture_review(review.frame, review.guides, review.sampled_faces)
            cv2.imshow(WINDOW_NAME, preview)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):
                return None
            if key in (ord("r"), ord("R")):
                review = None
                stable_frames = 0
            elif key in (ord("a"), ord("A")):
                return review
    finally:
        close_camera(cap)
        cv2.destroyAllWindows()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guided Rubik's Cube corner capture preview.")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index.")
    parser.add_argument("--width", type=int, default=1280, help="Requested camera width.")
    parser.add_argument("--height", type=int, default=720, help="Requested camera height.")
    parser.add_argument("--mirror", action="store_true", help="Mirror the capture (diagnostic use only).")
    return parser.parse_args()


def _print_capture(capture: GuidedCornerCapture) -> None:
    print("Accepted guided corner capture:")
    for sampled, alignment in zip(capture.sampled_faces, capture.alignments):
        center = sampled.stickers[4]
        print(
            f"  {sampled.face} ({sampled.expected_color} center): "
            f"score={alignment.score:.3f}, center BGR={tuple(round(v, 1) for v in center.median_bgr)}"
        )


def main() -> int:
    args = _parse_args()
    try:
        capture = run_guided_preview(args.camera, args.width, args.height, args.mirror)
    except CameraError as exc:
        print(f"Camera error: {exc}")
        return 1
    if capture is None:
        print("Guided capture cancelled.")
        return 1
    _print_capture(capture)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
