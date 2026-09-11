"""Vision package: guided camera scanning pipeline."""

from .alignment import AlignmentConfig, FaceAlignment, score_face_alignment
from .face_geometry import FaceGeometry, FaceGeometryConfig, analyze_face_geometry, analyze_face_group
from .guide_layout import FaceGuide, GuideProfile, STANDARD_FIRST_CORNER, STANDARD_SECOND_CORNER, build_face_guides
from .color_model import ClassificationResult, classify_balanced, classify_independent
from .reconstruction import ReconstructionResult, reconstruct
from .scan_validation import FaceScan, validate_cube_state, validate_face_stickers, validate_partial_scan
from .types import FACE_ORDER, VALID_FACE_SET, ValidationResult
from .warp_sampling import SampledFace, SamplingConfig, StickerSample, sample_guided_face

__all__ = [
    "FACE_ORDER",
    "AlignmentConfig",
    "ClassificationResult",
    "FaceAlignment",
    "VALID_FACE_SET",
    "FaceGeometry",
    "FaceGeometryConfig",
    "FaceGuide",
    "GuideProfile",
    "STANDARD_FIRST_CORNER",
    "STANDARD_SECOND_CORNER",
    "FaceScan",
    "ValidationResult",
    "ReconstructionResult",
    "SampledFace",
    "SamplingConfig",
    "StickerSample",
    "analyze_face_geometry",
    "analyze_face_group",
    "build_face_guides",
    "classify_balanced",
    "classify_independent",
    "reconstruct",
    "sample_guided_face",
    "score_face_alignment",
    "validate_cube_state",
    "validate_face_stickers",
    "validate_partial_scan",
]
