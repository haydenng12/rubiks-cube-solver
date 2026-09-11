"""Manifest schema and validation for repeatable real-camera experiments."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = {
    "sample_id", "session_id", "scramble_id", "frame_path", "labels",
    "lighting", "distance", "angle", "glare", "background", "camera_id",
}


@dataclass(frozen=True)
class DatasetSummary:
    rows: int
    sessions: int
    scrambles: int
    missing_frames: int


def validate_manifest(path: str | Path, require_frames=True) -> DatasetSummary:
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Manifest missing columns: {sorted(missing)}")
        rows = list(reader)
    ids = [row["sample_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("sample_id values must be unique")
    for row in rows:
        if len(row["labels"]) != 54 or any(row["labels"].count(face) != 9 for face in "URFDLB"):
            raise ValueError(f"Invalid 54-sticker ground truth for {row['sample_id']}")
    missing_frames = sum(not (path.parent / row["frame_path"]).exists() for row in rows)
    if require_frames and missing_frames:
        raise ValueError(f"Manifest references {missing_frames} missing frames")
    return DatasetSummary(len(rows), len({r['session_id'] for r in rows}), len({r['scramble_id'] for r in rows}), missing_frames)


def assert_split_independence(train_rows, test_rows):
    train_groups = {(row["session_id"], row["scramble_id"]) for row in train_rows}
    test_groups = {(row["session_id"], row["scramble_id"]) for row in test_rows}
    overlap = train_groups & test_groups
    if overlap:
        raise ValueError(f"Train/test leakage in session-scramble groups: {sorted(overlap)}")
