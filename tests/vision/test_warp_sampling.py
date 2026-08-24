import os
import sys

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from vision.alignment import AlignmentConfig, all_faces_ready, score_face_alignment
from vision.warp_sampling import sample_warped_face


COLORS = [
    (20, 30, 220), (30, 190, 30), (220, 100, 20),
    (0, 220, 250), (235, 235, 235), (20, 110, 245),
    (80, 40, 180), (170, 170, 40), (40, 180, 180),
]


def _synthetic_face(with_grid=True):
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    for row in range(3):
        for col in range(3):
            margin = 8 if with_grid else 0
            image[row*100+margin:(row+1)*100-margin, col*100+margin:(col+1)*100-margin] = COLORS[row*3+col]
    return image


def test_samples_nine_cell_interiors_in_row_major_order():
    sampled = sample_warped_face(_synthetic_face(), "F", "green")

    assert len(sampled.stickers) == 9
    assert [(item.row, item.col) for item in sampled.stickers] == [
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2),
    ]
    assert sampled.stickers[0].median_bgr == (
        float(COLORS[0][0]),
        float(COLORS[0][1]),
        float(COLORS[0][2]),
    )


def test_dark_grid_scores_better_than_a_uniform_region():
    patterned = sample_warped_face(_synthetic_face(), "F", "green")
    uniform_image = np.full((300, 300, 3), (90, 150, 90), dtype=np.uint8)
    uniform = sample_warped_face(uniform_image, "F", "green")

    patterned_score = score_face_alignment(patterned)
    uniform_score = score_face_alignment(uniform)

    assert patterned_score.score > uniform_score.score
    assert not all_faces_ready((uniform_score, uniform_score, uniform_score), AlignmentConfig())
