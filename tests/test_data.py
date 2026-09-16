from __future__ import annotations

import numpy as np

from calibtrace.data import make_split_manifest


def test_manifest_is_balanced_and_disjoint() -> None:
    labels = np.repeat(np.arange(100, dtype=np.int64), 500)
    manifest = make_split_manifest(
        labels, train_per_class=400, calibration_per_class=100, seed=7
    )
    manifest.validate(labels)
    assert len(manifest.train_indices) == 40_000
    assert len(manifest.calibration_indices) == 10_000
    assert set(manifest.train_indices).isdisjoint(manifest.calibration_indices)
    assert len(manifest.to_json()["sha256"]) == 64

