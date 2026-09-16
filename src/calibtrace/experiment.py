from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from .analysis import compare_artifacts, summarize_reproducibility
from .artifact_io import save_artifact
from .config import resolve_path
from .data import CIFAR100Dataset, load_datasets, subset_by_source_indices, write_manifest
from .quantization import apply_artifact, gptq_artifact, rtn_artifact
from .repro import default_device, seed_everything
from .train import evaluate, load_base_model


@dataclass(frozen=True)
class PairDesign:
    calibration_size: int
    target_index: int
    replacement_index: int
    target_number: int
    background_number: int
    background_indices: tuple[int, ...]

    @property
    def member_indices(self) -> list[int]:
        return [*self.background_indices, self.target_index]

    @property
    def nonmember_indices(self) -> list[int]:
        return [*self.background_indices, self.replacement_index]

    @property
    def pair_id(self) -> str:
        return f"target{self.target_number:03d}_background{self.background_number:03d}"


def _index_hash(indices: list[int]) -> str:
    canonical = ",".join(str(index) for index in indices).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def make_pair_designs(
    calibration: CIFAR100Dataset,
    *,
    calibration_size: int,
    targets: int,
    backgrounds_per_target: int,
    seed: int,
) -> list[PairDesign]:
    if calibration_size < 2 or calibration_size > len(calibration):
        raise ValueError("Invalid calibration size")
    pool = np.asarray(calibration.indices, dtype=np.int64)
    labels = calibration.labels
    rng = np.random.default_rng(seed + calibration_size * 1_000_003)
    candidate_order = rng.permutation(pool)
    target_indices = [int(index) for index in candidate_order[:targets]]
    designs: list[PairDesign] = []
    for target_number, target_index in enumerate(target_indices):
        same_class = pool[(labels[pool] == labels[target_index]) & (pool != target_index)]
        replacement_order = rng.permutation(same_class)
        if len(replacement_order) < backgrounds_per_target:
            raise ValueError("Not enough class-matched replacement records")
        for background_number in range(backgrounds_per_target):
            replacement_index = int(replacement_order[background_number])
            available = pool[(pool != target_index) & (pool != replacement_index)]
            background = rng.choice(available, size=calibration_size - 1, replace=False)
            designs.append(
                PairDesign(
                    calibration_size=calibration_size,
                    target_index=target_index,
                    replacement_index=replacement_index,
                    target_number=target_number,
                    background_number=background_number,
                    background_indices=tuple(sorted(int(index) for index in background)),
                )
            )
    return designs


def _loader(
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


def _evaluate_artifact(
    checkpoint_path: Path,
    artifact: Any,
    evaluation_loader: DataLoader,
    device: torch.device,
) -> dict[str, float]:
    quantized_model = load_base_model(checkpoint_path, device)
    apply_artifact(quantized_model, artifact)
    metrics = evaluate(quantized_model, evaluation_loader, device)
    del quantized_model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return metrics


def run_pilot(config: dict[str, Any], config_path: str | Path) -> Path:
    seed = int(config["seed"])
    seed_everything(seed)
    device = default_device()
    paths = config["paths"]
    data_cfg = config["data"]
    quant_cfg = config["quantization"]

    _, calibration, evaluation, manifest = load_datasets(
        resolve_path(config_path, paths["data_dir"]),
        train_per_class=int(data_cfg["train_per_class"]),
        calibration_per_class=int(data_cfg["calibration_per_class"]),
        split_seed=int(data_cfg["split_seed"]),
    )
    write_manifest(manifest, resolve_path(config_path, paths["split_manifest"]))
    checkpoint_path = resolve_path(config_path, paths["base_checkpoint"])
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Base checkpoint not found at {checkpoint_path}. Run the train command first."
        )
    model = load_base_model(checkpoint_path, device)
    bits = int(quant_cfg["bits"])
    include_linear = bool(quant_cfg["quantize_linear"])
    artifact_root = resolve_path(config_path, paths["artifact_dir"]) / "pilot"
    result_root = resolve_path(config_path, paths["result_dir"])
    result_root.mkdir(parents=True, exist_ok=True)
    evaluation_loader = DataLoader(
        evaluation,
        batch_size=int(config["train"]["eval_batch_size"]),
        shuffle=False,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )
    base_utility = evaluate(model, evaluation_loader, device)

    rtn = rtn_artifact(model, bits, include_linear)
    rtn_path = artifact_root / "rtn_w4.npz"
    rtn_hash = save_artifact(
        rtn,
        rtn_path,
        bits=bits,
        metadata={
            "method": "RTN",
            "calibration_dependent": False,
            "base_checkpoint": str(checkpoint_path.resolve()),
        },
    )
    rtn_utility = _evaluate_artifact(checkpoint_path, rtn, evaluation_loader, device)

    run_summary: dict[str, Any] = {
        "seed": seed,
        "device": str(device),
        "base_checkpoint": str(checkpoint_path.resolve()),
        "split_manifest_sha256": manifest.to_json()["sha256"],
        "rtn_artifact": str(rtn_path.resolve()),
        "rtn_sha256": rtn_hash,
        "base_utility": base_utility,
        "rtn_utility": rtn_utility,
        "conditions": {},
    }
    for calibration_size in [int(value) for value in quant_cfg["calibration_sizes"]]:
        condition_started = time.perf_counter()
        designs = make_pair_designs(
            calibration,
            calibration_size=calibration_size,
            targets=int(quant_cfg["targets"]),
            backgrounds_per_target=int(quant_cfg["backgrounds_per_target"]),
            seed=seed,
        )
        records: list[dict[str, Any]] = []
        determinism: dict[str, Any] | None = None
        first_pair_utility: dict[str, Any] | None = None
        for position, design in enumerate(designs, start=1):
            pair_started = time.perf_counter()
            condition_dir = artifact_root / f"n{calibration_size}" / design.pair_id
            member_loader = _loader(
                calibration,
                design.member_indices,
                batch_size=int(quant_cfg["calibration_batch_size"]),
                device=device,
            )
            nonmember_loader = _loader(
                calibration,
                design.nonmember_indices,
                batch_size=int(quant_cfg["calibration_batch_size"]),
                device=device,
            )
            member = gptq_artifact(
                model,
                member_loader,
                bits=bits,
                damping=float(quant_cfg["damping"]),
                block_size=int(quant_cfg["block_size"]),
                patches_per_image=int(quant_cfg["hessian_patches_per_image"]),
                include_linear=include_linear,
                device=device,
            )
            nonmember = gptq_artifact(
                model,
                nonmember_loader,
                bits=bits,
                damping=float(quant_cfg["damping"]),
                block_size=int(quant_cfg["block_size"]),
                patches_per_image=int(quant_cfg["hessian_patches_per_image"]),
                include_linear=include_linear,
                device=device,
            )
            if position == 1 and bool(quant_cfg.get("determinism_check", True)):
                repeated_member = gptq_artifact(
                    model,
                    member_loader,
                    bits=bits,
                    damping=float(quant_cfg["damping"]),
                    block_size=int(quant_cfg["block_size"]),
                    patches_per_image=int(quant_cfg["hessian_patches_per_image"]),
                    include_linear=include_linear,
                    device=device,
                )
                determinism = compare_artifacts(member, repeated_member)
                if determinism["changed_codes"] != 0:
                    raise RuntimeError(
                        "Identical calibration data produced non-identical quantized codes; "
                        "the causal pilot is invalid on this backend"
                    )
            if position == 1 and bool(quant_cfg.get("evaluate_first_pair", True)):
                first_pair_utility = {
                    "member": _evaluate_artifact(
                        checkpoint_path, member, evaluation_loader, device
                    ),
                    "nonmember": _evaluate_artifact(
                        checkpoint_path, nonmember, evaluation_loader, device
                    ),
                }
            common_metadata = {
                "method": "GPTQ-style",
                "base_checkpoint": str(checkpoint_path.resolve()),
                "calibration_size": calibration_size,
                "pair_id": design.pair_id,
                "target_index": design.target_index,
                "replacement_index": design.replacement_index,
                "background_sha256": _index_hash(list(design.background_indices)),
                "fixed_grid": True,
                "batchnorm_recalibration": False,
            }
            member_path = condition_dir / "member.npz"
            nonmember_path = condition_dir / "nonmember.npz"
            member_hash = save_artifact(
                member,
                member_path,
                bits=bits,
                metadata={
                    **common_metadata,
                    "membership": "in",
                    "calibration_indices_sha256": _index_hash(design.member_indices),
                },
            )
            nonmember_hash = save_artifact(
                nonmember,
                nonmember_path,
                bits=bits,
                metadata={
                    **common_metadata,
                    "membership": "out",
                    "calibration_indices_sha256": _index_hash(design.nonmember_indices),
                },
            )
            comparison = compare_artifacts(member, nonmember)
            record = {
                "pair_id": design.pair_id,
                "target_index": design.target_index,
                "replacement_index": design.replacement_index,
                "target_label": int(calibration.labels[design.target_index]),
                "background_sha256": common_metadata["background_sha256"],
                "member_artifact": str(member_path.resolve()),
                "nonmember_artifact": str(nonmember_path.resolve()),
                "member_sha256": member_hash,
                "nonmember_sha256": nonmember_hash,
                "seconds": time.perf_counter() - pair_started,
                **comparison,
            }
            records.append(record)
            print(
                json.dumps(
                    {
                        "condition": calibration_size,
                        "pair": f"{position}/{len(designs)}",
                        "pair_id": design.pair_id,
                        "flip_fraction": comparison["flip_fraction"],
                        "seconds": record["seconds"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        reproducibility = summarize_reproducibility(records)
        run_summary["conditions"][str(calibration_size)] = {
            "seconds": time.perf_counter() - condition_started,
            "pairs": records,
            "mean_flip_fraction": float(np.mean([record["flip_fraction"] for record in records])),
            "median_flip_fraction": float(
                np.median([record["flip_fraction"] for record in records])
            ),
            "determinism": determinism,
            "first_pair_utility": first_pair_utility,
            "reproducibility": reproducibility,
        }
        partial_path = result_root / "pilot_results.partial.json"
        with partial_path.open("w", encoding="utf-8") as handle:
            json.dump(run_summary, handle, indent=2, sort_keys=True)
            handle.write("\n")

    output_path = result_root / "pilot_results.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(run_summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path
