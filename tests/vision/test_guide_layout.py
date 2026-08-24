import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from vision.guide_layout import build_face_guides


def test_guides_scale_and_share_cube_vertices():
    top, front, right = build_face_guides((720, 1280, 3))

    assert top.face == "U"
    assert front.face == "F"
    assert right.face == "R"
    assert top.corners[2] == front.corners[1] == right.corners[0]
    assert front.corners[2] == right.corners[3]
    assert top.corners[0] == (640.0, 100.8)


def test_guides_expose_expected_standard_centers():
    guides = build_face_guides((1000, 1000, 3))
    assert [(guide.face, guide.expected_color) for guide in guides] == [
        ("U", "white"),
        ("F", "green"),
        ("R", "red"),
    ]
