import os
import sys
from unittest.mock import patch

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from vision.diagnostic_preview import analyze_diagnostic_frame


def test_analysis_reports_candidate_count_before_grouping():
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    candidates = [object() for _ in range(12)]

    with patch("vision.diagnostic_preview.find_sticker_candidates", return_value=candidates), patch(
        "vision.diagnostic_preview.group_stickers_into_faces"
    ) as grouping:
        result = analyze_diagnostic_frame(frame)

    assert not result.valid
    assert "detected 12" in (result.error or "")
    grouping.assert_not_called()


def test_analysis_preserves_geometry_failure_as_status():
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    candidates = [object() for _ in range(27)]

    with patch("vision.diagnostic_preview.find_sticker_candidates", return_value=candidates), patch(
        "vision.diagnostic_preview.group_stickers_into_faces", side_effect=ValueError("bad grouping")
    ):
        result = analyze_diagnostic_frame(frame)

    assert not result.valid
    assert result.error == "bad grouping"
