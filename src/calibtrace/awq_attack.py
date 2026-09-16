"""Named-library AWQ calibration-membership experiment.

AWQ uses calibration activations to search for channel rescalings before applying groupwise
weight quantization. This module evaluates whether that distinct transformation also records
calibration membership in a released artifact.
"""

from __future__ import annotations

import gc
import inspect
from pathlib import Path
from typing import Any

import torch
from torch import nn

from .autoround_attack import _seed_all, evaluate_autoround_attack
from .gptq_attack import _calibration_dataset, _generate_llmcompressor_attack


def _quantize_awq(
    *,
    model_name: str,
    model_revision: str | None,
    tokenizer: Any,
    records: torch.Tensor,
    indices: list[int],
    seqlen: int,
    seed: int,
    device: torch.device,
    pipeline: str,
    group_size: int,
    bits: int,
    ignore: list[str],
    model_dtype: torch.dtype,
    cfg: dict[str, Any] | None = None,
) -> tuple[nn.Module, dict[str, torch.Tensor]]:
    from llmcompressor import oneshot
    from llmcompressor.modifiers.quantization import QuantizationModifier
    from llmcompressor.modifiers.transform import AWQModifier
    from llmcompressor.modifiers.transform.awq import AWQMapping
    from transformers import AutoModelForCausalLM

    if bits != 4 or group_size != 128:
        raise ValueError("The named AWQ recipe is registered for W4A16, group size 128")
    options = cfg or {}
    duo_scaling = options.get("duo_scaling", "both")
    n_grid = int(options.get("n_grid", 20))
    if duo_scaling not in (True, False, "both"):
        raise ValueError("duo_scaling must be true, false, or 'both'")
    if n_grid < 2:
        raise ValueError("n_grid must be at least 2")

    _seed_all(seed)
    model = (
        AutoModelForCausalLM.from_pretrained(
            model_name,
            revision=model_revision,
            local_files_only=True,
            dtype=model_dtype,
            attn_implementation="eager",
        )
        .eval()
        .to(device)
    )
    if model.__class__.__name__ != "OPTForCausalLM":
        raise ValueError(
            "This registered AWQ experiment currently defines mappings only for OPTForCausalLM"
        )
    mappings = [
        AWQMapping(
            "re:.*layers\\.\\d+\\.self_attn_layer_norm$",
            ["re:.*self_attn.q_proj$", "re:.*self_attn.k_proj$", "re:.*self_attn.v_proj$"],
        ),
        AWQMapping("re:.*self_attn.v_proj$", ["re:.*self_attn.out_proj$"]),
        AWQMapping("re:.*layers\\.\\d+\\.final_layer_norm$", ["re:.*fc1$"]),
        AWQMapping("re:.*fc1$", ["re:.*fc2$"]),
    ]
    recipe = [
        AWQModifier(mappings=mappings, duo_scaling=duo_scaling, n_grid=n_grid),
        QuantizationModifier(
            targets="Linear",
            scheme="W4A16_ASYM",
            ignore=list(ignore),
        ),
    ]
    arguments = {
        "model": model,
        "processor": tokenizer,
        "dataset": _calibration_dataset(records, indices),
        "recipe": recipe,
        "max_seq_length": seqlen,
        "num_calibration_samples": len(indices),
        "shuffle_calibration_samples": False,
        "pipeline": pipeline,
        "log_dir": None,
    }
    accepted = set(inspect.signature(oneshot).parameters)
    oneshot(**{key: value for key, value in arguments.items() if key in accepted})
    weights = {
        name: module.weight.detach().to(device, model_dtype).clone()
        for name, module in model.named_modules()
        if isinstance(module, nn.Linear) and getattr(module, "quantization_scheme", None) is not None
    }
    if not weights:
        raise RuntimeError("AWQ quantized no linear layers")
    gc.collect()
    return model.eval(), weights


def generate_awq_attack(config: dict[str, Any], config_path: str | Path) -> Path:
    cfg = config["awq_attack"]
    return _generate_llmcompressor_attack(
        config,
        config_path,
        section="awq_attack",
        method="AWQ",
        quantize_fn=_quantize_awq,
        contract_extra={
            "scheme": "W4A16_ASYM",
            "mapping_profile": "OPTForCausalLM:v2",
            "duo_scaling": cfg.get("duo_scaling", "both"),
            "n_grid": int(cfg.get("n_grid", 20)),
        },
    )


def evaluate_awq_attack(config: dict[str, Any], config_path: str | Path) -> Path:
    return evaluate_autoround_attack({"autoround_attack": config["awq_attack"]}, config_path)
