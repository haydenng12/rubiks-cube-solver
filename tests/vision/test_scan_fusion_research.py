import pytest

from vision.scan_fusion import CaptureTransform, fuse_views, rotate_face


def test_four_face_rotations_restore_original():
    face = list("123456789")
    assert rotate_face(face, 4) == face


def test_fusion_requires_all_six_unique_faces():
    face = list("UUUUUUUUU")
    with pytest.raises(ValueError):
        fuse_views({"U": face}, {"U": face})


def test_fusion_applies_explicit_transform():
    observed = {
        "U": list("123456789"), "F": list("FFFFFFFFF"), "R": list("RRRRRRRRR"),
        "D": list("DDDDDDDDD"), "B": list("BBBBBBBBB"), "L": list("LLLLLLLLL"),
    }
    transforms = {face: CaptureTransform(face, 0) for face in observed}
    transforms["U"] = CaptureTransform("U", 1)
    result = fuse_views({k: observed[k] for k in ("U", "F", "R")},
                        {k: observed[k] for k in ("D", "B", "L")}, transforms)
    assert result["U"] == list("741852963")
