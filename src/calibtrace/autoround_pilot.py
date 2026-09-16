from __future__ import annotations

import gc
import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader

from .config import resolve_path


def _seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _sequence_digest(sequence: torch.Tensor) -> str:
    return hashlib.sha256(sequence.contiguous().numpy().tobytes()).hexdigest()


def _calibration_digest(indices: list[int]) -> str:
    return hashlib.sha256(",".join(str(value) for value in indices).encode("ascii")).hexdigest()


def _synthetic_sequences(tokenizer: Any, count: int, seqlen: int, seed: int) -> list[torch.Tensor]:
    vocabulary = (
        "analysis artifact boundary calibration channel compression confidential consequence "
        "dataset deployment discrete evidence experiment feature geometry gradient hidden "
        "inference information layer mechanism membership model observation optimization privacy "
        "quantization record reconstruction release residual sample security signal statistic "
        "threshold training transformation uncertainty validation vector weight"
    ).split()
    rng = np.random.default_rng(seed)
    sequences: list[torch.Tensor] = []
    for record_id in range(count):
        nonce = hashlib.sha256(f"calibtrace-{seed}-{record_id}".encode("ascii")).hexdigest()
        words = rng.choice(vocabulary, size=4 * seqlen, replace=True).tolist()
        text = (
            f"Novel CalibTrace calibration record {record_id} nonce {nonce}. "
            + " ".join(words)
        )
        token_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
        if len(token_ids) < seqlen:
            raise RuntimeError("Synthetic calibration record tokenized below the requested length")
        sequences.append(torch.tensor(token_ids[:seqlen], dtype=torch.long))
    return sequences


def _loader(sequences: list[torch.Tensor], indices: list[int], batch_size: int) -> DataLoader:
    examples = [
        {
            "input_ids": sequences[index],
            "attention_mask": torch.ones_like(sequences[index]),
        }
        for index in indices
    ]
    return DataLoader(examples, batch_size=batch_size, shuffle=False, num_workers=0)


@torch.inference_mode()
def _capture_base(
    model: nn.Module, candidate_batch: torch.Tensor
) -> tuple[
    dict[str, torch.Tensor],
    dict[str, torch.Tensor],
    dict[str, torch.Tensor],
    torch.Tensor,
]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()
    inputs: dict[str, torch.Tensor] = {}
    output_energy: dict[str, torch.Tensor] = {}
    handles: list[torch.utils.hooks.RemovableHandle] = []
    candidate_count = candidate_batch.shape[0]

    def make_hook(name: str):
        def hook(_module: nn.Module, args: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
            inputs[name] = args[0].detach().to("cpu", torch.float16)
            output_energy[name] = (
                output.detach().float().reshape(candidate_count, -1).square().sum(1).cpu()
            )

        return hook

    linear_modules = {
        name: module for name, module in model.named_modules() if isinstance(module, nn.Linear)
    }
    for name, module in linear_modules.items():
        handles.append(module.register_forward_hook(make_hook(name)))
    try:
        attention_mask = torch.ones_like(candidate_batch, device=device)
        logits = model(
            input_ids=candidate_batch.to(device), attention_mask=attention_mask
        ).logits.detach().cpu()
    finally:
        for handle in handles:
            handle.remove()
    weights = {
        name: module.weight.detach().to("cpu", torch.float16).clone()
        for name, module in linear_modules.items()
    }
    model.to("cpu")
    return weights, inputs, output_energy, logits


def _quantize_once(
    *,
    model_name: str,
    tokenizer: Any,
    loader: DataLoader,
    candidate_batch: torch.Tensor,
    seqlen: int,
    calibration_size: int,
    batch_size: int,
    iters: int,
    seed: int,
) -> tuple[dict[str, torch.Tensor], torch.Tensor, list[str], float]:
    from auto_round import AutoRound
    from transformers import AutoModelForCausalLM

    _seed_all(seed)
    started = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        local_files_only=True,
        dtype=torch.float16,
        attn_implementation="eager",
    ).eval()
    compressor = AutoRound(
        model,
        tokenizer=tokenizer,
        scheme="W4A16",
        dataset=loader,
        iters=iters,
        seqlen=seqlen,
        nsamples=calibration_size,
        batch_size=batch_size,
        device_map=0,
        enable_torch_compile=False,
        enable_deterministic_algorithms=True,
        seed=seed,
        low_cpu_mem_usage=False,
    )
    quantized_model, layer_config = compressor.quantize()
    module_lookup = dict(quantized_model.named_modules())
    quantized_names = [
        name
        for name, settings in layer_config.items()
        if isinstance(settings, dict)
        and int(settings.get("bits", 16)) < 16
        and name in module_lookup
        and isinstance(module_lookup[name], nn.Linear)
    ]
    weights = {
        name: module_lookup[name].weight.detach().to("cpu", torch.float16).clone()
        for name in quantized_names
    }
    device = next(quantized_model.parameters()).device
    with torch.inference_mode():
        logits = quantized_model(
            input_ids=candidate_batch.to(device),
            attention_mask=torch.ones_like(candidate_batch, device=device),
        ).logits.detach().cpu()
    seconds = time.perf_counter() - started
    del compressor, quantized_model, model, module_lookup
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return weights, logits, quantized_names, seconds


@torch.inference_mode()
def _reconstruction_scores(
    quantized_weights: dict[str, torch.Tensor],
    base_weights: dict[str, torch.Tensor],
    inputs: dict[str, torch.Tensor],
    output_energy: dict[str, torch.Tensor],
) -> np.ndarray:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    candidate_count = next(iter(inputs.values())).shape[0]
    error = torch.zeros(candidate_count, dtype=torch.float64, device=device)
    baseline = torch.zeros_like(error)
    for name, quantized_weight in quantized_weights.items():
        layer_input = inputs[name].to(device)
        difference = quantized_weight.to(device) - base_weights[name].to(device)
        residual = F.linear(layer_input, difference)
        error += residual.float().reshape(candidate_count, -1).square().sum(1).double()
        baseline += output_energy[name].to(device).double()
    return (-(error / baseline.clamp_min(torch.finfo(torch.float64).eps))).cpu().numpy()


def run_autoround_pilot(config: dict[str, Any], config_path: str | Path) -> Path:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = config["autoround"]
    seed = int(cfg["seed"])
    model_name = str(cfg["model"])
    seqlen = int(cfg["sequence_length"])
    calibration_size = int(cfg["calibration_size"])
    targets = int(cfg["targets"])
    backgrounds_per_target = int(cfg["backgrounds_per_target"])
    batch_size = int(cfg["batch_size"])
    iters = int(cfg["iters"])
    if not os.environ.get("HF_HOME"):
        raise RuntimeError("Set HF_HOME to the project-local Hugging Face cache")
    _seed_all(seed)
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    probe_model = AutoModelForCausalLM.from_pretrained(
        model_name, local_files_only=True, dtype=torch.float16
    ).eval()
    parameter_count = sum(parameter.numel() for parameter in probe_model.parameters())

    pool_size = max(2048, 2 * targets + calibration_size * targets * backgrounds_per_target)
    sequences = _synthetic_sequences(tokenizer, pool_size, seqlen, seed + 101)
    target_indices = list(range(0, 2 * targets, 2))
    replacement_indices = list(range(1, 2 * targets, 2))
    candidate_indices = [
        value for pair in zip(target_indices, replacement_indices, strict=True) for value in pair
    ]
    candidate_batch = torch.stack([sequences[index] for index in candidate_indices])
    base_weights, captured_inputs, output_energy, base_logits = _capture_base(
        probe_model, candidate_batch
    )
    del probe_model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    excluded = set(candidate_indices)
    background_pool = np.asarray(
        [index for index in range(pool_size) if index not in excluded], dtype=np.int64
    )
    records: list[dict[str, Any]] = []
    repeat_changed: int | None = None
    quantized_layer_names: list[str] | None = None
    first_member_weights: dict[str, torch.Tensor] | None = None
    pair_id = 0
    for target_position, (target_index, replacement_index) in enumerate(
        zip(target_indices, replacement_indices, strict=True)
    ):
        for background_id in range(backgrounds_per_target):
            pair_seed = seed + 1_000_003 * (pair_id + 1)
            rng = np.random.default_rng(pair_seed)
            background_indices = sorted(
                int(value)
                for value in rng.choice(
                    background_pool, calibration_size - 1, replace=False
                )
            )
            member_indices = sorted([*background_indices, target_index])
            nonmember_indices = sorted([*background_indices, replacement_index])
            member_weights, member_logits, member_names, member_seconds = _quantize_once(
                model_name=model_name,
                tokenizer=tokenizer,
                loader=_loader(sequences, member_indices, batch_size),
                candidate_batch=candidate_batch,
                seqlen=seqlen,
                calibration_size=calibration_size,
                batch_size=batch_size,
                iters=iters,
                seed=pair_seed,
            )
            nonmember_weights, nonmember_logits, nonmember_names, nonmember_seconds = _quantize_once(
                model_name=model_name,
                tokenizer=tokenizer,
                loader=_loader(sequences, nonmember_indices, batch_size),
                candidate_batch=candidate_batch,
                seqlen=seqlen,
                calibration_size=calibration_size,
                batch_size=batch_size,
                iters=iters,
                seed=pair_seed,
            )
            if member_names != nonmember_names:
                raise RuntimeError("AutoRound quantized different layer sets across a matched pair")
            quantized_layer_names = member_names
            changed = sum(
                int(torch.count_nonzero(member_weights[name] != nonmember_weights[name]))
                for name in member_names
            )
            total = sum(member_weights[name].numel() for name in member_names)
            member_reconstruction = _reconstruction_scores(
                member_weights, base_weights, captured_inputs, output_energy
            )
            nonmember_reconstruction = _reconstruction_scores(
                nonmember_weights, base_weights, captured_inputs, output_energy
            )
            member_output = -(
                (member_logits.float() - base_logits.float()).square().mean((1, 2)).numpy()
            )
            nonmember_output = -(
                (nonmember_logits.float() - base_logits.float()).square().mean((1, 2)).numpy()
            )
            target_candidate = 2 * target_position
            replacement_candidate = target_candidate + 1
            record = {
                "pair_id": pair_id,
                "target_position": target_position,
                "background_id": background_id,
                "target_digest": _sequence_digest(sequences[target_index]),
                "replacement_digest": _sequence_digest(sequences[replacement_index]),
                "member_calibration_digest": _calibration_digest(member_indices),
                "nonmember_calibration_digest": _calibration_digest(nonmember_indices),
                "changed_weights": changed,
                "total_quantized_weights": total,
                "changed_weight_fraction": changed / total,
                "target_reconstruction_margin": float(
                    member_reconstruction[target_candidate]
                    - nonmember_reconstruction[target_candidate]
                ),
                "replacement_reconstruction_margin": float(
                    nonmember_reconstruction[replacement_candidate]
                    - member_reconstruction[replacement_candidate]
                ),
                "target_output_margin": float(
                    member_output[target_candidate] - nonmember_output[target_candidate]
                ),
                "replacement_output_margin": float(
                    nonmember_output[replacement_candidate] - member_output[replacement_candidate]
                ),
                "member_seconds": member_seconds,
                "nonmember_seconds": nonmember_seconds,
            }
            records.append(record)
            print(json.dumps(record, sort_keys=True), flush=True)

            if pair_id == 0:
                first_member_weights = member_weights
                repeat_weights, _, repeat_names, _ = _quantize_once(
                    model_name=model_name,
                    tokenizer=tokenizer,
                    loader=_loader(sequences, member_indices, batch_size),
                    candidate_batch=candidate_batch,
                    seqlen=seqlen,
                    calibration_size=calibration_size,
                    batch_size=batch_size,
                    iters=iters,
                    seed=pair_seed,
                )
                if repeat_names != member_names:
                    raise RuntimeError("AutoRound repeat quantized a different layer set")
                repeat_changed = sum(
                    int(torch.count_nonzero(first_member_weights[name] != repeat_weights[name]))
                    for name in member_names
                )
                del repeat_weights
            del member_weights, nonmember_weights
            pair_id += 1

    reconstruction_margins = np.asarray(
        [
            margin
            for record in records
            for margin in (
                record["target_reconstruction_margin"],
                record["replacement_reconstruction_margin"],
            )
        ]
    )
    output_margins = np.asarray(
        [
            margin
            for record in records
            for margin in (record["target_output_margin"], record["replacement_output_margin"])
        ]
    )
    result = {
        "run_date": "2026-08-23",
        "library": "auto-round",
        "library_version": __import__("auto_round").__version__,
        "model": model_name,
        "parameters": parameter_count,
        "bits": 4,
        "calibration_size": calibration_size,
        "sequence_length": seqlen,
        "iters": iters,
        "targets": targets,
        "backgrounds_per_target": backgrounds_per_target,
        "pairs": len(records),
        "quantized_layers": len(quantized_layer_names or []),
        "determinism_repeat_changed_weights": repeat_changed,
        "mean_changed_weight_fraction": float(
            np.mean([record["changed_weight_fraction"] for record in records])
        ),
        "reconstruction_directional_wins": int(np.count_nonzero(reconstruction_margins > 0)),
        "reconstruction_decisions": int(len(reconstruction_margins)),
        "mean_reconstruction_margin": float(reconstruction_margins.mean()),
        "output_directional_wins": int(np.count_nonzero(output_margins > 0)),
        "output_decisions": int(len(output_margins)),
        "mean_output_margin": float(output_margins.mean()),
        "records": records,
        "limitations": [
            "Synthetic novel token sequences are a provenance-safe external-library pilot, not a real-text population.",
            "This paired experiment establishes causal influence, not a held-out single-artifact attack.",
            "Sequence length is shorter than production LLM calibration contexts.",
        ],
    }
    result_path = resolve_path(config_path, cfg["results"])
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return result_path
