from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable

import torch
import torch.nn.functional as F
from torch import nn

from .model import quantizable_modules


@dataclass
class QuantizedTensor:
    codes: torch.Tensor
    scales: torch.Tensor
    shape: tuple[int, ...]

    def dequantize(self) -> torch.Tensor:
        rows = self.codes.reshape(self.shape[0], -1).float()
        return (rows * self.scales.reshape(-1, 1)).reshape(self.shape)


Artifact = OrderedDict[str, QuantizedTensor]


def signed_range(bits: int) -> tuple[int, int]:
    if bits < 2 or bits > 8:
        raise ValueError("This pilot supports signed quantization from 2 to 8 bits")
    return -(2 ** (bits - 1)), 2 ** (bits - 1) - 1


def fixed_per_row_scales(weight: torch.Tensor, bits: int) -> torch.Tensor:
    _, qmax = signed_range(bits)
    rows = weight.detach().float().reshape(weight.shape[0], -1)
    scales = rows.abs().amax(dim=1, keepdim=True) / qmax
    return scales.clamp_min(torch.finfo(torch.float32).eps)


def rtn_quantize_weight(weight: torch.Tensor, bits: int) -> QuantizedTensor:
    qmin, qmax = signed_range(bits)
    rows = weight.detach().float().reshape(weight.shape[0], -1)
    scales = fixed_per_row_scales(weight, bits)
    codes = torch.round(rows / scales).clamp(qmin, qmax).to(torch.int8)
    return QuantizedTensor(codes.cpu(), scales.squeeze(1).cpu(), tuple(weight.shape))


def rtn_artifact(model: nn.Module, bits: int, include_linear: bool = True) -> Artifact:
    return OrderedDict(
        (name, rtn_quantize_weight(module.weight, bits))
        for name, module in quantizable_modules(model, include_linear).items()
    )


class HessianCollector:
    """Collect fixed-base input second moments without saving activations."""

    def __init__(
        self,
        model: nn.Module,
        *,
        patches_per_image: int,
        include_linear: bool,
        device: torch.device,
    ) -> None:
        self.model = model
        self.patches_per_image = patches_per_image
        self.device = device
        self.modules = quantizable_modules(model, include_linear)
        self.hessians: OrderedDict[str, torch.Tensor] = OrderedDict()
        self.counts: dict[str, int] = {}
        self.handles: list[torch.utils.hooks.RemovableHandle] = []
        for name, module in self.modules.items():
            features = module.weight.reshape(module.weight.shape[0], -1).shape[1]
            self.hessians[name] = torch.zeros(
                (features, features), dtype=torch.float32, device=device
            )
            self.counts[name] = 0
            self.handles.append(module.register_forward_pre_hook(self._make_hook(name, module)))

    def _make_hook(self, name: str, module: nn.Module):
        def hook(_module: nn.Module, args: tuple[torch.Tensor, ...]) -> None:
            inputs = args[0].detach().float()
            if isinstance(module, nn.Conv2d):
                patches = F.unfold(
                    inputs,
                    kernel_size=module.kernel_size,
                    dilation=module.dilation,
                    padding=module.padding,
                    stride=module.stride,
                ).transpose(1, 2)
                available = patches.shape[1]
                take = min(self.patches_per_image, available)
                positions = torch.linspace(
                    0, available - 1, steps=take, device=patches.device
                ).round().long()
                matrix = patches[:, positions, :].reshape(-1, patches.shape[-1])
            elif isinstance(module, nn.Linear):
                matrix = inputs.reshape(-1, inputs.shape[-1])
            else:  # pragma: no cover - guarded by quantizable_modules
                return
            self.hessians[name].addmm_(matrix.transpose(0, 1), matrix)
            self.counts[name] += matrix.shape[0]

        return hook

    @torch.inference_mode()
    def collect(self, batches: Iterable[tuple[torch.Tensor, torch.Tensor, torch.Tensor]]) -> None:
        self.model.eval()
        try:
            for images, _, _ in batches:
                self.model(images.to(self.device, non_blocking=True))
        finally:
            self.close()

    def close(self) -> None:
        for handle in self.handles:
            handle.remove()
        self.handles.clear()


def _inverse_cholesky_factor(hessian: torch.Tensor, damping: float) -> torch.Tensor:
    hessian = hessian.float()
    diagonal = torch.arange(hessian.shape[0], device=hessian.device)
    mean_diagonal = hessian.diag().mean().clamp_min(torch.finfo(hessian.dtype).eps)
    multiplier = damping
    for _ in range(6):
        regularized = hessian.clone()
        regularized[diagonal, diagonal] += multiplier * mean_diagonal
        factor, info = torch.linalg.cholesky_ex(regularized)
        if int(info.max()) == 0:
            inverse = torch.cholesky_inverse(factor)
            return torch.linalg.cholesky(inverse, upper=True)
        multiplier *= 10.0
    raise RuntimeError("Calibration Hessian remained non-positive-definite after damping")


@torch.inference_mode()
def gptq_quantize_weight(
    weight: torch.Tensor,
    hessian: torch.Tensor,
    sample_count: int,
    *,
    bits: int,
    damping: float,
    block_size: int,
) -> QuantizedTensor:
    """Deterministic GPTQ-style sequential error compensation on a fixed grid."""
    if sample_count <= 0:
        raise ValueError("No calibration activations were collected")
    qmin, qmax = signed_range(bits)
    original_shape = tuple(weight.shape)
    work = weight.detach().float().reshape(weight.shape[0], -1).clone()
    scales = fixed_per_row_scales(weight, bits).to(work.device)
    hessian = hessian / float(sample_count)
    inverse_factor = _inverse_cholesky_factor(hessian, damping)
    columns = work.shape[1]
    quantized = torch.zeros_like(work)

    for start in range(0, columns, block_size):
        stop = min(start + block_size, columns)
        block = work[:, start:stop].clone()
        block_factor = inverse_factor[start:stop, start:stop]
        errors = torch.zeros_like(block)
        for local_column in range(stop - start):
            values = block[:, local_column]
            diagonal = block_factor[local_column, local_column]
            codes = torch.round(values / scales[:, 0]).clamp(qmin, qmax)
            dequantized = codes * scales[:, 0]
            quantized[:, start + local_column] = dequantized
            error = (values - dequantized) / diagonal
            block[:, local_column:] -= error.unsqueeze(1) * block_factor[
                local_column, local_column:
            ].unsqueeze(0)
            errors[:, local_column] = error
        if stop < columns:
            work[:, stop:] -= errors @ inverse_factor[start:stop, stop:]

    codes = torch.round(quantized / scales).clamp(qmin, qmax).to(torch.int8)
    return QuantizedTensor(codes.cpu(), scales.squeeze(1).cpu(), original_shape)


@torch.inference_mode()
def gptq_artifact(
    model: nn.Module,
    batches: Iterable[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
    *,
    bits: int,
    damping: float,
    block_size: int,
    patches_per_image: int,
    include_linear: bool,
    device: torch.device,
) -> Artifact:
    collector = HessianCollector(
        model,
        patches_per_image=patches_per_image,
        include_linear=include_linear,
        device=device,
    )
    collector.collect(batches)
    artifact: Artifact = OrderedDict()
    for name, module in collector.modules.items():
        artifact[name] = gptq_quantize_weight(
            module.weight,
            collector.hessians[name],
            collector.counts[name],
            bits=bits,
            damping=damping,
            block_size=block_size,
        )
        del collector.hessians[name]
    return artifact


def apply_artifact(model: nn.Module, artifact: Artifact) -> None:
    modules = dict(model.named_modules())
    with torch.no_grad():
        for name, tensor in artifact.items():
            module = modules[name]
            module.weight.copy_(tensor.dequantize().to(module.weight.device, module.weight.dtype))

