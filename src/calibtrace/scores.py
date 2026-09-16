from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn

from .artifact_io import load_artifact
from .config import resolve_path
from .data import CIFAR100Dataset, load_datasets
from .model import quantizable_modules
from .quantization import Artifact
from .repro import default_device, seed_everything
from .train import load_base_model


@torch.inference_mode()
def capture_candidate(
    model: nn.Module,
    image: torch.Tensor,
    *,
    include_linear: bool,
) -> OrderedDict[str, tuple[torch.Tensor, float]]:
    captured: OrderedDict[str, tuple[torch.Tensor, float]] = OrderedDict()
    handles: list[torch.utils.hooks.RemovableHandle] = []

    def make_hook(name: str):
        def hook(_module: nn.Module, args: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
            captured[name] = (args[0].detach(), float(output.detach().double().square().sum()))

        return hook

    for name, module in quantizable_modules(model, include_linear).items():
        handles.append(module.register_forward_hook(make_hook(name)))
    try:
        model(image)
    finally:
        for handle in handles:
            handle.remove()
    return captured


@torch.inference_mode()
def reconstruction_score(
    model: nn.Module,
    artifact: Artifact,
    captured: OrderedDict[str, tuple[torch.Tensor, float]],
    *,
    include_linear: bool,
) -> dict[str, Any]:
    modules = quantizable_modules(model, include_linear)
    absolute_total = 0.0
    baseline_total = 0.0
    layer_relative: dict[str, float] = {}
    epsilon = np.finfo(np.float64).eps
    for name, module in modules.items():
        inputs, baseline_energy = captured[name]
        quantized_weight = artifact[name].dequantize().to(
            module.weight.device, module.weight.dtype
        )
        difference = quantized_weight - module.weight
        if isinstance(module, nn.Conv2d):
            residual = F.conv2d(
                inputs,
                difference,
                bias=None,
                stride=module.stride,
                padding=module.padding,
                dilation=module.dilation,
                groups=module.groups,
            )
        elif isinstance(module, nn.Linear):
            residual = F.linear(inputs, difference, bias=None)
        else:  # pragma: no cover - guarded by quantizable_modules
            continue
        error_energy = float(residual.double().square().sum())
        absolute_total += error_energy
        baseline_total += baseline_energy
        layer_relative[name] = error_energy / max(baseline_energy, epsilon)
    relative_error = absolute_total / max(baseline_total, epsilon)
    mean_layer_relative_error = float(np.mean(list(layer_relative.values())))
    return {
        "score": -relative_error,
        "relative_error": relative_error,
        "mean_layer_score": -mean_layer_relative_error,
        "mean_layer_relative_error": mean_layer_relative_error,
        "layers": layer_relative,
    }


def _image_for_source_index(dataset: CIFAR100Dataset, source_index: int) -> torch.Tensor:
    positions = np.flatnonzero(dataset.indices == source_index)
    if len(positions) != 1:
        raise ValueError(f"Expected one calibration record for source index {source_index}")
    image, _, _ = dataset[int(positions[0])]
    return image.unsqueeze(0)


def score_saved_pairs(
    config: dict[str, Any],
    config_path: str | Path,
    results_path: str | Path | None = None,
) -> Path:
    seed_everything(int(config["seed"]))
    device = default_device()
    paths = config["paths"]
    data_cfg = config["data"]
    _, calibration, _, _ = load_datasets(
        resolve_path(config_path, paths["data_dir"]),
        train_per_class=int(data_cfg["train_per_class"]),
        calibration_per_class=int(data_cfg["calibration_per_class"]),
        split_seed=int(data_cfg["split_seed"]),
    )
    checkpoint_path = resolve_path(config_path, paths["base_checkpoint"])
    model = load_base_model(checkpoint_path, device)
    include_linear = bool(config["quantization"]["quantize_linear"])
    if results_path is None:
        results_path = resolve_path(config_path, paths["result_dir"]) / "pilot_results.json"
    results_path = Path(results_path)
    with results_path.open("r", encoding="utf-8") as handle:
        results = json.load(handle)

    capture_cache: dict[int, OrderedDict[str, tuple[torch.Tensor, float]]] = {}

    def get_capture(source_index: int) -> OrderedDict[str, tuple[torch.Tensor, float]]:
        if source_index not in capture_cache:
            image = _image_for_source_index(calibration, source_index).to(device)
            capture_cache[source_index] = capture_candidate(
                model, image, include_linear=include_linear
            )
        return capture_cache[source_index]

    for condition_name, condition in results["conditions"].items():
        pair_scores: list[dict[str, Any]] = []
        for position, record in enumerate(condition["pairs"], start=1):
            member, _ = load_artifact(record["member_artifact"])
            nonmember, _ = load_artifact(record["nonmember_artifact"])
            target_index = int(record["target_index"])
            replacement_index = int(record["replacement_index"])
            target_capture = get_capture(target_index)
            replacement_capture = get_capture(replacement_index)
            target_in = reconstruction_score(
                model, member, target_capture, include_linear=include_linear
            )
            target_out = reconstruction_score(
                model, nonmember, target_capture, include_linear=include_linear
            )
            replacement_in = reconstruction_score(
                model, nonmember, replacement_capture, include_linear=include_linear
            )
            replacement_out = reconstruction_score(
                model, member, replacement_capture, include_linear=include_linear
            )
            target_margin = target_in["score"] - target_out["score"]
            replacement_margin = replacement_in["score"] - replacement_out["score"]
            pair_scores.append(
                {
                    "pair_id": record["pair_id"],
                    "target_index": target_index,
                    "replacement_index": replacement_index,
                    "target_member_score": target_in["score"],
                    "target_nonmember_score": target_out["score"],
                    "target_margin": target_margin,
                    "replacement_member_score": replacement_in["score"],
                    "replacement_nonmember_score": replacement_out["score"],
                    "replacement_margin": replacement_margin,
                    "mean_directional_margin": (target_margin + replacement_margin) / 2.0,
                }
            )
            print(
                json.dumps(
                    {
                        "condition": condition_name,
                        "pair": f"{position}/{len(condition['pairs'])}",
                        "target_margin": target_margin,
                        "replacement_margin": replacement_margin,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        directional_margins = [
            value
            for pair in pair_scores
            for value in (pair["target_margin"], pair["replacement_margin"])
        ]
        condition["reconstruction_scores"] = {
            "pairs": pair_scores,
            "mean_directional_margin": float(np.mean(directional_margins)),
            "median_directional_margin": float(np.median(directional_margins)),
            "directional_win_rate": float(np.mean(np.asarray(directional_margins) > 0)),
            "targets": len(pair_scores),
            "directional_comparisons": len(directional_margins),
        }
    with results_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return results_path

