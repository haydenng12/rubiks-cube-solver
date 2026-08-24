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
    assert top.corners[0] == (640.0, 129.6)

    all_points = [point for guide in (top, front, right) for point in guide.corners]
    guide_width = max(point[0] for point in all_points) - min(point[0] for point in all_points)
    guide_height = max(point[1] for point in all_points) - min(point[1] for point in all_points)
    assert round(guide_width, 5) == round(guide_height, 5)


def test_guides_expose_expected_standard_centers():
    guides = build_face_guides((1000, 1000, 3))
    assert [(guide.face, guide.expected_color) for guide in guides] == [
        ("U", "white"),
        ("F", "green"),
        ("R", "red"),
    ]


def test_widescreen_frame_does_not_stretch_guides_horizontally():
    guides = build_face_guides((720, 1920, 3))
    all_points = [point for guide in guides for point in guide.corners]

    assert min(point[0] for point in all_points) > 700
    assert max(point[0] for point in all_points) < 1220
    assert min(point[1] for point in all_points) > 100
    assert max(point[1] for point in all_points) < 620
