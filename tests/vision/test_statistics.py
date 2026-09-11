from vision.statistics import cluster_bootstrap_mean, paired_cluster_bootstrap_difference


def test_bootstrap_is_deterministic_and_contains_observed_mean():
    result = cluster_bootstrap_mean([0, 1, 1, 0], ["a", "a", "b", "b"], iterations=100)
    assert result["mean"] == 0.5
    assert result["ci95_low"] <= result["mean"] <= result["ci95_high"]


def test_paired_identical_methods_have_zero_difference():
    result = paired_cluster_bootstrap_difference([1, 0], [1, 0], ["a", "b"], iterations=20)
    assert result == {"mean": 0.0, "ci95_low": 0.0, "ci95_high": 0.0}
