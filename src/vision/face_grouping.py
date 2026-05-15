"""Group detected sticker candidates into three visible cube faces (Phase 3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence

import numpy as np

DetectedSticker = Any


@dataclass(frozen=True)
class FaceGroupingConfig:
    n_faces: int = 3
    expected_per_face: int = 9
    max_iterations: int = 50
    random_seed: int = 7


@dataclass(frozen=True)
class FaceGroup:
    stickers: tuple[DetectedSticker, ...]
    centroid: tuple[float, float]


def _kmeans(points: np.ndarray, k: int, max_iterations: int, random_seed: int) -> np.ndarray:
    rng = np.random.default_rng(random_seed)
    if len(points) < k:
        raise ValueError(f"Need at least {k} points for grouping, got {len(points)}")

    indices = rng.choice(len(points), size=k, replace=False)
    centers = points[indices].copy()

    labels = np.zeros(len(points), dtype=np.int32)
    for _ in range(max_iterations):
        distances = ((points[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_labels = np.argmin(distances, axis=1)

        if np.array_equal(new_labels, labels):
            break
        labels = new_labels

        for i in range(k):
            cluster_points = points[labels == i]
            if len(cluster_points) > 0:
                centers[i] = cluster_points.mean(axis=0)

    return labels


def group_stickers_into_faces(candidates: Sequence[DetectedSticker], config: FaceGroupingConfig | None = None) -> List[FaceGroup]:
    if config is None:
        config = FaceGroupingConfig()

    if len(candidates) < config.n_faces * config.expected_per_face:
        raise ValueError(
            f"Not enough candidates to form {config.n_faces} faces: "
            f"need {config.n_faces * config.expected_per_face}, got {len(candidates)}"
        )

    points = np.array([c.center for c in candidates], dtype=np.float32)
    labels = _kmeans(points, config.n_faces, config.max_iterations, config.random_seed)

    groups: List[FaceGroup] = []
    for cluster_id in range(config.n_faces):
        members = [candidates[i] for i in range(len(candidates)) if labels[i] == cluster_id]
        if len(members) != config.expected_per_face:
            raise ValueError(
                f"Cluster {cluster_id} has {len(members)} stickers; expected {config.expected_per_face}."
            )

        centroid_x = float(np.mean([m.center[0] for m in members]))
        centroid_y = float(np.mean([m.center[1] for m in members]))
        groups.append(FaceGroup(stickers=tuple(members), centroid=(centroid_x, centroid_y)))

    groups.sort(key=lambda g: (g.centroid[1], g.centroid[0]))
    return groups
