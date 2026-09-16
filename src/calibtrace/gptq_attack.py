"""Named-library GPTQ replication of the calibration membership attack.

Where :mod:`calibtrace.autoround_attack` exercises AutoRound's iterative rounding optimization,
this module runs the same population design through llm-compressor's GPTQ implementation. GPTQ
applies one-shot Hessian-informed error compensation, which is the mechanism the repository's own
CIFAR quantizer imitates, so this is the matched external-validity test for the flagship claim.
"""

from __future__ import annotations

import gc
import inspect
import json
import os
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch
from torch import nn

from .autoround_attack import (
    _output_scores,
    _reconstruction_scores,
    _seed_all,
    _tensor_sha256,
    attach_experiment_contract,
    evaluate_autoround_attack,
    load_record_pool,
    make_population_design,
    prepare_resumable_scores,
)
from .config import resolve_path


def _model_dtype(name: str) -> torch.dtype:
    values = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    try:
        return values[name.lower()]
    except KeyError as error:
        supported = ", ".join(sorted(values))
        raise ValueError(f"Unsupported model_dtype {name!r}; choose one of {supported}") from error


def _require_finite_scores(
    reconstruction: np.ndarray,
    layer_reconstruction: np.ndarray,
    outputs: dict[str, np.ndarray],
) -> None:
    arrays = {
        "artifact_reconstruction": reconstruction,
        "layer_reconstruction": layer_reconstruction,
        **outputs,
    }
    invalid = {
        name: int(values.size - np.count_nonzero(np.isfinite(values)))
        for name, values in arrays.items()
        if not np.isfinite(values).all()
    }
    if invalid:
        raise FloatingPointError(f"Non-finite attack scores: {invalid}")


def _gptq_modifier_options(cfg: dict[str, Any] | None) -> dict[str, Any]:
    """Return the calibration-statistic intervention knobs recorded in the contract."""
    values = cfg or {}
    dampening_frac = float(values.get("dampening_frac", 0.01))
    if dampening_frac < 0:
        raise ValueError("dampening_frac must be nonnegative")
    return {
        "dampening_frac": dampening_frac,
        "offload_hessians": bool(values.get("offload_hessians", False)),
    }


def _calibration_dataset(records: torch.Tensor, indices: list[int]) -> Any:
    from datasets import Dataset

    selected = records[indices]
    return Dataset.from_dict(
        {
            "input_ids": selected.tolist(),
            "attention_mask": torch.ones_like(selected).tolist(),
        }
    )


def _quantize_gptq(
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
    from llmcompressor.modifiers.quantization import GPTQModifier
    from transformers import AutoModelForCausalLM

    _seed_all(seed)
    load_kwargs: dict[str, Any] = {
        "revision": model_revision,
        "local_files_only": True,
        "dtype": model_dtype,
        "attn_implementation": "eager",
    }
    device_map = (cfg or {}).get("quantization_device_map")
    if device_map:
        load_kwargs["device_map"] = device_map
        max_memory = (cfg or {}).get("quantization_max_memory")
        if max_memory:
            load_kwargs["max_memory"] = {
                (int(key) if str(key).isdigit() else str(key)): str(value)
                for key, value in max_memory.items()
            }
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs).eval()
    if not device_map:
        model = model.to(device)
    modifier = GPTQModifier(
        targets="Linear",
        scheme=f"W{bits}A16",
        ignore=list(ignore),
        block_size=group_size,
        **_gptq_modifier_options(cfg),
    )
    arguments = {
        "model": model,
        "processor": tokenizer,
        "dataset": _calibration_dataset(records, indices),
        "recipe": modifier,
        "max_seq_length": seqlen,
        "num_calibration_samples": len(indices),
        "shuffle_calibration_samples": False,
        "pipeline": pipeline,
        "log_dir": None,
    }
    accepted = set(inspect.signature(oneshot).parameters)
    oneshot(**{key: value for key, value in arguments.items() if key in accepted})
    weights = {
        name: module.weight.detach()
        for name, module in model.named_modules()
        if isinstance(module, nn.Linear) and getattr(module, "quantization_scheme", None) is not None
    }
    if not weights:
        raise RuntimeError("GPTQ quantized no linear layers")
    gc.collect()
    return model.eval(), weights


def _generate_llmcompressor_attack(
    config: dict[str, Any],
    config_path: str | Path,
    *,
    section: str,
    method: str,
    quantize_fn: Callable[..., tuple[nn.Module, dict[str, torch.Tensor]]],
    contract_extra: dict[str, Any] | None = None,
) -> Path:
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = config[section]
    if not os.environ.get("HF_HOME"):
        raise RuntimeError("Set HF_HOME to the project-local Hugging Face cache")
    seed = int(cfg["seed"])
    model_name = str(cfg["model"])
    model_revision = str(cfg["model_revision"]) if cfg.get("model_revision") else None
    model_dtype_name = str(cfg.get("model_dtype", "float16")).lower()
    model_dtype = _model_dtype(model_dtype_name)
    seqlen = int(cfg["sequence_length"])
    calibration_size = int(cfg["calibration_size"])
    targets = int(cfg["targets"])
    bits = int(cfg.get("bits", 4))
    reference_records = int(cfg.get("reference_records", 0))
    pipeline = str(cfg.get("pipeline", "sequential"))
    group_size = int(cfg.get("group_size", 128))
    ignore = list(cfg.get("ignore", ["lm_head"]))
    requested_device = str(cfg.get("scoring_device", "auto")).lower()
    if requested_device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif requested_device in {"cpu", "cuda"}:
        device = torch.device(requested_device)
    else:
        raise ValueError("scoring_device must be auto, cpu, or cuda")

    _seed_all(seed)
    model_source = snapshot_download(
        model_name,
        revision=model_revision,
        local_files_only=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_source, local_files_only=True
    )
    design = make_population_design(
        calibration_size=calibration_size,
        targets=targets,
        shadow_artifacts=int(cfg["shadow_artifacts"]),
        test_artifacts=int(cfg["test_artifacts"]),
        pool_size=int(cfg["pool_size"]),
        seed=seed,
        reference_records=reference_records,
    )
    record_seed = int(cfg.get("record_seed", seed + 101))
    records, record_metadata = load_record_pool(
        tokenizer,
        cfg=cfg,
        config_path=config_path,
        count=int(cfg["pool_size"]),
        seqlen=seqlen,
        seed=record_seed,
    )
    scored = records[: targets + reference_records]

    base_model = AutoModelForCausalLM.from_pretrained(
        model_source,
        local_files_only=True,
        dtype=model_dtype,
        attn_implementation="eager",
    ).eval().to(device)
    design.update(
        {
            "model": model_name,
            "model_revision": model_revision,
            "parameters": int(sum(p.numel() for p in base_model.parameters())),
            "sequence_length": seqlen,
            "iters": 0,
            "bits": bits,
            "group_size": group_size,
            "library": "llm-compressor",
            "library_version": __import__("llmcompressor").__version__,
            "method": method,
            "pipeline": pipeline,
            "quantizer_seed": "fixed",
            "model_dtype": model_dtype_name,
        }
    )
    contract = {
        "library": design["library"],
        "library_version": design["library_version"],
        "model": model_name,
        "model_revision": model_revision,
        "method": method,
        "bits": bits,
        "group_size": group_size,
        "pipeline": pipeline,
        "ignore": ignore,
        "quantizer_seed": design["quantizer_seed"],
        "model_dtype": model_dtype_name,
        "scoring_device": str(device),
        "quantization_device_map": cfg.get("quantization_device_map"),
        "quantization_max_memory": cfg.get("quantization_max_memory"),
        "score_chunk": int(cfg.get("score_chunk", 4)),
        "output_chunk": int(cfg.get("output_chunk", 2)),
        **_gptq_modifier_options(cfg),
    }
    if contract_extra:
        contract.update(contract_extra)
    if "reconstruction_compute_dtype" in cfg:
        contract["reconstruction_compute_dtype"] = str(cfg["reconstruction_compute_dtype"])
    attach_experiment_contract(
        design,
        record_metadata=record_metadata,
        contract=contract,
    )

    manifest_path = resolve_path(config_path, cfg["manifest"])
    scores_path = resolve_path(config_path, cfg["scores"])
    scores_path.parent.mkdir(parents=True, exist_ok=True)
    completed, _ = prepare_resumable_scores(scores_path, manifest_path, design)

    reference_weights: dict[str, torch.Tensor] | None = None
    track_changed_fraction = bool(cfg.get("track_changed_fraction", True))
    if (
        track_changed_fraction
        and completed
        and len(completed) < len(design["artifacts"])
        and 0 in completed
    ):
        first = design["artifacts"][0]
        quantized_reference, reference_weights = quantize_fn(
            model_name=model_source,
            model_revision=None,
            tokenizer=tokenizer,
            records=records,
            indices=first["calibration_indices"],
            seqlen=seqlen,
            seed=seed,
            device=device,
            pipeline=pipeline,
            group_size=group_size,
            bits=bits,
            ignore=ignore,
            model_dtype=model_dtype,
            cfg=cfg,
        )
        del quantized_reference
        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()
    generated = 0
    max_new_artifacts = int(cfg.get("max_new_artifacts", 0))
    for record in design["artifacts"]:
        artifact_id = int(record["artifact_id"])
        if artifact_id in completed:
            continue
        started = time.perf_counter()
        quantized_model, weights = quantize_fn(
            model_name=model_source,
            model_revision=None,
            tokenizer=tokenizer,
            records=records,
            indices=record["calibration_indices"],
            seqlen=seqlen,
            seed=seed,
            device=device,
            pipeline=pipeline,
            group_size=group_size,
            bits=bits,
            ignore=ignore,
            model_dtype=model_dtype,
            cfg=cfg,
        )
        outputs = _output_scores(
            base_model, quantized_model, scored, device, int(cfg.get("output_chunk", 2))
        )
        del quantized_model
        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()
        reconstruction, layer_reconstruction = _reconstruction_scores(
            base_model,
            weights,
            scored,
            device,
            int(cfg.get("score_chunk", 4)),
            compute_dtype=str(cfg.get("reconstruction_compute_dtype", "model")),
        )
        _require_finite_scores(reconstruction, layer_reconstruction, outputs)
        if not track_changed_fraction:
            changed_fraction = None
        elif reference_weights is None:
            reference_weights = {name: value.clone() for name, value in weights.items()}
            changed_fraction = 0.0
        else:
            changed = sum(
                int(torch.count_nonzero(weights[name] != reference_weights[name]))
                for name in weights
            )
            changed_fraction = changed / sum(value.numel() for value in weights.values())
        row = {
            "artifact_id": artifact_id,
            "experiment_sha256": design["experiment_sha256"],
            "population_sha256": design["population_sha256"],
            "split": record["split"],
            "member_target_positions": record["member_target_positions"],
            "calibration_indices_sha256": record["calibration_indices_sha256"],
            "quantized_weights_sha256": _tensor_sha256(weights),
            "quantized_layers": sorted(weights),
            "changed_weight_fraction_vs_artifact0": changed_fraction,
            "artifact_reconstruction": reconstruction.tolist(),
            "layer_reconstruction": layer_reconstruction.tolist(),
            **{name: values.tolist() for name, values in outputs.items()},
            "seconds": time.perf_counter() - started,
        }
        with scores_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")
        del weights
        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(
            json.dumps(
                {
                    "artifact_id": artifact_id,
                    "split": record["split"],
                    "members": len(record["member_target_positions"]),
                    "changed_weight_fraction_vs_artifact0": changed_fraction,
                    "seconds": row["seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        generated += 1
        if max_new_artifacts > 0 and generated >= max_new_artifacts:
            break
    return manifest_path


def generate_gptq_attack(config: dict[str, Any], config_path: str | Path) -> Path:
    return _generate_llmcompressor_attack(
        config,
        config_path,
        section="gptq_attack",
        method="GPTQ",
        quantize_fn=_quantize_gptq,
    )


def evaluate_gptq_attack(config: dict[str, Any], config_path: str | Path) -> Path:
    """Evaluate with the shared population analysis used for the AutoRound replication."""
    return evaluate_autoround_attack({"autoround_attack": config["gptq_attack"]}, config_path)
