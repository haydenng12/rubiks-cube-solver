import sys
import os
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from vision.face_grouping import FaceGroupingConfig, group_stickers_into_faces


@dataclass(frozen=True)
class FakeSticker:
    center: tuple[int, int]


def _make_candidate(x: int, y: int) -> FakeSticker:
    return FakeSticker(center=(x, y))


def test_group_stickers_into_three_faces_of_nine():
    candidates = []
    for base_x, base_y in ((50, 50), (200, 60), (120, 220)):
        for dx in (0, 20, 40):
            for dy in (0, 20, 40):
                candidates.append(_make_candidate(base_x + dx, base_y + dy))

    groups = group_stickers_into_faces(candidates, FaceGroupingConfig(random_seed=1))

    assert len(groups) == 3
    assert all(len(g.stickers) == 9 for g in groups)


def test_grouping_rejects_insufficient_candidates():
    candidates = [_make_candidate(10 + i, 10 + i) for i in range(10)]

    try:
        group_stickers_into_faces(candidates)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Not enough candidates" in str(exc)
