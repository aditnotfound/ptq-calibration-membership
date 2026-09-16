from __future__ import annotations

import numpy as np
import pytest
import torch

from calibtrace.autoround_attack import _tensor_sha256
from calibtrace.gptq_attack import _gptq_modifier_options, _model_dtype, _require_finite_scores


def test_model_dtype_is_explicit_and_validated() -> None:
    assert _model_dtype("float16") is torch.float16
    assert _model_dtype("BFLOAT16") is torch.bfloat16
    assert _model_dtype("float32") is torch.float32
    with pytest.raises(ValueError, match="Unsupported model_dtype"):
        _model_dtype("float64")


def test_gptq_calibration_statistic_interventions_are_validated() -> None:
    assert _gptq_modifier_options(None) == {
        "dampening_frac": 0.01,
        "offload_hessians": False,
    }
    assert _gptq_modifier_options(
        {"dampening_frac": 0.1, "offload_hessians": True}
    ) == {"dampening_frac": 0.1, "offload_hessians": True}
    with pytest.raises(ValueError, match="nonnegative"):
        _gptq_modifier_options({"dampening_frac": -0.1})


def test_nonfinite_attack_scores_are_rejected_before_serialization() -> None:
    finite = np.ones(2, dtype=np.float64)
    _require_finite_scores(finite, finite[:, None], {"output": finite})
    with pytest.raises(FloatingPointError, match="output"):
        _require_finite_scores(finite, finite[:, None], {"output": np.asarray([np.nan])})


def test_tensor_hash_supports_bfloat16_and_tracks_exact_bits() -> None:
    first = {"weight": torch.tensor([1.0, 2.0], dtype=torch.bfloat16)}
    second = {"weight": torch.tensor([1.0, 3.0], dtype=torch.bfloat16)}
    assert _tensor_sha256(first) == _tensor_sha256(first)
    assert _tensor_sha256(first) != _tensor_sha256(second)
