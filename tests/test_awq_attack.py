from __future__ import annotations

import pytest

from calibtrace.awq_attack import _quantize_awq


def test_awq_registered_recipe_rejects_nonstandard_shape_before_loading_model() -> None:
    with pytest.raises(ValueError, match="W4A16"):
        _quantize_awq(
            model_name="unused",
            model_revision=None,
            tokenizer=None,
            records=None,  # type: ignore[arg-type]
            indices=[],
            seqlen=8,
            seed=1,
            device=None,  # type: ignore[arg-type]
            pipeline="sequential",
            group_size=64,
            bits=4,
            ignore=[],
            model_dtype=None,  # type: ignore[arg-type]
        )
