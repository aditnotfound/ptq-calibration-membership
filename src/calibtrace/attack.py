from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score, roc_curve
from torch import nn
from torch.utils.data import DataLoader

from .artifact_io import load_artifact, save_artifact
from .config import resolve_path
from .data import CIFAR100Dataset, load_datasets, subset_by_source_indices
from .model import quantizable_modules
from .quantization import Artifact, apply_artifact, gptq_artifact
from .repro import default_device, seed_everything
from .train import load_base_model


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _indices_sha256(indices: list[int]) -> str:
    payload = ",".join(str(value) for value in indices).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _fixed_degree_membership(rows: int, columns: int, rng: np.random.Generator) -> np.ndarray:
    """Return a randomized binary matrix with all row and column margins fixed at one half."""
    if rows % 2 or columns % 2:
        raise ValueError("Fixed-degree membership requires even artifact and target counts")
    membership = np.fromfunction(
        lambda row, column: (row + column) % 2 == 0,
        (rows, columns),
        dtype=int,
    ).astype(bool)
    # Random 2x2 switches preserve every margin while breaking the initial checkerboard structure.
    accepted = 0
    target_switches = 20 * rows * columns
    attempts = 0
    max_attempts = 20 * target_switches
    while accepted < target_switches and attempts < max_attempts:
        row_a, row_b = rng.choice(rows, 2, replace=False)
        column_a, column_b = rng.choice(columns, 2, replace=False)
        diagonal = membership[[row_a, row_b], [column_a, column_b]]
        off_diagonal = membership[[row_a, row_b], [column_b, column_a]]
        if bool(diagonal[0]) == bool(diagonal[1]) and bool(off_diagonal[0]) == bool(off_diagonal[1]):
            if bool(diagonal[0]) != bool(off_diagonal[0]):
                membership[row_a, column_a] = ~membership[row_a, column_a]
                membership[row_b, column_b] = ~membership[row_b, column_b]
                membership[row_a, column_b] = ~membership[row_a, column_b]
                membership[row_b, column_a] = ~membership[row_b, column_a]
                accepted += 1
        attempts += 1
    if accepted < target_switches:
        raise RuntimeError("Could not randomize the fixed-degree membership matrix")
    if not np.all(membership.sum(axis=1) == columns // 2):
        raise RuntimeError("Fixed-degree membership row margins changed")
    if not np.all(membership.sum(axis=0) == rows // 2):
        raise RuntimeError("Fixed-degree membership column margins changed")
    return membership


def make_population_design(
    calibration: CIFAR100Dataset,
    *,
    calibration_size: int,
    targets: int,
    shadow_artifacts: int,
    test_artifacts: int,
    seed: int,
    fixed_target_count_per_artifact: bool = False,
) -> dict[str, Any]:
    if shadow_artifacts % 2 or test_artifacts % 2:
        raise ValueError("Shadow and test artifact counts must be even for exact target balance")
    if targets >= calibration_size:
        raise ValueError("The target count must leave room for background calibration records")
    rng = np.random.default_rng(seed + 17_171)
    pool = np.asarray(calibration.indices, dtype=np.int64)
    labels = calibration.labels
    available_classes = rng.permutation(np.unique(labels[pool]))
    if targets > len(available_classes):
        raise ValueError("This design selects at most one target per class")
    target_indices: list[int] = []
    for class_id in available_classes[:targets]:
        class_pool = pool[labels[pool] == class_id]
        target_indices.append(int(rng.choice(class_pool)))

    total_artifacts = shadow_artifacts + test_artifacts
    if fixed_target_count_per_artifact:
        membership = np.concatenate(
            (
                _fixed_degree_membership(shadow_artifacts, targets, rng),
                _fixed_degree_membership(test_artifacts, targets, rng),
            ),
            axis=0,
        )
    else:
        membership = np.zeros((total_artifacts, targets), dtype=bool)
        for target_position in range(targets):
            shadow_rows = rng.choice(shadow_artifacts, shadow_artifacts // 2, replace=False)
            test_rows = shadow_artifacts + rng.choice(test_artifacts, test_artifacts // 2, replace=False)
            membership[shadow_rows, target_position] = True
            membership[test_rows, target_position] = True

    target_set = set(target_indices)
    background_pool = np.asarray(
        [int(index) for index in pool if int(index) not in target_set], dtype=np.int64
    )
    artifacts: list[dict[str, Any]] = []
    for artifact_id in range(total_artifacts):
        member_positions = np.flatnonzero(membership[artifact_id])
        member_targets = [target_indices[int(position)] for position in member_positions]
        background_count = calibration_size - len(member_targets)
        artifact_rng = np.random.default_rng(seed + 1_000_003 * (artifact_id + 1))
        backgrounds = [
            int(index)
            for index in artifact_rng.choice(background_pool, background_count, replace=False)
        ]
        calibration_indices = sorted([*member_targets, *backgrounds])
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
        "target_indices": target_indices,
        "target_labels": [int(labels[index]) for index in target_indices],
        "shadow_artifacts": shadow_artifacts,
        "test_artifacts": test_artifacts,
        "membership_design": (
            "fixed_row_and_column_degrees"
            if fixed_target_count_per_artifact
            else "independently_balanced_columns"
        ),
        "membership": membership.astype(np.uint8).tolist(),
        "artifacts": artifacts,
    }


def _calibration_loader(
    calibration: CIFAR100Dataset,
    indices: list[int],
    *,
    batch_size: int,
    device: torch.device,
) -> DataLoader:
    return DataLoader(
        subset_by_source_indices(calibration, indices),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )


def generate_attack_population(config: dict[str, Any], config_path: str | Path) -> Path:
    seed = int(config["seed"])
    seed_everything(seed)
    device = default_device()
    paths = config["paths"]
    data_cfg = config["data"]
    quant_cfg = config["quantization"]
    attack_cfg = config["attack"]
    _, calibration, _, manifest = load_datasets(
        resolve_path(config_path, paths["data_dir"]),
        train_per_class=int(data_cfg["train_per_class"]),
        calibration_per_class=int(data_cfg["calibration_per_class"]),
        split_seed=int(data_cfg["split_seed"]),
    )
    checkpoint_path = resolve_path(config_path, paths["base_checkpoint"])
    model = load_base_model(checkpoint_path, device)
    design = make_population_design(
        calibration,
        calibration_size=int(attack_cfg["calibration_size"]),
        targets=int(attack_cfg["targets"]),
        shadow_artifacts=int(attack_cfg["shadow_artifacts"]),
        test_artifacts=int(attack_cfg["test_artifacts"]),
        seed=seed,
        fixed_target_count_per_artifact=bool(
            attack_cfg.get("fixed_target_count_per_artifact", False)
        ),
    )
    artifact_root = resolve_path(config_path, attack_cfg["artifact_dir"])
    manifest_path = resolve_path(config_path, attack_cfg["manifest"])
    artifact_root.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    design["base_checkpoint"] = str(checkpoint_path.resolve())
    design["base_checkpoint_sha256"] = _sha256(checkpoint_path)
    design["split_manifest_sha256"] = manifest.to_json()["sha256"]
    design["quantizer"] = {
        "method": "GPTQ-style",
        "bits": int(quant_cfg["bits"]),
        "damping": float(quant_cfg["damping"]),
        "block_size": int(quant_cfg["block_size"]),
        "hessian_patches_per_image": int(quant_cfg["hessian_patches_per_image"]),
        "fixed_grid": True,
        "batchnorm_recalibration": False,
    }

    first_artifact: Artifact | None = None
    for position, record in enumerate(design["artifacts"], start=1):
        started = time.perf_counter()
        artifact_id = int(record["artifact_id"])
        artifact_path = artifact_root / f"artifact_{artifact_id:03d}.npz"
        if artifact_path.exists():
            artifact, _ = load_artifact(artifact_path)
            digest = _sha256(artifact_path)
            resumed = True
        else:
            loader = _calibration_loader(
                calibration,
                record["calibration_indices"],
                batch_size=int(attack_cfg["calibration_batch_size"]),
                device=device,
            )
            artifact = gptq_artifact(
                model,
                loader,
                bits=int(quant_cfg["bits"]),
                damping=float(quant_cfg["damping"]),
                block_size=int(quant_cfg["block_size"]),
                patches_per_image=int(quant_cfg["hessian_patches_per_image"]),
                include_linear=bool(quant_cfg["quantize_linear"]),
                device=device,
            )
            # The released artifact deliberately excludes membership labels, record IDs, hashes,
            # and calibration-set metadata. Ground truth exists only in this external manifest.
            digest = save_artifact(
                artifact,
                artifact_path,
                bits=int(quant_cfg["bits"]),
                metadata={
                    "method": "GPTQ-style",
                    "artifact_id": artifact_id,
                    "calibration_size": int(attack_cfg["calibration_size"]),
                    "fixed_grid": True,
                    "batchnorm_recalibration": False,
                },
            )
            resumed = False
        record["artifact_path"] = str(artifact_path.resolve())
        record["artifact_sha256"] = digest
        record["seconds"] = time.perf_counter() - started
        record["resumed"] = resumed
        if artifact_id == 0:
            first_artifact = artifact
            repeat_loader = _calibration_loader(
                calibration,
                record["calibration_indices"],
                batch_size=int(attack_cfg["calibration_batch_size"]),
                device=device,
            )
            repeated = gptq_artifact(
                model,
                repeat_loader,
                bits=int(quant_cfg["bits"]),
                damping=float(quant_cfg["damping"]),
                block_size=int(quant_cfg["block_size"]),
                patches_per_image=int(quant_cfg["hessian_patches_per_image"]),
                include_linear=bool(quant_cfg["quantize_linear"]),
                device=device,
            )
            changed = sum(
                int(torch.count_nonzero(first_artifact[name].codes != repeated[name].codes))
                for name in first_artifact
            )
            design["determinism_repeat_changed_codes"] = changed
            if changed:
                raise RuntimeError("Population determinism check failed")
        with manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(design, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(
            json.dumps(
                {
                    "artifact": f"{position}/{len(design['artifacts'])}",
                    "artifact_id": artifact_id,
                    "split": record["split"],
                    "target_members": len(record["member_target_positions"]),
                    "resumed": resumed,
                    "seconds": record["seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    return manifest_path


@torch.inference_mode()
def _capture_batch(
    model: nn.Module,
    images: torch.Tensor,
    include_linear: bool,
) -> tuple[dict[str, tuple[torch.Tensor, torch.Tensor]], torch.Tensor]:
    captured: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}
    handles: list[torch.utils.hooks.RemovableHandle] = []

    def make_hook(name: str):
        def hook(_module: nn.Module, args: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
            energy = output.detach().float().flatten(1).square().sum(1)
            captured[name] = (args[0].detach(), energy)

        return hook

    for name, module in quantizable_modules(model, include_linear).items():
        handles.append(module.register_forward_hook(make_hook(name)))
    try:
        logits = model(images)
    finally:
        for handle in handles:
            handle.remove()
    return captured, logits.detach()


@torch.inference_mode()
def _batch_reconstruction_scores(
    model: nn.Module,
    artifact: Artifact,
    captured: dict[str, tuple[torch.Tensor, torch.Tensor]],
    include_linear: bool,
) -> tuple[torch.Tensor, torch.Tensor]:
    modules = quantizable_modules(model, include_linear)
    batch_size = next(iter(captured.values()))[0].shape[0]
    error_total = torch.zeros(batch_size, dtype=torch.float64, device=next(model.parameters()).device)
    baseline_total = torch.zeros_like(error_total)
    layer_scores: list[torch.Tensor] = []
    for name, module in modules.items():
        inputs, baseline_energy = captured[name]
        difference = artifact[name].dequantize().to(module.weight.device, module.weight.dtype)
        difference = difference - module.weight
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
        else:
            residual = F.linear(inputs, difference, bias=None)
        layer_error = residual.float().flatten(1).square().sum(1).double()
        error_total += layer_error
        baseline_total += baseline_energy.double()
        layer_scores.append(
            -(layer_error / baseline_energy.double().clamp_min(torch.finfo(torch.float64).eps))
        )
    total_score = -(error_total / baseline_total.clamp_min(torch.finfo(torch.float64).eps))
    return total_score, torch.stack(layer_scores, dim=1)


def _target_batch(calibration: CIFAR100Dataset, target_indices: list[int]) -> tuple[torch.Tensor, torch.Tensor]:
    position_by_source = {int(source): position for position, source in enumerate(calibration.indices)}
    examples = [calibration[position_by_source[index]] for index in target_indices]
    images = torch.stack([example[0] for example in examples])
    labels = torch.tensor([example[1] for example in examples], dtype=torch.long)
    return images, labels


def score_attack_population(config: dict[str, Any], config_path: str | Path) -> Path:
    seed_everything(int(config["seed"]))
    device = default_device()
    paths = config["paths"]
    data_cfg = config["data"]
    attack_cfg = config["attack"]
    _, calibration, _, _ = load_datasets(
        resolve_path(config_path, paths["data_dir"]),
        train_per_class=int(data_cfg["train_per_class"]),
        calibration_per_class=int(data_cfg["calibration_per_class"]),
        split_seed=int(data_cfg["split_seed"]),
    )
    manifest_path = resolve_path(config_path, attack_cfg["manifest"])
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = load_base_model(resolve_path(config_path, paths["base_checkpoint"]), device)
    include_linear = bool(config["quantization"]["quantize_linear"])
    images, labels = _target_batch(calibration, manifest["target_indices"])
    images = images.to(device)
    labels = labels.to(device)
    captured, base_logits = _capture_batch(model, images, include_linear)
    base_weights = {
        name: module.weight.detach().clone()
        for name, module in quantizable_modules(model, include_linear).items()
    }
    artifacts = manifest["artifacts"]
    shape = (len(artifacts), len(manifest["target_indices"]))
    layer_names = list(quantizable_modules(model, include_linear))
    reconstruction = np.full(shape, np.nan, dtype=np.float64)
    layer_reconstruction = np.full((*shape, len(layer_names)), np.nan, dtype=np.float64)
    logit_mse = np.full(shape, np.nan, dtype=np.float64)
    output_kl = np.full(shape, np.nan, dtype=np.float64)
    true_logprob = np.full(shape, np.nan, dtype=np.float64)
    base_probabilities = base_logits.softmax(1)

    for position, record in enumerate(artifacts, start=1):
        started = time.perf_counter()
        artifact, _ = load_artifact(record["artifact_path"])
        row = int(record["artifact_id"])
        aggregate_score, layer_scores = _batch_reconstruction_scores(
            model, artifact, captured, include_linear
        )
        reconstruction[row] = aggregate_score.cpu().numpy()
        layer_reconstruction[row] = layer_scores.cpu().numpy()
        apply_artifact(model, artifact)
        with torch.inference_mode():
            quantized_logits = model(images)
        logit_mse[row] = -(
            (quantized_logits - base_logits).float().square().mean(1).cpu().numpy()
        )
        quantized_logprob = quantized_logits.log_softmax(1)
        output_kl[row] = -(
            (
                base_probabilities
                * (base_probabilities.clamp_min(1e-12).log() - quantized_logprob)
            )
            .sum(1)
            .cpu()
            .numpy()
        )
        true_logprob[row] = quantized_logprob.gather(1, labels[:, None]).squeeze(1).cpu().numpy()
        with torch.no_grad():
            modules = dict(model.named_modules())
            for name, weight in base_weights.items():
                modules[name].weight.copy_(weight)
        print(
            json.dumps(
                {
                    "scored_artifact": f"{position}/{len(artifacts)}",
                    "artifact_id": row,
                    "seconds": time.perf_counter() - started,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    scores_path = resolve_path(config_path, attack_cfg["scores"])
    scores_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        scores_path,
        artifact_reconstruction=reconstruction,
        layer_reconstruction=layer_reconstruction,
        layer_names=np.asarray(layer_names, dtype=np.str_),
        output_logit_mse=logit_mse,
        output_kl=output_kl,
        output_true_logprob=true_logprob,
        membership=np.asarray(manifest["membership"], dtype=np.uint8),
        target_indices=np.asarray(manifest["target_indices"], dtype=np.int64),
        target_labels=np.asarray(manifest["target_labels"], dtype=np.int64),
        shadow_artifacts=np.asarray(manifest["shadow_artifacts"], dtype=np.int64),
    )
    return scores_path


def _tpr_at_fpr(labels: np.ndarray, scores: np.ndarray, target_fpr: float) -> float:
    false_positive_rate, true_positive_rate, _ = roc_curve(labels, scores)
    eligible = true_positive_rate[false_positive_rate <= target_fpr]
    return float(eligible.max()) if len(eligible) else 0.0


def _shadow_normalize_all(
    raw_scores: np.ndarray,
    membership: np.ndarray,
    shadow_count: int,
) -> np.ndarray:
    normalized = np.empty_like(raw_scores, dtype=np.float64)
    for target in range(raw_scores.shape[1]):
        shadow_values = raw_scores[:shadow_count, target]
        shadow_labels = membership[:shadow_count, target].astype(bool)
        member_values = shadow_values[shadow_labels]
        nonmember_values = shadow_values[~shadow_labels]
        member_mean = float(member_values.mean())
        nonmember_mean = float(nonmember_values.mean())
        midpoint = (member_mean + nonmember_mean) / 2.0
        pooled_scale = float(
            np.sqrt((member_values.var(ddof=1) + nonmember_values.var(ddof=1)) / 2.0)
        )
        pooled_scale = max(pooled_scale, np.finfo(np.float64).eps)
        learned_direction = 1.0 if member_mean >= nonmember_mean else -1.0
        normalized[:, target] = learned_direction * (raw_scores[:, target] - midpoint) / pooled_scale
    return normalized


def _shadow_normalize(
    raw_scores: np.ndarray,
    membership: np.ndarray,
    shadow_count: int,
) -> np.ndarray:
    return _shadow_normalize_all(raw_scores, membership, shadow_count)[shadow_count:]


def _metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    return {
        "auroc": float(roc_auc_score(labels, scores)),
        "tpr_at_1pct_fpr": _tpr_at_fpr(labels, scores, 0.01),
        "tpr_at_0_1pct_fpr": _tpr_at_fpr(labels, scores, 0.001),
    }


def _shadow_calibrated_operating_point(
    shadow_labels: np.ndarray,
    shadow_scores: np.ndarray,
    test_labels: np.ndarray,
    test_scores: np.ndarray,
    target_fpr: float,
) -> dict[str, float | int]:
    shadow_nonmembers = shadow_scores[~shadow_labels.astype(bool)]
    allowed_false_positives = int(np.floor(target_fpr * len(shadow_nonmembers)))
    descending = np.sort(shadow_nonmembers)[::-1]
    threshold = float(descending[allowed_false_positives])
    shadow_predictions = shadow_scores > threshold
    test_predictions = test_scores > threshold
    shadow_nonmember_mask = ~shadow_labels.astype(bool)
    test_member_mask = test_labels.astype(bool)
    test_nonmember_mask = ~test_member_mask
    return {
        "target_fpr": target_fpr,
        "threshold": threshold,
        "allowed_shadow_false_positives": allowed_false_positives,
        "shadow_false_positives": int(
            np.count_nonzero(shadow_predictions & shadow_nonmember_mask)
        ),
        "shadow_fpr": float(shadow_predictions[shadow_nonmember_mask].mean()),
        "test_false_positives": int(np.count_nonzero(test_predictions & test_nonmember_mask)),
        "test_fpr": float(test_predictions[test_nonmember_mask].mean()),
        "test_true_positives": int(np.count_nonzero(test_predictions & test_member_mask)),
        "test_tpr": float(test_predictions[test_member_mask].mean()),
    }


def _per_target_auroc_summary(labels: np.ndarray, scores: np.ndarray) -> dict[str, float | int]:
    values = np.asarray(
        [roc_auc_score(labels[:, target], scores[:, target]) for target in range(labels.shape[1])]
    )
    return {
        "minimum": float(values.min()),
        "lower_quartile": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "upper_quartile": float(np.quantile(values, 0.75)),
        "maximum": float(values.max()),
        "targets_above_chance": int(np.count_nonzero(values > 0.5)),
        "targets_at_least_0_9": int(np.count_nonzero(values >= 0.9)),
    }


def _distribution_summary(values: np.ndarray) -> dict[str, Any]:
    """Return an auditable five-number summary together with every unit-level value."""
    vector = np.asarray(values, dtype=np.float64)
    return {
        "minimum": float(vector.min()),
        "lower_quartile": float(np.quantile(vector, 0.25)),
        "median": float(np.median(vector)),
        "upper_quartile": float(np.quantile(vector, 0.75)),
        "maximum": float(vector.max()),
        "values": vector.tolist(),
    }


def _per_artifact_auroc_summary(
    labels: np.ndarray, scores: np.ndarray
) -> dict[str, Any]:
    """Summarize discrimination separately for each held-out deployment artifact."""
    values = np.asarray(
        [roc_auc_score(labels[row], scores[row]) for row in range(labels.shape[0])],
        dtype=np.float64,
    )
    result = _distribution_summary(values)
    result.update(
        {
            "artifacts": int(values.size),
            "artifacts_above_chance": int(np.count_nonzero(values > 0.5)),
            "artifacts_at_least_0_9": int(np.count_nonzero(values >= 0.9)),
        }
    )
    return result


def _per_artifact_operating_summary(
    labels: np.ndarray, scores: np.ndarray, threshold: float
) -> dict[str, Any]:
    """Report artifact-level TPR and FPR at one threshold fixed on shadow artifacts."""
    predictions = scores > threshold
    tpr = np.asarray(
        [predictions[row, labels[row]].mean() for row in range(labels.shape[0])],
        dtype=np.float64,
    )
    fpr = np.asarray(
        [predictions[row, ~labels[row]].mean() for row in range(labels.shape[0])],
        dtype=np.float64,
    )
    return {
        "threshold": float(threshold),
        "tpr": _distribution_summary(tpr),
        "fpr": _distribution_summary(fpr),
    }


def _bootstrap_metrics(
    labels: np.ndarray,
    feature_scores: dict[str, np.ndarray],
    *,
    replicates: int,
    seed: int,
    baseline_key: str = "output_logit_mse",
    artifact_key: str = "artifact_reconstruction",
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    artifact_count, target_count = labels.shape
    samples: dict[str, list[dict[str, float]]] = {name: [] for name in feature_scores}
    differences: list[float] = []
    for _ in range(replicates):
        artifact_indices = rng.integers(0, artifact_count, artifact_count)
        target_indices = rng.integers(0, target_count, target_count)
        selected_labels = labels[np.ix_(artifact_indices, target_indices)].reshape(-1)
        if selected_labels.min() == selected_labels.max():
            continue
        replicate_values: dict[str, dict[str, float]] = {}
        for name, scores in feature_scores.items():
            selected_scores = scores[np.ix_(artifact_indices, target_indices)].reshape(-1)
            replicate_values[name] = _metrics(selected_labels, selected_scores)
            samples[name].append(replicate_values[name])
        differences.append(
            replicate_values[artifact_key]["auroc"] - replicate_values[baseline_key]["auroc"]
        )

    summary: dict[str, Any] = {}
    for name, values in samples.items():
        summary[name] = {}
        for metric in ("auroc", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"):
            vector = np.asarray([value[metric] for value in values])
            summary[name][metric] = {
                "lower_95": float(np.quantile(vector, 0.025)),
                "upper_95": float(np.quantile(vector, 0.975)),
            }
    difference_vector = np.asarray(differences)
    summary[f"artifact_minus_{baseline_key}_auroc"] = {
        "lower_95": float(np.quantile(difference_vector, 0.025)),
        "upper_95": float(np.quantile(difference_vector, 0.975)),
    }
    return summary


def evaluate_attack_population(config: dict[str, Any], config_path: str | Path) -> Path:
    attack_cfg = config["attack"]
    scores_path = resolve_path(config_path, attack_cfg["scores"])
    with np.load(scores_path, allow_pickle=False) as payload:
        membership = payload["membership"].astype(bool)
        shadow_count = int(payload["shadow_artifacts"])
        raw_features = {
            name: payload[name].copy()
            for name in (
                "artifact_reconstruction",
                "output_logit_mse",
                "output_kl",
                "output_true_logprob",
            )
        }
        layer_reconstruction = (
            payload["layer_reconstruction"].copy()
            if "layer_reconstruction" in payload.files
            else None
        )
        layer_names = (
            payload["layer_names"].astype(str).tolist()
            if "layer_names" in payload.files
            else None
        )
    normalized_all = {
        name: _shadow_normalize_all(values, membership, shadow_count)
        for name, values in raw_features.items()
    }
    normalized = {name: values[shadow_count:] for name, values in normalized_all.items()}
    shadow_labels_matrix = membership[:shadow_count]
    test_labels_matrix = membership[shadow_count:]
    shadow_labels = shadow_labels_matrix.reshape(-1).astype(np.uint8)
    flattened_labels = test_labels_matrix.reshape(-1).astype(np.uint8)
    point_metrics = {
        name: _metrics(flattened_labels, values.reshape(-1))
        for name, values in normalized.items()
    }
    operating_points = {
        name: {
            "1pct_target_fpr": _shadow_calibrated_operating_point(
                shadow_labels,
                normalized_all[name][:shadow_count].reshape(-1),
                flattened_labels,
                values.reshape(-1),
                0.01,
            ),
            "0_1pct_target_fpr": _shadow_calibrated_operating_point(
                shadow_labels,
                normalized_all[name][:shadow_count].reshape(-1),
                flattened_labels,
                values.reshape(-1),
                0.001,
            ),
        }
        for name, values in normalized.items()
    }
    per_target = {
        name: _per_target_auroc_summary(test_labels_matrix, values)
        for name, values in normalized.items()
    }
    per_artifact = {
        name: _per_artifact_auroc_summary(test_labels_matrix, values)
        for name, values in normalized.items()
    }
    fit_free_scores = raw_features["artifact_reconstruction"][shadow_count:]
    fit_free_metrics = _metrics(flattened_labels, fit_free_scores.reshape(-1))
    layerwise: list[dict[str, Any]] | None = None
    if layer_reconstruction is not None and layer_names is not None:
        layerwise = []
        for layer_index, layer_name in enumerate(layer_names):
            layer_normalized_all = _shadow_normalize_all(
                layer_reconstruction[:, :, layer_index], membership, shadow_count
            )
            layer_test_scores = layer_normalized_all[shadow_count:]
            layer_metrics = _metrics(flattened_labels, layer_test_scores.reshape(-1))
            layer_operating_point = _shadow_calibrated_operating_point(
                shadow_labels,
                layer_normalized_all[:shadow_count].reshape(-1),
                flattened_labels,
                layer_test_scores.reshape(-1),
                0.01,
            )
            layerwise.append(
                {
                    "layer": layer_name,
                    **layer_metrics,
                    "shadow_calibrated_1pct": layer_operating_point,
                }
            )
        layerwise.sort(key=lambda values: values["auroc"], reverse=True)
    bootstrap = _bootstrap_metrics(
        test_labels_matrix,
        normalized,
        replicates=int(attack_cfg["bootstrap_replicates"]),
        seed=int(attack_cfg["bootstrap_seed"]),
    )
    result = {
        "threat_model": "public base, known quantizer, one held-out released artifact",
        "shadow_artifacts": shadow_count,
        "test_artifacts": int(membership.shape[0] - shadow_count),
        "targets": int(membership.shape[1]),
        "test_decisions": int(flattened_labels.size),
        "test_members": int(flattened_labels.sum()),
        "test_nonmembers": int((1 - flattened_labels).sum()),
        "empirical_test_fpr_resolution": float(1 / (1 - flattened_labels).sum()),
        "metrics": point_metrics,
        "shadow_calibrated_operating_points": operating_points,
        "per_target_auroc": per_target,
        "per_artifact_auroc": per_artifact,
        "fit_free_fixed_score": {
            "protocol": (
                "predefined negative residual-energy score with zero learned direction, "
                "normalization, layer weighting, regularization, or feature selection"
            ),
            "metrics": fit_free_metrics,
            "per_artifact_auroc": _per_artifact_auroc_summary(
                test_labels_matrix, fit_free_scores
            ),
        },
        "layerwise_artifact_reconstruction": layerwise,
        "cluster_bootstrap": bootstrap,
    }
    result["artifact_minus_output_logit_mse_auroc"] = (
        point_metrics["artifact_reconstruction"]["auroc"]
        - point_metrics["output_logit_mse"]["auroc"]
    )
    report_path = resolve_path(config_path, attack_cfg["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("# CalibTrace single-artifact attack report\n\n")
        handle.write(
            f"Evaluation uses {result['shadow_artifacts']} shadow artifacts, "
            f"{result['test_artifacts']} completely held-out artifacts, and "
            f"{result['targets']} candidate records at W4/"
            f"N={int(attack_cfg['calibration_size'])}.\n\n"
        )
        handle.write("| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |\n")
        handle.write("|---|---:|---:|---:|\n")
        for name, values in point_metrics.items():
            handle.write(
                f"| {name} | {values['auroc']:.4f} | "
                f"{values['tpr_at_1pct_fpr']:.4f} | "
                f"{values['tpr_at_0_1pct_fpr']:.4f} |\n"
            )
        handle.write("\n")
        if layerwise:
            handle.write("## Layerwise localization\n\n")
            handle.write(
                "Each layer is scored alone with the same shadow-only candidate normalization. "
                "These are localization diagnostics, not separately bootstrapped claims.\n\n"
            )
            handle.write("| Layer | AUROC | ROC TPR @ FPR<=1% | Frozen-threshold test TPR |\n")
            handle.write("|---|---:|---:|---:|\n")
            for values in layerwise:
                handle.write(
                    f"| {values['layer']} | {values['auroc']:.4f} | "
                    f"{values['tpr_at_1pct_fpr']:.4f} | "
                    f"{values['shadow_calibrated_1pct']['test_tpr']:.4f} |\n"
                )
            handle.write("\n")
        handle.write(
            "The held-out set has 768 nonmembers, so its empirical FPR resolution is "
            f"{100 * result['empirical_test_fpr_resolution']:.3f}%. The final column is the "
            "zero-observed-false-positive point; it must not be read as a resolved 0.1% estimate.\n\n"
        )
        handle.write("## Shadow-calibrated operating points\n\n")
        handle.write(
            "Thresholds below are selected using shadow nonmembers only and then frozen before "
            "evaluation on held-out artifacts.\n\n"
        )
        handle.write("| Feature | Target FPR | Shadow FPR | Test FPR | Test TPR |\n")
        handle.write("|---|---:|---:|---:|---:|\n")
        for name, feature_points in operating_points.items():
            for label, values in feature_points.items():
                target_label = "1%" if label == "1pct_target_fpr" else "0.1%"
                handle.write(
                    f"| {name} | {target_label} | {values['shadow_fpr']:.4f} | "
                    f"{values['test_fpr']:.4f} | {values['test_tpr']:.4f} |\n"
                )
        handle.write("\n")
        handle.write(
            "Artifact minus output-logit-MSE AUROC: "
            f"{result['artifact_minus_output_logit_mse_auroc']:.4f}.\n\n"
        )
        handle.write("Full crossed target/artifact bootstrap intervals and metadata:\n\n")
        handle.write("```json\n")
        handle.write(json.dumps(result, indent=2, sort_keys=True))
        handle.write("\n```\n")
    json_path = report_path.with_suffix(".json")
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return report_path
