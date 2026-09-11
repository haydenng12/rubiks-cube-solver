"""Convert sampled physical colors into canonical solver face symbols."""

from __future__ import annotations

from typing import Mapping, Sequence


def label_colors_by_centers(color_ids: Sequence[int], center_positions: Mapping[str, int]) -> tuple[str, ...]:
    cluster_to_face = {color_ids[position]: face for face, position in center_positions.items()}
    if len(cluster_to_face) != 6:
        raise ValueError("The six centers must identify six distinct color classes")
    try:
        return tuple(cluster_to_face[color] for color in color_ids)
    except KeyError as exc:
        raise ValueError(f"Sticker uses an unknown color class: {exc.args[0]}") from exc
