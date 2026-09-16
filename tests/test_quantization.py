from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np
import torch

from calibtrace.artifact_io import load_artifact, save_artifact
from calibtrace.quantization import (
    QuantizedTensor,
    gptq_quantize_weight,
    rtn_quantize_weight,
)


def test_w4_artifact_round_trip() -> None:
    codes = torch.tensor([[-8, -1, 0, 7], [3, 2, -2, -7]], dtype=torch.int8)
    artifact = OrderedDict(
        layer=QuantizedTensor(codes=codes, scales=torch.tensor([0.1, 0.2]), shape=(2, 4))
    )
    path = Path("artifact_round_trip_test.npz")
    try:
        digest = save_artifact(artifact, path, bits=4, metadata={"test": True})
        restored, header = load_artifact(path)
        assert len(digest) == 64
        assert header["test"] is True
        assert torch.equal(restored["layer"].codes, codes)
        assert torch.equal(restored["layer"].scales, artifact["layer"].scales)
    finally:
        path.unlink(missing_ok=True)


def test_rtn_uses_fixed_weight_grid() -> None:
    weight = torch.tensor([[0.0, 0.4, -0.9, 1.0]], dtype=torch.float32)
    first = rtn_quantize_weight(weight, bits=4)
    second = rtn_quantize_weight(weight.clone(), bits=4)
    assert torch.equal(first.codes, second.codes)
    assert torch.equal(first.scales, second.scales)


def test_gptq_codes_can_depend_on_calibration_hessian() -> None:
    generator = torch.Generator().manual_seed(19)
    found_difference = False
    for _ in range(12):
        weight = torch.randn(5, 12, generator=generator)
        first_inputs = torch.randn(12, 16, generator=generator)
        second_inputs = torch.randn(12, 16, generator=generator)
        first = gptq_quantize_weight(
            weight,
            first_inputs @ first_inputs.T,
            16,
            bits=4,
            damping=0.01,
            block_size=6,
        )
        second = gptq_quantize_weight(
            weight,
            second_inputs @ second_inputs.T,
            16,
            bits=4,
            damping=0.01,
            block_size=6,
        )
        assert np.array_equal(first.scales.numpy(), second.scales.numpy())
        if not torch.equal(first.codes, second.codes):
            found_difference = True
            break
    assert found_difference
