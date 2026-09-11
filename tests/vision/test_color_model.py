import numpy as np

from vision.color_model import COLOR_ORDER, classify_balanced, classify_independent


PROTOTYPES = {
    "U": (245, 245, 245), "R": (30, 30, 220), "F": (30, 180, 30),
    "D": (0, 220, 240), "L": (20, 120, 245), "B": (220, 100, 20),
}


def test_independent_lab_recovers_prototypes():
    result = classify_independent([PROTOTYPES[label] for label in COLOR_ORDER], PROTOTYPES)
    assert result.labels == COLOR_ORDER


def test_balanced_assignment_enforces_nine_of_each_color():
    samples = [PROTOTYPES[label] for label in COLOR_ORDER for _ in range(9)]
    result = classify_balanced(samples, PROTOTYPES)
    assert all(result.labels.count(label) == 9 for label in COLOR_ORDER)
    assert np.asarray(result.costs).shape == (54, 6)
