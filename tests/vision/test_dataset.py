import csv

import pytest

from vision.dataset import REQUIRED_COLUMNS, assert_split_independence, validate_manifest


def test_manifest_can_be_validated_without_real_frames(tmp_path):
    path = tmp_path / "manifest.csv"
    row = {column: "x" for column in REQUIRED_COLUMNS}
    row.update(sample_id="one", session_id="s1", scramble_id="q1",
               frame_path="missing.png", labels="".join(face * 9 for face in "URFDLB"))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(REQUIRED_COLUMNS))
        writer.writeheader(); writer.writerow(row)
    summary = validate_manifest(path, require_frames=False)
    assert summary.rows == 1 and summary.missing_frames == 1


def test_split_leakage_is_rejected():
    row = {"session_id": "same", "scramble_id": "same"}
    with pytest.raises(ValueError):
        assert_split_independence([row], [row])
