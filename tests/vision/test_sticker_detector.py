import sys
import os

import pytest
import numpy as np

cv2 = pytest.importorskip("cv2", reason="OpenCV runtime not available in test environment", exc_type=ImportError)

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from vision.sticker_detector import StickerDetectionConfig, find_sticker_candidates


def test_detects_square_candidate_in_synthetic_frame():
    frame = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 100), (180, 180), (0, 255, 0), -1)

    cfg = StickerDetectionConfig(min_area=100, max_area=30000, canny_low=30, canny_high=120)
    candidates = find_sticker_candidates(frame, cfg)

    assert len(candidates) >= 1

    best = max(candidates, key=lambda c: c.area)
    assert 120 <= best.center[0] <= 160
    assert 120 <= best.center[1] <= 160
    assert len(best.corners) == 4
    assert best.avg_hsv[1] > 20


def test_filters_small_noise_quads_by_area():
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.rectangle(frame, (10, 10), (16, 16), (255, 255, 255), -1)

    cfg = StickerDetectionConfig(min_area=200)
    candidates = find_sticker_candidates(frame, cfg)

    assert len(candidates) == 0
