import numpy as np

from vision.temporal import aggregate_bgr


def test_temporal_median_rejects_one_outlier_frame():
    frames = np.zeros((3, 54, 3), dtype=float)
    frames[2] = 255
    assert np.all(aggregate_bgr(frames, "median") == 0)
