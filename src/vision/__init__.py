"""Vision package: guided camera scanning pipeline."""

from .alignment import AlignmentConfig, FaceAlignment, score_face_alignment
from .face_geometry import FaceGeometry, FaceGeometryConfig, analyze_face_geometry, analyze_face_group
from .guide_layout import FaceGuide, GuideProfile, build_face_guides
from .scan_validation import FaceScan, validate_cube_state, validate_face_stickers, validate_partial_scan
from .types import FACE_ORDER, VALID_FACE_SET, ValidationResult
from .warp_sampling import SampledFace, SamplingConfig, StickerSample, sample_guided_face

__all__ = [
    "FACE_ORDER",
    "AlignmentConfig",
    "FaceAlignment",
    "VALID_FACE_SET",
    "FaceGeometry",
    "FaceGeometryConfig",
    "FaceGuide",
    "GuideProfile",
    "FaceScan",
    "ValidationResult",
    "SampledFace",
    "SamplingConfig",
    "StickerSample",
    "analyze_face_geometry",
    "analyze_face_group",
    "build_face_guides",
    "sample_guided_face",
    "score_face_alignment",
    "validate_cube_state",
    "validate_face_stickers",
    "validate_partial_scan",
]
