"""Evaluate candidate-cross-fitted attacks across the matched GPTQ and AutoRound populations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from calibtrace.attack import _bootstrap_metrics, _metrics  # noqa: E402
from calibtrace.autoround_attack import (  # noqa: E402
    OUTPUT_FEATURES,
    SCORE_FEATURES,
    _apply_global_scalar,
    _apply_global_vector,
    _fit_global_scalar,
    _fit_global_vector,
    _fixed_degree_randomization_test,
    _load_scores,
    _reference_correct,
)
from calibtrace.config import load_config, resolve_path  # noqa: E402


def _load_arm(config_path: Path, section: str) -> dict[str, Any]:
    config = load_config(config_path)
    cfg = config[section]
    manifest_path = resolve_path(config_path, cfg["manifest"])
    with manifest_path.open("r", encoding="utf-8") as handle:
        design = json.load(handle)
    payload = _load_scores(resolve_path(config_path, cfg["scores"]), design)
    corrected = {
        name: _reference_correct(payload[name], payload[f"{name}__reference"])
        for name in SCORE_FEATURES
    }
    layers = payload["layer_reconstruction"]
    reference_layers = payload["layer_reconstruction__reference"]
    if reference_layers.shape[1]:
        layers = layers - reference_layers.mean(1, keepdims=True)
    return {
        "cfg": cfg,
        "design": design,
        "method": str(design.get("method", "AutoRound" if section == "autoround_attack" else "GPTQ")),
        "membership": np.asarray(design["membership"], dtype=bool),
        "corrected": corrected,
        "layers": layers,
        "layer_names": payload["layer_names"],
    }


def _validate_match(first: dict[str, Any], second: dict[str, Any]) -> None:
    fields = (
        "record_pool_sha256",
        "population_sha256",
        "targets",
        "shadow_artifacts",
        "test_artifacts",
        "calibration_size",
        "sequence_length",
    )
    mismatched = [
        field
        for field in fields
        if first["design"].get(field) != second["design"].get(field)
    ]
    if mismatched:
        raise ValueError(f"Quantizer populations are not matched: {mismatched}")
    if not np.array_equal(first["membership"], second["membership"]):
        raise ValueError("Quantizer populations use different membership matrices")
    if first["layer_names"] != second["layer_names"]:
        raise ValueError("Quantizer populations expose different quantized layer sets")


def _transfer(
    source: dict[str, Any],
    target: dict[str, Any],
    *,
    folds: int,
    seed: int,
    bootstrap_replicates: int,
    bootstrap_seed: int,
    randomization_replicates: int,
    randomization_seed: int,
) -> dict[str, Any]:
    membership = source["membership"]
    shadow_count = int(source["design"]["shadow_artifacts"])
    target_labels = target["membership"][shadow_count:]
    target_count = membership.shape[1]
    grid = tuple(
        float(value)
        for value in source["cfg"].get("logistic_regularization", (1.0, 0.1, 0.01, 0.001))
    )
    rng = np.random.default_rng(seed)
    candidate_folds = np.array_split(rng.permutation(target_count), folds)
    scalar_names = ("artifact_reconstruction", *OUTPUT_FEATURES)
    predictions = {
        name: np.full(target_labels.shape, np.nan, dtype=np.float64) for name in scalar_names
    }
    predictions["artifact_layer_combination"] = np.full(
        target_labels.shape, np.nan, dtype=np.float64
    )
    predictions["output_combination"] = np.full(target_labels.shape, np.nan, dtype=np.float64)
    selected_artifact = np.full(target_labels.shape, np.nan, dtype=np.float64)
    selected_output = np.full(target_labels.shape, np.nan, dtype=np.float64)
    source_output = np.stack(
        [source["corrected"][name] for name in OUTPUT_FEATURES], axis=-1
    )
    target_output = np.stack(
        [target["corrected"][name] for name in OUTPUT_FEATURES], axis=-1
    )
    selections: list[dict[str, Any]] = []

    for fold_index, held_out in enumerate(candidate_folds):
        training = np.setdiff1d(np.arange(target_count), held_out, assume_unique=True)
        training_labels = membership[:shadow_count, training]
        source_scores: dict[str, float] = {}
        for name in scalar_names:
            calibration = _fit_global_scalar(
                source["corrected"][name][:shadow_count, training], training_labels
            )
            predictions[name][:, held_out] = _apply_global_scalar(
                target["corrected"][name][shadow_count:, held_out], calibration
            )
            fitted_source = _apply_global_scalar(
                source["corrected"][name][:shadow_count, training], calibration
            )
            source_scores[name] = _metrics(
                training_labels.reshape(-1), fitted_source.reshape(-1)
            )["auroc"]

        layer_model, layer_mean, layer_scale, layer_strength, layer_cv = _fit_global_vector(
            source["layers"][:shadow_count, training], training_labels, grid
        )
        predictions["artifact_layer_combination"][:, held_out] = _apply_global_vector(
            layer_model,
            layer_mean,
            layer_scale,
            target["layers"][shadow_count:, held_out],
        )
        output_model, output_mean, output_scale, output_strength, output_cv = _fit_global_vector(
            source_output[:shadow_count, training], training_labels, grid
        )
        predictions["output_combination"][:, held_out] = _apply_global_vector(
            output_model,
            output_mean,
            output_scale,
            target_output[shadow_count:, held_out],
        )
        source_scores["artifact_layer_combination"] = layer_cv
        source_scores["output_combination"] = output_cv
        artifact_key = max(
            ("artifact_reconstruction", "artifact_layer_combination"),
            key=lambda name: source_scores[name],
        )
        output_key = max(
            (*OUTPUT_FEATURES, "output_combination"),
            key=lambda name: source_scores[name],
        )
        selected_artifact[:, held_out] = predictions[artifact_key][:, held_out]
        selected_output[:, held_out] = predictions[output_key][:, held_out]
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
            }
        )

    predictions["selected_artifact"] = selected_artifact
    predictions["selected_output"] = selected_output
    if any(np.isnan(values).any() for values in predictions.values()):
        raise RuntimeError("Transfer evaluation left unevaluated scores")
    flattened_labels = target_labels.reshape(-1).astype(np.uint8)
    metrics = {
        name: _metrics(flattened_labels, values.reshape(-1))
        for name, values in predictions.items()
    }
    bootstrap = _bootstrap_metrics(
        target_labels,
        predictions,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
        artifact_key="selected_artifact",
        baseline_key="selected_output",
    )
    randomization = _fixed_degree_randomization_test(
        target_labels,
        selected_artifact,
        replicates=randomization_replicates,
        seed=randomization_seed,
    )
    return {
        "source_method": source["method"],
        "target_method": target["method"],
        "protocol": (
            "zero-shot quantizer-family transfer: every direction, normalization, feature "
            "combination, and feature choice is fit on source-family shadow artifacts; evaluated "
            "candidates are excluded by candidate-fold cross-fitting"
        ),
        "folds": folds,
        "seed": seed,
        "test_decisions": int(target_labels.size),
        "metrics": metrics,
        "cluster_bootstrap": bootstrap,
        "fixed_degree_randomization_test": randomization,
        "selections": selections,
    }


def _write_markdown(path: Path, result: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Cross-quantizer transfer\n\n")
        handle.write(
            "Every attack component is fit on shadow artifacts from the source PTQ family and "
            "applied without retuning to held-out artifacts from the target family. The two arms "
            "use the exact same records and membership matrix.\n\n"
        )
        handle.write("| Source | Target | Artifact AUROC | Output AUROC | Decisions |\n")
        handle.write("|---|---|---:|---:|---:|\n")
        for transfer in result["transfers"]:
            artifact = transfer["metrics"]["selected_artifact"]["auroc"]
            output = transfer["metrics"]["selected_output"]["auroc"]
            handle.write(
                f"| {transfer['source_method']} | {transfer['target_method']} | "
                f"{artifact:.4f} | {output:.4f} | {transfer['test_decisions']} |\n"
            )
        handle.write("\nFull metrics and metadata:\n\n```json\n")
        handle.write(json.dumps(result, indent=2, sort_keys=True))
        handle.write("\n```\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--first-config",
        "--gptq-config",
        dest="first_config",
        type=Path,
        default=Path("configs/matched_gptq.yaml"),
    )
    parser.add_argument("--first-section", default="gptq_attack")
    parser.add_argument(
        "--second-config",
        "--autoround-config",
        dest="second_config",
        type=Path,
        default=Path("configs/matched_autoround.yaml"),
    )
    parser.add_argument("--second-section", default="autoround_attack")
    parser.add_argument(
        "--output", type=Path, default=Path("reports/cross_quantizer_transfer.json")
    )
    parser.add_argument("--folds", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261021)
    args = parser.parse_args()

    first = _load_arm(args.first_config, args.first_section)
    second = _load_arm(args.second_config, args.second_section)
    _validate_match(first, second)
    result = {
        "population_sha256": first["design"]["population_sha256"],
        "record_pool_sha256": first["design"]["record_pool_sha256"],
        "exact_population_match": True,
        "transfers": [
            _transfer(
                first,
                second,
                folds=args.folds,
                seed=args.seed,
                bootstrap_replicates=1000,
                bootstrap_seed=args.seed + 1,
                randomization_replicates=10000,
                randomization_seed=args.seed + 2,
            ),
            _transfer(
                second,
                first,
                folds=args.folds,
                seed=args.seed,
                bootstrap_replicates=1000,
                bootstrap_seed=args.seed + 3,
                randomization_replicates=10000,
                randomization_seed=args.seed + 4,
            ),
        ],
    }
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    _write_markdown(output.with_suffix(".md"), result)
    print(json.dumps({"report": str(output), "transfers": len(result["transfers"])}))


if __name__ == "__main__":
    main()
