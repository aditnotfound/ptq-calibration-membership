from __future__ import annotations

import numpy as np

from calibtrace.attack import _shadow_normalize, make_population_design
from calibtrace.data import CIFAR100Dataset


def test_population_is_balanced_and_provenance_safe() -> None:
    labels = np.repeat(np.arange(100, dtype=np.int64), 10)
    images = np.zeros((len(labels), 3, 1, 1), dtype=np.uint8)
    calibration = CIFAR100Dataset(images, labels, augment=False)
    design = make_population_design(
        calibration,
        calibration_size=128,
        targets=64,
        shadow_artifacts=8,
        test_artifacts=4,
        seed=11,
        fixed_target_count_per_artifact=True,
    )
    membership = np.asarray(design["membership"], dtype=bool)
    assert membership[:8].sum(axis=0).tolist() == [4] * 64
    assert membership[8:].sum(axis=0).tolist() == [2] * 64
    assert membership.sum(axis=1).tolist() == [32] * 12
    assert design["membership_design"] == "fixed_row_and_column_degrees"
    assert len(set(design["target_labels"])) == 64
    targets = set(design["target_indices"])
    for record, row in zip(design["artifacts"], membership, strict=True):
        calibration_indices = set(record["calibration_indices"])
        assert len(calibration_indices) == 128
        for position, target in enumerate(design["target_indices"]):
            assert (target in calibration_indices) == bool(row[position])
        assert not (targets - set(np.asarray(design["target_indices"])[row])) & calibration_indices


def test_shadow_normalization_learns_direction_without_test_labels() -> None:
    membership = np.asarray(
        [
            [1, 0],
            [1, 0],
            [0, 1],
            [0, 1],
            [1, 0],
            [0, 1],
        ],
        dtype=bool,
    )
    # Candidate zero has larger member scores; candidate one has smaller member scores.
    raw = np.asarray(
        [
            [3.0, 3.0],
            [2.0, 4.0],
            [0.0, 0.0],
            [1.0, 1.0],
            [2.5, 3.5],
            [0.5, 0.5],
        ]
    )
    normalized = _shadow_normalize(raw, membership, shadow_count=4)
    assert normalized[0, 0] > normalized[1, 0]
    assert normalized[1, 1] > normalized[0, 1]
