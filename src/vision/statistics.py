"""Cluster-aware bootstrap summaries for experimental results."""

from __future__ import annotations

from collections import defaultdict
import numpy as np


def cluster_bootstrap_mean(values, clusters, iterations=2000, seed=20260910):
    values = np.asarray(values, dtype=float)
    clusters = np.asarray(clusters)
    if len(values) != len(clusters) or not len(values):
        raise ValueError("Values and clusters must be non-empty and equally sized")
    grouped = defaultdict(list)
    for value, cluster in zip(values, clusters):
        grouped[cluster].append(float(value))
    keys = list(grouped)
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(iterations):
        selected = rng.choice(keys, size=len(keys), replace=True)
        sample = [value for key in selected for value in grouped[key]]
        estimates.append(float(np.mean(sample)))
    low, high = np.percentile(estimates, (2.5, 97.5))
    return {"mean": float(np.mean(values)), "ci95_low": float(low), "ci95_high": float(high)}


def paired_cluster_bootstrap_difference(a, b, clusters, iterations=2000, seed=20260910):
    if len(a) != len(b):
        raise ValueError("Paired methods must contain the same observations")
    return cluster_bootstrap_mean(np.asarray(a) - np.asarray(b), clusters, iterations, seed)
