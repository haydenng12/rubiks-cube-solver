"""Interactive two-view acquisition and calibrated cube reconstruction."""

from __future__ import annotations

import argparse

from .guide_layout import STANDARD_FIRST_CORNER, STANDARD_SECOND_CORNER
from .guided_preview import run_guided_preview
from .reconstruction import reconstruct


def main(argv=None):
    parser = argparse.ArgumentParser(description="Capture both guided cube corners")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--independent", action="store_true", help="Disable nine-per-color assignment")
    args = parser.parse_args(argv)
    print("View 1: hold WHITE on top, GREEN front-left, RED right.")
    first = run_guided_preview(camera_index=args.camera, profile=STANDARD_FIRST_CORNER)
    if first is None:
        return 1
    print("View 2: rotate to the opposite corner: YELLOW top, BLUE front-left, ORANGE right.")
    second = run_guided_preview(camera_index=args.camera, profile=STANDARD_SECOND_CORNER)
    if second is None:
        return 1
    result = reconstruct(first.sampled_faces, second.sampled_faces, balanced=not args.independent)
    print(f"Reconstructed state: {result.cube_string}")
    print(f"Validation: {result.validation_message}")
    low = sorted(enumerate(result.classification.confidence), key=lambda pair: pair[1])[:5]
    print("Lowest-confidence sticker positions:", low)
    return 0 if result.structurally_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
