"""Held-out single-artifact calibration membership attack against a named PTQ library.

This module implements a fixed-margin calibration-membership design for named PTQ libraries. The
base model is never retrained, calibration records can be synthetic or dated natural text, and every
artifact score is computed from the quantized weights plus the public full-precision base.
"""

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

from .attack import (
    _bootstrap_metrics,
    _fixed_degree_membership,
    _metrics,
    _per_artifact_auroc_summary,
    _per_artifact_operating_summary,
    _per_target_auroc_summary,
    _shadow_calibrated_operating_point,
    _shadow_normalize_all,
)
from .config import resolve_path

OUTPUT_FEATURES = ("output_logit_mse", "output_kl", "output_logprob", "output_logprob_gap")
SCORE_FEATURES = ("artifact_reconstruction", *OUTPUT_FEATURES)


def _seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _indices_sha256(indices: list[int]) -> str:
    return hashlib.sha256(",".join(str(value) for value in indices).encode("ascii")).hexdigest()


def _tensor_sha256(tensors: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name in sorted(tensors):
        digest.update(name.encode("ascii"))
        raw = tensors[name].detach().contiguous().cpu().view(torch.uint8)
        digest.update(raw.numpy().tobytes())
    return digest.hexdigest()


def _word_token_ids(tokenizer: Any, pool_size: int, seed: int) -> np.ndarray:
    """Return ids of lowercase word-initial tokens, which behave like ordinary running text."""
    vocabulary = tokenizer.get_vocab()
    words = sorted(
        token
        for token in vocabulary
        if token.startswith("Ġ") and len(token) >= 5 and token[1:].isalpha() and token[1:].islower()
    )
    if len(words) < pool_size:
        raise RuntimeError(f"Tokenizer exposes only {len(words)} usable word tokens")
    rng = np.random.default_rng(seed)
    chosen = rng.choice(len(words), size=pool_size, replace=False)
    return np.asarray(
        [vocabulary[words[int(index)]] for index in sorted(chosen)], dtype=np.int64
    )


def synthetic_records(
    tokenizer: Any,
    *,
    count: int,
    seqlen: int,
    seed: int,
    vocabulary_size: int = 4096,
    topic_size: int = 96,
    concentration: float = 0.4,
    nonce_length: int = 8,
) -> torch.Tensor:
    """Build provenance-safe calibration records with controllable record distinctiveness.

    Every record draws a topic vocabulary of ``topic_size`` tokens and a Dirichlet token
    distribution. An optional record-unique nonce prefix makes disjointness especially transparent;
    setting ``nonce_length=0`` supplies the stricter no-canary control.

    Record distinctiveness is the key experimental knob. A small ``topic_size`` with low
    ``concentration`` gives each record a nearly private token support, which behaves like a canary.
    Setting ``topic_size`` to ``vocabulary_size`` with high ``concentration`` makes every record an
    independent draw from one shared distribution, which is the realistic homogeneous-corpus case
    and the harder test.
    """
    token_pool = _word_token_ids(tokenizer, vocabulary_size, seed)
    if nonce_length < 0:
        raise ValueError("Nonce length must be nonnegative")
    if seqlen <= nonce_length:
        raise ValueError("Sequence length must exceed the nonce prefix")
    records = np.empty((count, seqlen), dtype=np.int64)
    for record_id in range(count):
        rng = np.random.default_rng([seed, record_id])
        topic = rng.choice(token_pool, size=topic_size, replace=False)
        weights = rng.dirichlet(np.full(topic_size, concentration))
        body = rng.choice(topic, size=seqlen - nonce_length, replace=True, p=weights)
        nonce_digest = hashlib.sha256(f"calibtrace-{seed}-{record_id}".encode("ascii")).digest()
        if nonce_length > len(nonce_digest) // 4:
            raise ValueError("Nonce length exceeds the SHA-256 construction limit")
        nonce = token_pool[
            np.frombuffer(nonce_digest[: 4 * nonce_length], dtype=np.uint32) % len(token_pool)
        ]
        records[record_id] = np.concatenate((nonce, body))
    if len(np.unique(records, axis=0)) != count:
        raise RuntimeError("Synthetic calibration records are not unique")
    return torch.from_numpy(records)


def record_distribution(cfg: dict[str, Any]) -> dict[str, Any]:
    """Read the record-distinctiveness knobs, defaulting to the heterogeneous topic design."""
    return {
        "vocabulary_size": int(cfg.get("record_vocabulary_size", 4096)),
        "topic_size": int(cfg.get("record_topic_size", 96)),
        "concentration": float(cfg.get("record_concentration", 0.4)),
        "nonce_length": int(cfg.get("record_nonce_length", 8)),
    }


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonl_corpus_metadata(
    path: Path, *, published_after: str | None = None
) -> dict[str, Any]:
    """Summarize immutable provenance fields exposed by a JSONL text corpus."""
    published: list[str] = []
    identifiers: list[str] = []
    sources: set[str] = set()
    queries: set[str] = set()
    document_count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            published_value = payload.get("published")
            if published_after is not None:
                if not isinstance(published_value, str):
                    raise ValueError(
                        f"A publication timestamp is required for filtering at {path}:{line_number}"
                    )
                if published_value <= published_after:
                    continue
            document_count += 1
            value = published_value
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError(f"Invalid published field at {path}:{line_number}")
                published.append(value)
            identifier = payload.get("id")
            if isinstance(identifier, str):
                identifiers.append(identifier)
            source = payload.get("source")
            if isinstance(source, str):
                sources.add(source)
            query = payload.get("query")
            if isinstance(query, str):
                queries.add(query)
    metadata: dict[str, Any] = {
        "document_count": document_count,
        "identifier_sha256": _canonical_sha256(sorted(identifiers)),
        "sources": sorted(sources),
        "queries": sorted(queries),
    }
    if published:
        metadata["earliest_published"] = min(published)
        metadata["latest_published"] = max(published)
    if published_after is not None:
        metadata["row_filter_published_after"] = published_after
    return metadata


def text_records(
    tokenizer: Any,
    *,
    path: Path,
    count: int,
    seqlen: int,
    seed: int,
    text_field: str = "text",
    published_after: str | None = None,
) -> torch.Tensor:
    """Pack a deterministic post-cutoff JSONL corpus into disjoint token sequences."""
    documents: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if published_after is not None:
                published = payload.get("published")
                if not isinstance(published, str):
                    raise ValueError(
                        f"A publication timestamp is required for filtering at {path}:{line_number}"
                    )
                if published <= published_after:
                    continue
            value = payload.get(text_field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing nonempty {text_field!r} at {path}:{line_number}")
            documents.append(" ".join(value.split()))
    if not documents:
        raise ValueError(f"No text records found in {path}")
    rng = np.random.default_rng(seed)
    ordered = [documents[int(index)] for index in rng.permutation(len(documents))]
    separator = tokenizer.eos_token_id
    if separator is None:
        raise ValueError("Tokenizer has no EOS token for document separation")
    stream: list[int] = []
    required = count * seqlen
    for document in ordered:
        stream.extend(tokenizer.encode(document, add_special_tokens=False))
        stream.append(int(separator))
        if len(stream) >= required:
            break
    if len(stream) < required:
        raise ValueError(
            f"Corpus supplies {len(stream):,} tokens; {required:,} are required for "
            f"{count} records of length {seqlen}"
        )
    values = np.asarray(stream[:required], dtype=np.int64).reshape(count, seqlen)
    if len(np.unique(values, axis=0)) != count:
        raise RuntimeError("Text calibration records are not unique")
    return torch.from_numpy(values)


def load_record_pool(
    tokenizer: Any,
    *,
    cfg: dict[str, Any],
    config_path: str | Path,
    count: int,
    seqlen: int,
    seed: int,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Load a synthetic or post-cutoff natural-text calibration population."""
    source = str(cfg.get("record_source", "synthetic"))
    if source == "synthetic":
        distribution = record_distribution(cfg)
        records = synthetic_records(
            tokenizer,
            count=count,
            seqlen=seqlen,
            seed=seed,
            **distribution,
        )
        metadata = {"source": source, "distribution": distribution}
    elif source == "text_jsonl":
        if "record_text_path" not in cfg:
            raise ValueError("record_text_path is required when record_source=text_jsonl")
        path = resolve_path(config_path, cfg["record_text_path"])
        row_published_after = (
            str(cfg["record_row_published_after"])
            if cfg.get("record_row_published_after") is not None
            else None
        )
        records = text_records(
            tokenizer,
            path=path,
            count=count,
            seqlen=seqlen,
            seed=seed,
            text_field=str(cfg.get("record_text_field", "text")),
            published_after=row_published_after,
        )
        metadata = {
            "source": source,
            "path": str(path.resolve()),
            "sha256": _file_sha256(path),
            "text_field": str(cfg.get("record_text_field", "text")),
            **_jsonl_corpus_metadata(path, published_after=row_published_after),
        }
        published_after = cfg.get("record_published_after")
        if published_after is not None:
            earliest = metadata.get("earliest_published")
            if earliest is None or earliest <= str(published_after):
                raise ValueError(
                    f"Corpus earliest publication {earliest!r} does not postdate "
                    f"{published_after!r}"
                )
            metadata["required_published_after"] = str(published_after)
    else:
        raise ValueError(f"Unsupported record_source: {source!r}")
    metadata["seed"] = seed
    metadata["pool_sha256"] = hashlib.sha256(records.numpy().tobytes()).hexdigest()
    return records, metadata


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def attach_experiment_contract(
    design: dict[str, Any],
    *,
    record_metadata: dict[str, Any],
    contract: dict[str, Any],
) -> None:
    """Attach immutable hashes for the population and the quantizer execution contract."""
    population_payload = {
        "seed": design["seed"],
        "calibration_size": design["calibration_size"],
        "targets": design["targets"],
        "shadow_artifacts": design["shadow_artifacts"],
        "test_artifacts": design["test_artifacts"],
        "pool_size": design["pool_size"],
        "reference_records": design.get("reference_records", 0),
        "membership": design["membership"],
        "artifacts": [
            {
                "artifact_id": row["artifact_id"],
                "split": row["split"],
                "member_target_positions": row["member_target_positions"],
                "calibration_indices_sha256": row["calibration_indices_sha256"],
            }
            for row in design["artifacts"]
        ],
        "record_metadata": record_metadata,
    }
    design["schema_version"] = 2
    design["record_metadata"] = record_metadata
    design["record_pool_sha256"] = record_metadata["pool_sha256"]
    design["population_sha256"] = _canonical_sha256(population_payload)
    design["experiment_contract"] = contract
    design["experiment_sha256"] = _canonical_sha256(
        {"population_sha256": design["population_sha256"], "contract": contract}
    )


def prepare_resumable_scores(
    scores_path: Path,
    manifest_path: Path,
    design: dict[str, Any],
) -> tuple[set[int], dict[int, dict[str, Any]]]:
    """Validate every persisted row before allowing a generation run to resume."""
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as handle:
            previous = json.load(handle)
        if previous.get("experiment_sha256") != design["experiment_sha256"]:
            raise RuntimeError(
                f"Existing manifest {manifest_path} belongs to a different experiment. "
                "Use new output paths; completed evidence is never overwritten or reinterpreted."
            )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(design, handle, indent=2, sort_keys=True)
        handle.write("\n")
    rows: dict[int, dict[str, Any]] = {}
    if not scores_path.exists():
        return set(), rows
    expected = {int(row["artifact_id"]): row for row in design["artifacts"]}
    with scores_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            artifact_id = int(row["artifact_id"])
            if artifact_id in rows:
                raise RuntimeError(f"Duplicate artifact {artifact_id} at {scores_path}:{line_number}")
            if artifact_id not in expected:
                raise RuntimeError(f"Unexpected artifact {artifact_id} in {scores_path}")
            if row.get("experiment_sha256") != design["experiment_sha256"]:
                raise RuntimeError(
                    f"Score row {artifact_id} in {scores_path} has a stale or missing "
                    "experiment fingerprint"
                )
            contract_row = expected[artifact_id]
            for key in ("split", "member_target_positions", "calibration_indices_sha256"):
                if row.get(key) != contract_row[key]:
                    raise RuntimeError(
                        f"Score row {artifact_id} disagrees with the manifest field {key}"
                    )
            rows[artifact_id] = row
    return set(rows), rows


def make_population_design(
    *,
    calibration_size: int,
    targets: int,
    shadow_artifacts: int,
    test_artifacts: int,
    pool_size: int,
    seed: int,
    reference_records: int = 0,
) -> dict[str, Any]:
    """Lay out the artifact population.

    Pool positions are partitioned so that the first ``targets`` records are the tracked
    candidates, the next ``reference_records`` are public reference records held out of every
    calibration set, and the remainder supply backgrounds. Reference records give each artifact a
    difficulty estimate that never looks at another candidate, which keeps every membership
    decision candidate-local.
    """
    if targets >= calibration_size:
        raise ValueError("The target count must leave room for background calibration records")
    rng = np.random.default_rng(seed + 17_171)
    membership = np.concatenate(
        (
            _fixed_degree_membership(shadow_artifacts, targets, rng),
            _fixed_degree_membership(test_artifacts, targets, rng),
        ),
        axis=0,
    )
    background_pool = np.arange(targets + reference_records, pool_size, dtype=np.int64)
    artifacts: list[dict[str, Any]] = []
    for artifact_id in range(shadow_artifacts + test_artifacts):
        member_positions = np.flatnonzero(membership[artifact_id])
        artifact_rng = np.random.default_rng(seed + 1_000_003 * (artifact_id + 1))
        backgrounds = artifact_rng.choice(
            background_pool, calibration_size - len(member_positions), replace=False
        )
        calibration_indices = sorted(int(value) for value in [*member_positions, *backgrounds])
        artifacts.append(
            {
                "artifact_id": artifact_id,
                "split": "shadow" if artifact_id < shadow_artifacts else "test",
                "member_target_positions": [int(value) for value in member_positions],
                "calibration_indices": calibration_indices,
                "calibration_indices_sha256": _indices_sha256(calibration_indices),
            }
        )
    return {
        "seed": seed,
        "calibration_size": calibration_size,
        "targets": targets,
        "shadow_artifacts": shadow_artifacts,
        "test_artifacts": test_artifacts,
        "pool_size": pool_size,
        "reference_records": reference_records,
        "membership_design": "fixed_row_and_column_degrees",
        "membership": membership.astype(np.uint8).tolist(),
        "artifacts": artifacts,
    }


def _loader(records: torch.Tensor, indices: list[int], batch_size: int) -> DataLoader:
    examples = [
        {"input_ids": records[index], "attention_mask": torch.ones_like(records[index])}
        for index in indices
    ]
    return DataLoader(examples, batch_size=batch_size, shuffle=False, num_workers=0)


def _quantize(
    *,
    model_name: str,
    model_revision: str | None,
    model_dtype: torch.dtype,
    tokenizer: Any,
    loader: DataLoader,
    seqlen: int,
    calibration_size: int,
    batch_size: int,
    bits: int,
    iters: int,
    seed: int,
    device: torch.device,
) -> tuple[Any, dict[str, torch.Tensor]]:
    from auto_round import AutoRound
    from transformers import AutoModelForCausalLM

    _seed_all(seed)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        revision=model_revision,
        local_files_only=True,
        dtype=model_dtype,
        attn_implementation="eager",
    ).eval()
    compressor = AutoRound(
        model,
        tokenizer=tokenizer,
        scheme=f"W{bits}A16",
        dataset=loader,
        iters=iters,
        seqlen=seqlen,
        nsamples=calibration_size,
        batch_size=batch_size,
        device_map=0 if device.type == "cuda" else "cpu",
        enable_torch_compile=False,
        enable_deterministic_algorithms=True,
        seed=seed,
        low_cpu_mem_usage=False,
    )
    quantized_model, layer_config = compressor.quantize()
    modules = dict(quantized_model.named_modules())
    weights = {
        name: modules[name].weight.detach().to(device, model_dtype).clone()
        for name, settings in layer_config.items()
        if isinstance(settings, dict)
        and int(settings.get("bits", 16)) < 16
        and isinstance(modules.get(name), nn.Linear)
    }
    del compressor
    gc.collect()
    return quantized_model.to(device).eval(), weights


@torch.inference_mode()
def _reconstruction_scores(
    base_model: nn.Module,
    quantized_weights: dict[str, torch.Tensor],
    candidates: torch.Tensor,
    device: torch.device,
    chunk: int,
    compute_dtype: str = "model",
) -> tuple[np.ndarray, np.ndarray]:
    """Score candidates by the quantization residual energy they induce, layer by layer.

    Hooks evaluate ``||(Q_l - W_l) h_{l-1}(x)||^2`` while the full-precision activations are live,
    so nothing beyond the quantized weights and the public base model is ever required.
    """
    layer_names = sorted(quantized_weights)
    modules = dict(base_model.named_modules())
    totals: list[np.ndarray] = []
    layerwise: list[np.ndarray] = []
    for start in range(0, candidates.shape[0], chunk):
        batch = candidates[start : start + chunk].to(device)
        # OPT flattens hidden states to (batch * position, features) before its feedforward
        # layers, so every reduction is reshaped back against the candidate count explicitly.
        count = batch.shape[0]
        errors: dict[str, torch.Tensor] = {}
        energies: dict[str, torch.Tensor] = {}
        handles: list[torch.utils.hooks.RemovableHandle] = []

        def make_hook(name: str):
            def hook(module: nn.Module, args: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
                quantized_weight = quantized_weights[name]
                if quantized_weight.device != module.weight.device:
                    quantized_weight = quantized_weight.to(module.weight.device)
                    quantized_weights[name] = quantized_weight
                difference = quantized_weight.to(module.weight.dtype) - module.weight
                if compute_dtype == "float32":
                    residual = F.linear(args[0].float(), difference.float())
                elif compute_dtype == "model":
                    residual = F.linear(args[0], difference)
                else:
                    raise ValueError(f"Unsupported reconstruction compute dtype: {compute_dtype}")
                errors[name] = residual.float().reshape(count, -1).square().sum(1).double()
                energies[name] = output.float().reshape(count, -1).square().sum(1).double()

            return hook

        for name in layer_names:
            handles.append(modules[name].register_forward_hook(make_hook(name)))
        try:
            base_model(input_ids=batch, attention_mask=torch.ones_like(batch))
        finally:
            for handle in handles:
                handle.remove()
        error_stack = torch.stack([errors[name] for name in layer_names], dim=1)
        energy_stack = torch.stack([energies[name] for name in layer_names], dim=1)
        floor = torch.finfo(torch.float64).eps
        layerwise.append(-(error_stack / energy_stack.clamp_min(floor)).cpu().numpy())
        totals.append(
            -(error_stack.sum(1) / energy_stack.sum(1).clamp_min(floor)).cpu().numpy()
        )
    return np.concatenate(totals), np.concatenate(layerwise)


def _teacher_forced_logprob(log_probabilities: torch.Tensor, input_ids: torch.Tensor) -> torch.Tensor:
    return (
        log_probabilities[:, :-1]
        .gather(-1, input_ids[:, 1:].unsqueeze(-1))
        .squeeze(-1)
        .mean(1)
    )


@torch.inference_mode()
def _output_scores(
    base_model: nn.Module,
    quantized_model: nn.Module,
    candidates: torch.Tensor,
    device: torch.device,
    chunk: int,
) -> dict[str, np.ndarray]:
    """Matched one-query output-only baselines observed on the released quantized model."""
    quantized_device = quantized_model.get_input_embeddings().weight.device
    columns: dict[str, list[np.ndarray]] = {name: [] for name in OUTPUT_FEATURES}
    for start in range(0, candidates.shape[0], chunk):
        batch = candidates[start : start + chunk].to(device)
        mask = torch.ones_like(batch)
        base_logits = base_model(input_ids=batch, attention_mask=mask).logits.float()
        quantized_logits = (
            quantized_model(
                input_ids=batch.to(quantized_device), attention_mask=mask.to(quantized_device)
            )
            .logits.to(device)
            .float()
        )
        columns["output_logit_mse"].append(
            -(quantized_logits - base_logits).square().mean((1, 2)).double().cpu().numpy()
        )
        base_log_probabilities = base_logits.log_softmax(-1)
        del base_logits
        quantized_log_probabilities = quantized_logits.log_softmax(-1)
        del quantized_logits
        divergence = (
            base_log_probabilities.exp()
            * (base_log_probabilities - quantized_log_probabilities)
        ).sum(-1).mean(1)
        base_sequence = _teacher_forced_logprob(base_log_probabilities, batch)
        quantized_sequence = _teacher_forced_logprob(quantized_log_probabilities, batch)
        columns["output_kl"].append(-divergence.double().cpu().numpy())
        columns["output_logprob"].append(quantized_sequence.double().cpu().numpy())
        columns["output_logprob_gap"].append(
            (quantized_sequence - base_sequence).double().cpu().numpy()
        )
        del base_log_probabilities, quantized_log_probabilities
    return {name: np.concatenate(values) for name, values in columns.items()}


def generate_autoround_attack(config: dict[str, Any], config_path: str | Path) -> Path:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = config["autoround_attack"]
    if not os.environ.get("HF_HOME"):
        raise RuntimeError("Set HF_HOME to the project-local Hugging Face cache")
    seed = int(cfg["seed"])
    model_name = str(cfg["model"])
    model_revision = str(cfg["model_revision"]) if cfg.get("model_revision") else None
    model_dtype_name = str(cfg.get("model_dtype", "float16")).lower()
    model_dtypes = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if model_dtype_name not in model_dtypes:
        supported = ", ".join(sorted(model_dtypes))
        raise ValueError(
            f"Unsupported model_dtype {model_dtype_name!r}; choose one of {supported}"
        )
    model_dtype = model_dtypes[model_dtype_name]
    seqlen = int(cfg["sequence_length"])
    calibration_size = int(cfg["calibration_size"])
    targets = int(cfg["targets"])
    bits = int(cfg.get("bits", 4))
    iters = int(cfg["iters"])
    per_artifact_seed = bool(cfg.get("per_artifact_quantizer_seed", False))
    score_chunk = int(cfg.get("score_chunk", 4))
    output_chunk = int(cfg.get("output_chunk", 2))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    reference_records = int(cfg.get("reference_records", 0))
    _seed_all(seed)
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, revision=model_revision, local_files_only=True
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
    # Candidates and public reference records are scored together in a single pass.
    scored = records[: targets + reference_records]

    base_model = (
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
    design["model"] = model_name
    design["model_revision"] = model_revision
    design["model_dtype"] = model_dtype_name
    design["parameters"] = int(sum(p.numel() for p in base_model.parameters()))
    design["sequence_length"] = seqlen
    design["iters"] = iters
    design["bits"] = bits
    design["library"] = "auto-round"
    design["library_version"] = __import__("auto_round").__version__
    design["quantizer_seed"] = "per_artifact" if per_artifact_seed else "fixed"
    attach_experiment_contract(
        design,
        record_metadata=record_metadata,
        contract={
            "library": design["library"],
            "library_version": design["library_version"],
            "model": model_name,
            "model_revision": model_revision,
            "model_dtype": model_dtype_name,
            "bits": bits,
            "iters": iters,
            "batch_size": int(cfg["batch_size"]),
            "quantizer_seed": design["quantizer_seed"],
            "score_chunk": score_chunk,
            "output_chunk": output_chunk,
        },
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
        quantized_reference, reference_weights = _quantize(
            model_name=model_name,
            model_revision=model_revision,
            model_dtype=model_dtype,
            tokenizer=tokenizer,
            loader=_loader(records, first["calibration_indices"], int(cfg["batch_size"])),
            seqlen=seqlen,
            calibration_size=calibration_size,
            batch_size=int(cfg["batch_size"]),
            bits=bits,
            iters=iters,
            seed=seed + (1_000_003 if per_artifact_seed else 0),
            device=device,
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
        quantizer_seed = seed + (1_000_003 * (artifact_id + 1) if per_artifact_seed else 0)
        quantized_model, weights = _quantize(
            model_name=model_name,
            model_revision=model_revision,
            model_dtype=model_dtype,
            tokenizer=tokenizer,
            loader=_loader(records, record["calibration_indices"], int(cfg["batch_size"])),
            seqlen=seqlen,
            calibration_size=calibration_size,
            batch_size=int(cfg["batch_size"]),
            bits=bits,
            iters=iters,
            seed=quantizer_seed,
            device=device,
        )
        outputs = _output_scores(base_model, quantized_model, scored, device, output_chunk)
        del quantized_model
        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()
        reconstruction, layer_reconstruction = _reconstruction_scores(
            base_model, weights, scored, device, score_chunk
        )
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


def _load_scores(scores_path: Path, design: dict[str, Any]) -> dict[str, Any]:
    rows: dict[int, dict[str, Any]] = {}
    with scores_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[int(row["artifact_id"])] = row
    expected = len(design["artifacts"])
    missing = [index for index in range(expected) if index not in rows]
    if missing:
        raise RuntimeError(f"Missing scored artifacts: {missing}")
    ordered = [rows[index] for index in range(expected)]
    targets = int(design["targets"])
    reference_records = int(design.get("reference_records", 0))
    expected_scores = targets + reference_records
    if "experiment_sha256" in design:
        for index, row in enumerate(ordered):
            if row.get("experiment_sha256") != design["experiment_sha256"]:
                raise RuntimeError(f"Artifact {index} has a stale experiment fingerprint")
            expected_row = design["artifacts"][index]
            if row.get("calibration_indices_sha256") != expected_row["calibration_indices_sha256"]:
                raise RuntimeError(f"Artifact {index} was scored for different calibration indices")
    for index, row in enumerate(ordered):
        for name in SCORE_FEATURES:
            if len(row[name]) != expected_scores:
                raise RuntimeError(
                    f"Artifact {index} has {len(row[name])} {name} scores; "
                    f"the manifest requires {expected_scores}"
                )
    payload: dict[str, Any] = {"layer_names": ordered[0]["quantized_layers"]}
    for name in SCORE_FEATURES:
        values = np.asarray([row[name] for row in ordered], dtype=np.float64)
        payload[name] = values[:, :targets]
        payload[f"{name}__reference"] = values[:, targets:]
    layers = np.asarray([row["layer_reconstruction"] for row in ordered], dtype=np.float64)
    payload["layer_reconstruction"] = layers[:, :targets]
    payload["layer_reconstruction__reference"] = layers[:, targets:]
    payload["changed_weight_fraction"] = np.asarray(
        [
            np.nan
            if row["changed_weight_fraction_vs_artifact0"] is None
            else row["changed_weight_fraction_vs_artifact0"]
            for row in ordered
        ],
        dtype=np.float64,
    )
    payload["generation_seconds"] = np.asarray(
        [float(row["seconds"]) for row in ordered], dtype=np.float64
    )
    return payload


def _reference_correct(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Subtract each artifact's difficulty on public reference records held out of every set.

    The correction never looks at another candidate, so a membership decision stays candidate-local.
    """
    if reference.shape[1] == 0:
        return candidate
    return candidate - reference.mean(1, keepdims=True)


def _reference_utility(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Summarize predictive utility on public records excluded from every calibration set."""
    quantized = np.asarray(payload["output_logprob__reference"], dtype=np.float64)
    gap = np.asarray(payload["output_logprob_gap__reference"], dtype=np.float64)
    if quantized.shape[1] == 0:
        return None
    base = quantized - gap
    quantized_mean = float(quantized.mean())
    base_mean = float(base.mean())
    mean_change = float(gap.mean())
    artifact_changes = gap.mean(1)
    return {
        "protocol": "teacher-forced mean token log probability on public held-out references",
        "reference_decisions": int(quantized.size),
        "base_mean_logprob": base_mean,
        "quantized_mean_logprob": quantized_mean,
        "mean_logprob_change": mean_change,
        "artifact_logprob_change_std": float(artifact_changes.std(ddof=1)),
        "base_perplexity": float(np.exp(-base_mean)),
        "quantized_perplexity": float(np.exp(-quantized_mean)),
        "perplexity_ratio_quantized_over_base": float(np.exp(-mean_change)),
    }


def _shadow_standardize(values: np.ndarray, shadow_count: int) -> np.ndarray:
    """Standardize each candidate column with shadow-only statistics and no labels."""
    mean = values[:shadow_count].mean(0)
    scale = np.clip(values[:shadow_count].std(0), np.finfo(np.float64).eps, None)
    return (values - mean) / scale


def _shadow_layer_combination(
    layer_scores: np.ndarray,
    membership: np.ndarray,
    shadow_count: int,
    regularization_grid: tuple[float, ...],
) -> tuple[np.ndarray, float, float, np.ndarray]:
    """Fit a membership direction over layerwise scores using shadow artifacts only.

    A one-record calibration swap perturbs most weights, so the unweighted sum of layer residuals
    is dominated by quantization noise. Learning the weighting recovers the coherent component.
    The regularization strength is chosen by splitting the shadow artifacts in half, so no
    held-out artifact influences any part of the fit.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    standardized = np.stack(
        [
            _shadow_standardize(layer_scores[:, :, index], shadow_count)
            for index in range(layer_scores.shape[2])
        ],
        axis=-1,
    )
    layer_count = standardized.shape[2]
    shadow_features = standardized[:shadow_count].reshape(-1, layer_count)
    shadow_labels = membership[:shadow_count].reshape(-1)
    halves = (np.arange(shadow_count) < shadow_count // 2, np.arange(shadow_count) >= shadow_count // 2)
    best_strength, best_score = regularization_grid[0], -np.inf
    for strength in regularization_grid:
        folds = []
        for mask in halves:
            train = standardized[:shadow_count][mask].reshape(-1, layer_count)
            validate = standardized[:shadow_count][~mask].reshape(-1, layer_count)
            train_labels = membership[:shadow_count][mask].reshape(-1)
            validate_labels = membership[:shadow_count][~mask].reshape(-1)
            model = LogisticRegression(max_iter=5000, C=strength)
            model.fit(train, train_labels)
            folds.append(roc_auc_score(validate_labels, model.decision_function(validate)))
        if float(np.mean(folds)) > best_score:
            best_strength, best_score = strength, float(np.mean(folds))
    model = LogisticRegression(max_iter=5000, C=best_strength)
    model.fit(shadow_features, shadow_labels)
    decisions = model.decision_function(standardized.reshape(-1, layer_count))
    return (
        decisions.reshape(standardized.shape[:2]),
        best_strength,
        best_score,
        model.coef_.reshape(-1).astype(np.float64),
    )


def _fit_global_scalar(values: np.ndarray, labels: np.ndarray) -> tuple[float, float, float]:
    """Learn one score direction and calibration shared by every training candidate."""
    flattened = values.reshape(-1)
    flattened_labels = labels.reshape(-1).astype(bool)
    member_values = flattened[flattened_labels]
    nonmember_values = flattened[~flattened_labels]
    member_mean = float(member_values.mean())
    nonmember_mean = float(nonmember_values.mean())
    midpoint = (member_mean + nonmember_mean) / 2.0
    pooled_scale = float(
        np.sqrt((member_values.var(ddof=1) + nonmember_values.var(ddof=1)) / 2.0)
    )
    scale = max(pooled_scale, np.finfo(np.float64).eps)
    direction = 1.0 if member_mean >= nonmember_mean else -1.0
    return direction, midpoint, scale


def _apply_global_scalar(
    values: np.ndarray, calibration: tuple[float, float, float]
) -> np.ndarray:
    direction, midpoint, scale = calibration
    return direction * (values - midpoint) / scale


def _fit_global_vector(
    features: np.ndarray,
    labels: np.ndarray,
    regularization_grid: tuple[float, ...],
) -> tuple[Any, np.ndarray, np.ndarray, float, float]:
    """Fit a globally standardized logistic attack with artifact-wise validation."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    artifact_count = features.shape[0]
    halves = (
        np.arange(artifact_count) < artifact_count // 2,
        np.arange(artifact_count) >= artifact_count // 2,
    )
    best_strength, best_score = regularization_grid[0], -np.inf
    for strength in regularization_grid:
        fold_scores = []
        for train_rows in halves:
            train = features[train_rows].reshape(-1, features.shape[-1])
            validate = features[~train_rows].reshape(-1, features.shape[-1])
            train_labels = labels[train_rows].reshape(-1)
            validate_labels = labels[~train_rows].reshape(-1)
            mean = train.mean(0)
            scale = np.clip(train.std(0), np.finfo(np.float64).eps, None)
            model = LogisticRegression(max_iter=5000, C=strength)
            model.fit((train - mean) / scale, train_labels)
            fold_scores.append(
                roc_auc_score(validate_labels, model.decision_function((validate - mean) / scale))
            )
        score = float(np.mean(fold_scores))
        if score > best_score:
            best_strength, best_score = strength, score
    flattened = features.reshape(-1, features.shape[-1])
    mean = flattened.mean(0)
    scale = np.clip(flattened.std(0), np.finfo(np.float64).eps, None)
    model = LogisticRegression(max_iter=5000, C=best_strength)
    model.fit((flattened - mean) / scale, labels.reshape(-1))
    return model, mean, scale, best_strength, best_score


def _apply_global_vector(
    model: Any, mean: np.ndarray, scale: np.ndarray, features: np.ndarray
) -> np.ndarray:
    flattened = features.reshape(-1, features.shape[-1])
    decisions = model.decision_function((flattened - mean) / scale)
    return decisions.reshape(features.shape[:2])


def _candidate_crossfit(
    *,
    corrected: dict[str, np.ndarray],
    corrected_layers: np.ndarray,
    membership: np.ndarray,
    shadow_count: int,
    regularization_grid: tuple[float, ...],
    folds: int,
    seed: int,
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Evaluate candidates excluded from every fitted direction, scale, and layer weight."""
    if folds < 2:
        raise ValueError("Candidate cross-fitting requires at least two folds")
    target_count = membership.shape[1]
    if folds > target_count:
        raise ValueError("Candidate cross-fitting has more folds than candidates")
    rng = np.random.default_rng(seed)
    candidate_folds = np.array_split(rng.permutation(target_count), folds)
    test_labels = membership[shadow_count:]
    scalar_names = ("artifact_reconstruction", *OUTPUT_FEATURES)
    predictions = {
        name: np.full(test_labels.shape, np.nan, dtype=np.float64) for name in scalar_names
    }
    predictions["artifact_layer_combination"] = np.full(
        test_labels.shape, np.nan, dtype=np.float64
    )
    predictions["output_combination"] = np.full(test_labels.shape, np.nan, dtype=np.float64)
    selected_artifact = np.full(test_labels.shape, np.nan, dtype=np.float64)
    selected_output = np.full(test_labels.shape, np.nan, dtype=np.float64)
    selections: list[dict[str, Any]] = []
    output_tensor = np.stack([corrected[name] for name in OUTPUT_FEATURES], axis=-1)

    for fold_index, held_out in enumerate(candidate_folds):
        training = np.setdiff1d(np.arange(target_count), held_out, assume_unique=True)
        training_labels = membership[:shadow_count, training]
        training_scores: dict[str, float] = {}
        for name in scalar_names:
            calibration = _fit_global_scalar(
                corrected[name][:shadow_count, training], training_labels
            )
            predictions[name][:, held_out] = _apply_global_scalar(
                corrected[name][shadow_count:, held_out], calibration
            )
            training_predictions = _apply_global_scalar(
                corrected[name][:shadow_count, training], calibration
            )
            training_scores[name] = _metrics(
                training_labels.reshape(-1), training_predictions.reshape(-1)
            )["auroc"]

        layer_model, layer_mean, layer_scale, layer_strength, layer_cv = _fit_global_vector(
            corrected_layers[:shadow_count, training], training_labels, regularization_grid
        )
        predictions["artifact_layer_combination"][:, held_out] = _apply_global_vector(
            layer_model,
            layer_mean,
            layer_scale,
            corrected_layers[shadow_count:, held_out],
        )
        output_model, output_mean, output_scale, output_strength, output_cv = _fit_global_vector(
            output_tensor[:shadow_count, training], training_labels, regularization_grid
        )
        predictions["output_combination"][:, held_out] = _apply_global_vector(
            output_model,
            output_mean,
            output_scale,
            output_tensor[shadow_count:, held_out],
        )
        training_scores["artifact_layer_combination"] = layer_cv
        training_scores["output_combination"] = output_cv
        artifact_key = max(
            ("artifact_reconstruction", "artifact_layer_combination"),
            key=lambda name: training_scores[name],
        )
        output_key = max(
            (*OUTPUT_FEATURES, "output_combination"),
            key=lambda name: training_scores[name],
        )
        selected_artifact[:, held_out] = predictions[artifact_key][:, held_out]
        selected_output[:, held_out] = predictions[output_key][:, held_out]
        held_out_payload = np.ascontiguousarray(
            np.stack(
                (
                    selected_artifact[:, held_out],
                    selected_output[:, held_out],
                ),
                axis=-1,
            ),
            dtype=np.float64,
        )
        selections.append(
            {
                "fold": fold_index,
                "training_candidates": training.tolist(),
                "held_out_candidates": held_out.tolist(),
                "selected_artifact_feature": artifact_key,
                "selected_output_feature": output_key,
                "layer_regularization": layer_strength,
                "layer_validation_auroc": layer_cv,
                "output_regularization": output_strength,
                "output_validation_auroc": output_cv,
                "held_out_prediction_sha256": hashlib.sha256(
                    held_out_payload.tobytes()
                ).hexdigest(),
            }
        )

    if any(np.isnan(values).any() for values in predictions.values()):
        raise RuntimeError("Candidate cross-fitting left unevaluated scores")
    predictions["selected_artifact"] = selected_artifact
    predictions["selected_output"] = selected_output
    flattened_labels = test_labels.reshape(-1).astype(np.uint8)
    metrics = {
        name: _metrics(flattened_labels, values.reshape(-1))
        for name, values in predictions.items()
    }
    per_artifact = {
        name: _per_artifact_auroc_summary(test_labels, values)
        for name, values in predictions.items()
    }
    bootstrap = _bootstrap_metrics(
        test_labels,
        predictions,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
        artifact_key="selected_artifact",
        baseline_key="selected_output",
    )
    return {
        "protocol": (
            "candidate-fold cross-fitting: all score directions, scales, feature combinations, "
            "and feature choices exclude the evaluated candidate"
        ),
        "normalization": (
            "one fold-global direction, midpoint, and scale pooled over shadow scores from "
            "training-fold candidates only"
        ),
        "excluded_identity_shadow_scores_used": False,
        "excluded_identity_test_scores_used_for_fitting": False,
        "folds": folds,
        "seed": seed,
        "selections": selections,
        "metrics": metrics,
        "per_artifact_auroc": per_artifact,
        "cluster_bootstrap": bootstrap,
        "artifact_minus_output_auroc": (
            metrics["selected_artifact"]["auroc"] - metrics["selected_output"]["auroc"]
        ),
    }


def _fixed_degree_randomization_test(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Test AUROC after permuting artifact and candidate identities.

    Two-way permutations preserve the observed binary matrix exactly, including every row and
    column margin, while breaking its alignment with the score matrix.
    """
    from sklearn.metrics import roc_auc_score

    observed = float(roc_auc_score(labels.reshape(-1), scores.reshape(-1)))
    rng = np.random.default_rng(seed)
    null = np.empty(replicates, dtype=np.float64)
    for index in range(replicates):
        permuted = labels[rng.permutation(labels.shape[0])][
            :, rng.permutation(labels.shape[1])
        ]
        null[index] = roc_auc_score(permuted.reshape(-1), scores.reshape(-1))
    return {
        "observed_auroc": observed,
        "replicates": replicates,
        "p_value_greater_equal": float((1 + np.count_nonzero(null >= observed)) / (replicates + 1)),
        "null_mean": float(null.mean()),
        "null_lower_95": float(np.quantile(null, 0.025)),
        "null_upper_95": float(np.quantile(null, 0.975)),
    }


def evaluate_autoround_attack(config: dict[str, Any], config_path: str | Path) -> Path:
    cfg = config["autoround_attack"]
    manifest_path = resolve_path(config_path, cfg["manifest"])
    with manifest_path.open("r", encoding="utf-8") as handle:
        design = json.load(handle)
    payload = _load_scores(resolve_path(config_path, cfg["scores"]), design)
    membership = np.asarray(design["membership"], dtype=bool)
    shadow_count = int(design["shadow_artifacts"])
    grid = tuple(float(value) for value in cfg.get("logistic_regularization", (1.0, 0.1, 0.01, 0.001)))

    corrected = {
        name: _reference_correct(payload[name], payload[f"{name}__reference"])
        for name in SCORE_FEATURES
    }
    reference_layers = payload["layer_reconstruction__reference"]
    corrected_layers = payload["layer_reconstruction"]
    if reference_layers.shape[1]:
        corrected_layers = corrected_layers - reference_layers.mean(1, keepdims=True)
    combination, strength, shadow_split_auroc, layer_coefficients = _shadow_layer_combination(
        corrected_layers, membership, shadow_count, grid
    )
    corrected["artifact_layer_combination"] = combination
    output_tensor = np.stack([corrected[name] for name in OUTPUT_FEATURES], axis=-1)
    (
        output_combination,
        output_strength,
        output_shadow_split_auroc,
        output_coefficients,
    ) = _shadow_layer_combination(output_tensor, membership, shadow_count, grid)
    corrected["output_combination"] = output_combination
    output_feature_names = (*OUTPUT_FEATURES, "output_combination")
    feature_names = (
        "artifact_reconstruction",
        "artifact_layer_combination",
        *output_feature_names,
    )

    normalized_all = {
        name: _shadow_normalize_all(corrected[name], membership, shadow_count)
        for name in feature_names
    }
    normalized = {name: values[shadow_count:] for name, values in normalized_all.items()}
    shadow_labels_matrix = membership[:shadow_count]
    test_labels_matrix = membership[shadow_count:]
    shadow_labels = shadow_labels_matrix.reshape(-1).astype(np.uint8)
    test_labels = test_labels_matrix.reshape(-1).astype(np.uint8)
    point_metrics = {
        name: _metrics(test_labels, values.reshape(-1)) for name, values in normalized.items()
    }
    per_artifact = {
        name: _per_artifact_auroc_summary(test_labels_matrix, values)
        for name, values in normalized.items()
    }
    fit_free_scores = {
        "raw_fixed_formula": payload["artifact_reconstruction"][shadow_count:],
        "reference_corrected_fixed_formula": corrected["artifact_reconstruction"][shadow_count:],
    }
    fit_free_metrics = {
        name: _metrics(test_labels, values.reshape(-1))
        for name, values in fit_free_scores.items()
    }
    fit_free_bootstrap = _bootstrap_metrics(
        test_labels_matrix,
        fit_free_scores,
        replicates=int(cfg["bootstrap_replicates"]),
        seed=int(cfg["bootstrap_seed"]) + 83,
        artifact_key="reference_corrected_fixed_formula",
        baseline_key="raw_fixed_formula",
    )
    # Both the artifact score and the output baseline it must beat are chosen on shadow artifacts
    # only, so the comparison never sees a held-out label.
    shadow_metrics = {
        name: _metrics(shadow_labels, normalized_all[name][:shadow_count].reshape(-1))
        for name in feature_names
    }
    baseline_key = max(output_feature_names, key=lambda name: shadow_metrics[name]["auroc"])
    artifact_key = max(
        ("artifact_reconstruction", "artifact_layer_combination"),
        key=lambda name: shadow_metrics[name]["auroc"],
    )
    operating_points = {
        name: {
            "1pct_target_fpr": _shadow_calibrated_operating_point(
                shadow_labels,
                normalized_all[name][:shadow_count].reshape(-1),
                test_labels,
                values.reshape(-1),
                0.01,
            ),
        }
        for name, values in normalized.items()
    }
    selected_artifact_threshold = operating_points[artifact_key]["1pct_target_fpr"]["threshold"]
    per_artifact_operating = _per_artifact_operating_summary(
        test_labels_matrix,
        normalized[artifact_key],
        selected_artifact_threshold,
    )
    per_target = {
        name: _per_target_auroc_summary(test_labels_matrix, values)
        for name, values in normalized.items()
    }
    layer_names = payload["layer_names"]
    layerwise = []
    for layer_index, layer_name in enumerate(layer_names):
        layer_all = _shadow_normalize_all(
            corrected_layers[:, :, layer_index], membership, shadow_count
        )
        layerwise.append(
            {
                "layer": layer_name,
                **_metrics(test_labels, layer_all[shadow_count:].reshape(-1)),
            }
        )
    layerwise.sort(key=lambda values: values["auroc"], reverse=True)
    bootstrap = _bootstrap_metrics(
        test_labels_matrix,
        normalized,
        replicates=int(cfg["bootstrap_replicates"]),
        seed=int(cfg["bootstrap_seed"]),
        baseline_key=baseline_key,
        artifact_key=artifact_key,
    )
    candidate_generalization = _candidate_crossfit(
        corrected=corrected,
        corrected_layers=corrected_layers,
        membership=membership,
        shadow_count=shadow_count,
        regularization_grid=grid,
        folds=int(cfg.get("candidate_crossfit_folds", 2)),
        seed=int(cfg.get("candidate_crossfit_seed", int(design["seed"]) + 41)),
        bootstrap_replicates=int(cfg["bootstrap_replicates"]),
        bootstrap_seed=int(cfg["bootstrap_seed"]) + 41,
    )
    randomization = _fixed_degree_randomization_test(
        test_labels_matrix,
        normalized[artifact_key],
        replicates=int(cfg.get("randomization_replicates", 1000)),
        seed=int(cfg.get("randomization_seed", int(cfg["bootstrap_seed"]) + 73)),
    )
    difference_key = f"artifact_minus_{baseline_key}_auroc"
    changed_values = payload["changed_weight_fraction"][1:]
    mean_changed_fraction = (
        float(np.nanmean(changed_values)) if np.isfinite(changed_values).any() else None
    )
    generation_seconds = payload["generation_seconds"]
    result = {
        "threat_model": (
            f"public base, released {design['library']} W{design['bits']} artifact, "
            "one held-out artifact"
        ),
        "library": design["library"],
        "library_version": design["library_version"],
        "method": design.get("method", "AutoRound"),
        "model": design["model"],
        "model_revision": design.get("model_revision"),
        "model_dtype": design.get("model_dtype", "float16"),
        "parameters": design["parameters"],
        "bits": design["bits"],
        "calibration_size": design["calibration_size"],
        "sequence_length": design["sequence_length"],
        "iters": design["iters"],
        "quantizer_seed": design["quantizer_seed"],
        "shadow_artifacts": shadow_count,
        "test_artifacts": int(membership.shape[0] - shadow_count),
        "targets": int(membership.shape[1]),
        "test_decisions": int(test_labels.size),
        "test_members": int(test_labels.sum()),
        "test_nonmembers": int((1 - test_labels).sum()),
        "empirical_test_fpr_resolution": float(1 / (1 - test_labels).sum()),
        "reference_records": int(design.get("reference_records", 0)),
        "reference_utility": _reference_utility(payload),
        "generation_runtime": {
            "artifacts": int(generation_seconds.size),
            "total_seconds": float(generation_seconds.sum()),
            "mean_seconds_per_artifact": float(generation_seconds.mean()),
            "minimum_seconds": float(generation_seconds.min()),
            "maximum_seconds": float(generation_seconds.max()),
        },
        "selected_output_baseline": baseline_key,
        "selected_artifact_feature": artifact_key,
        "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
        "layer_combination": {
            "regularization": strength,
            "shadow_split_auroc": shadow_split_auroc,
            "coefficients": {
                name: float(value)
                for name, value in zip(payload["layer_names"], layer_coefficients, strict=True)
            },
        },
        "output_combination": {
            "regularization": output_strength,
            "shadow_split_auroc": output_shadow_split_auroc,
            "features": list(OUTPUT_FEATURES),
            "coefficients": {
                name: float(value)
                for name, value in zip(OUTPUT_FEATURES, output_coefficients, strict=True)
            },
        },
        "shadow_metrics": shadow_metrics,
        "metrics": point_metrics,
        "shadow_calibrated_operating_points": operating_points,
        "per_target_auroc": per_target,
        "per_artifact_auroc": per_artifact,
        "selected_artifact_per_artifact_operating_point": per_artifact_operating,
        "fit_free_fixed_score": {
            "protocol": (
                "predefined negative residual-energy score; no fitted direction, location, "
                "scale, layer combination, regularization, or feature selection"
            ),
            "metrics": fit_free_metrics,
            "per_artifact_auroc": {
                name: _per_artifact_auroc_summary(test_labels_matrix, values)
                for name, values in fit_free_scores.items()
            },
            "cluster_bootstrap": fit_free_bootstrap,
        },
        "layerwise_artifact_reconstruction": layerwise,
        "mean_changed_weight_fraction_vs_artifact0": mean_changed_fraction,
        "cluster_bootstrap": bootstrap,
        "candidate_generalization": candidate_generalization,
        "fixed_degree_randomization_test": randomization,
        "population_sha256": design.get("population_sha256"),
        "experiment_sha256": design.get("experiment_sha256"),
        "record_metadata": design.get("record_metadata"),
        difference_key: point_metrics[artifact_key]["auroc"] - point_metrics[baseline_key]["auroc"],
    }
    report_path = resolve_path(config_path, cfg["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("# CalibTrace named-library attack report\n\n")
        handle.write(
            f"Library `{result['library']}` {result['library_version']} quantizes "
            f"`{result['model']}` to W{result['bits']}A16 from {result['shadow_artifacts']} shadow "
            f"and {result['test_artifacts']} held-out calibration assignments of "
            f"N={result['calibration_size']} sequences of {result['sequence_length']} tokens, "
            f"tracking {result['targets']} candidate records.\n\n"
        )
        handle.write("| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |\n")
        handle.write("|---|---:|---:|---:|\n")
        for name, values in point_metrics.items():
            handle.write(
                f"| {name} | {values['auroc']:.4f} | {values['tpr_at_1pct_fpr']:.4f} | "
                f"{values['tpr_at_0_1pct_fpr']:.4f} |\n"
            )
        interval = bootstrap[difference_key]
        handle.write(
            f"\nSelected artifact feature `{artifact_key}` minus selected output baseline "
            f"`{baseline_key}`: {result[difference_key]:.4f} AUROC, crossed-bootstrap 95% interval "
            f"[{interval['lower_95']:.4f}, {interval['upper_95']:.4f}]. Both features were selected "
            f"on shadow artifacts only. A negative value indicates that the selected output "
            f"feature has higher AUROC in this configuration.\n\n"
        )
        utility = result["reference_utility"]
        if utility is not None:
            handle.write("## Public-reference utility\n\n")
            handle.write(
                f"Across {utility['reference_decisions']} calibration-excluded reference scores, "
                f"mean token log probability changes by {utility['mean_logprob_change']:.6f}; "
                f"the corresponding perplexity ratio is "
                f"{utility['perplexity_ratio_quantized_over_base']:.6f}.\n\n"
            )
        runtime = result["generation_runtime"]
        handle.write("## Generation runtime\n\n")
        handle.write(
            f"The {runtime['artifacts']} quantize-and-score jobs took "
            f"{runtime['total_seconds'] / 60:.1f} minutes in aggregate, with mean "
            f"{runtime['mean_seconds_per_artifact']:.1f} seconds per artifact.\n\n"
        )
        handle.write("## Layerwise localization\n\n")
        handle.write("| Layer | AUROC | ROC TPR @ FPR<=1% |\n|---|---:|---:|\n")
        for values in layerwise[:12]:
            handle.write(
                f"| {values['layer']} | {values['auroc']:.4f} | {values['tpr_at_1pct_fpr']:.4f} |\n"
            )
        held_out = candidate_generalization["metrics"]
        handle.write("\n## Unseen-candidate generalization\n\n")
        handle.write(
            "Candidate-fold cross-fitting uses one global direction, midpoint, and scale pooled "
            "over the other candidates. The evaluated candidate contributes no shadow score, "
            "label, normalization statistic, feature weight, or selection decision.\n\n"
        )
        handle.write("| Feature | AUROC | ROC TPR @ FPR<=1% |\n|---|---:|---:|\n")
        for name in ("artifact_reconstruction", "artifact_layer_combination", "selected_artifact", "selected_output"):
            values = held_out[name]
            handle.write(
                f"| {name} | {values['auroc']:.4f} | {values['tpr_at_1pct_fpr']:.4f} |\n"
            )
        handle.write("\n## Fit-free fixed score\n\n")
        handle.write(
            "This ablation applies the predefined negative residual-energy score directly, with "
            "zero learned direction, normalization, layer weighting, or feature selection.\n\n"
        )
        handle.write("| Variant | AUROC | ROC TPR @ FPR<=1% |\n|---|---:|---:|\n")
        for name, values in fit_free_metrics.items():
            handle.write(
                f"| {name} | {values['auroc']:.4f} | {values['tpr_at_1pct_fpr']:.4f} |\n"
            )
        artifact_values = per_artifact[artifact_key]
        crossfit_artifact_values = candidate_generalization["per_artifact_auroc"][
            "selected_artifact"
        ]
        operating_tpr = per_artifact_operating["tpr"]
        operating_fpr = per_artifact_operating["fpr"]
        handle.write("\n## Held-out artifact distribution\n\n")
        handle.write(
            f"For {artifact_key}, per-artifact AUROC has minimum "
            f"{artifact_values['minimum']:.4f}, median {artifact_values['median']:.4f}, "
            f"and maximum {artifact_values['maximum']:.4f} across "
            f"{artifact_values['artifacts']} test artifacts.\n\n"
        )
        handle.write(
            "Under candidate cross-fitting, selected-artifact per-artifact AUROC has minimum "
            f"{crossfit_artifact_values['minimum']:.4f}, median "
            f"{crossfit_artifact_values['median']:.4f}, and maximum "
            f"{crossfit_artifact_values['maximum']:.4f}. At the global threshold fixed from "
            "shadow nonmembers for 1% FPR, per-artifact TPR ranges from "
            f"{operating_tpr['minimum']:.4f} to {operating_tpr['maximum']:.4f}, and FPR ranges "
            f"from {operating_fpr['minimum']:.4f} to {operating_fpr['maximum']:.4f}.\n\n"
        )
        handle.write(
            f"\nFixed-degree randomization test for the selected artifact score: "
            f"p={randomization['p_value_greater_equal']:.6f} "
            f"({randomization['replicates']} random assignments).\n"
        )
        handle.write("\nFull metrics and metadata:\n\n```json\n")
        handle.write(json.dumps(result, indent=2, sort_keys=True))
        handle.write("\n```\n")
    with report_path.with_suffix(".json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return report_path
