from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from .artifact_io import load_artifact
from .quantization import Artifact


def compare_artifacts(member: Artifact, nonmember: Artifact) -> dict[str, Any]:
    if member.keys() != nonmember.keys():
        raise ValueError("Artifacts contain different layers")
    layers: dict[str, dict[str, float | int]] = {}
    changed_total = 0
    code_total = 0
    squared_delta_total = 0.0
    for name in member:
        left = member[name].codes.numpy().astype(np.int16, copy=False)
        right = nonmember[name].codes.numpy().astype(np.int16, copy=False)
        delta = left - right
        changed = int(np.count_nonzero(delta))
        count = int(delta.size)
        squared_delta = float(np.square(delta.astype(np.float64)).sum())
        layers[name] = {
            "changed_codes": changed,
            "total_codes": count,
            "flip_fraction": changed / count,
            "squared_code_delta": squared_delta,
        }
        changed_total += changed
        code_total += count
        squared_delta_total += squared_delta
    return {
        "changed_codes": changed_total,
        "total_codes": code_total,
        "flip_fraction": changed_total / code_total,
        "code_delta_l2": squared_delta_total**0.5,
        "layers": layers,
    }


def artifact_delta(member: Artifact, nonmember: Artifact) -> dict[str, np.ndarray]:
    return {
        name: member[name].codes.numpy().astype(np.int16)
        - nonmember[name].codes.numpy().astype(np.int16)
        for name in member
    }


def _delta_similarity(left: dict[str, np.ndarray], right: dict[str, np.ndarray]) -> dict[str, float]:
    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    intersection = 0
    union = 0
    for name in left:
        first = left[name].reshape(-1).astype(np.float64, copy=False)
        second = right[name].reshape(-1).astype(np.float64, copy=False)
        dot += float(first @ second)
        left_norm += float(first @ first)
        right_norm += float(second @ second)
        first_mask = first != 0
        second_mask = second != 0
        intersection += int(np.count_nonzero(first_mask & second_mask))
        union += int(np.count_nonzero(first_mask | second_mask))
    cosine = dot / max((left_norm * right_norm) ** 0.5, np.finfo(float).eps)
    jaccard = intersection / union if union else 1.0
    return {"signed_delta_cosine": cosine, "flip_mask_jaccard": jaccard}


def summarize_reproducibility(records: list[dict[str, Any]]) -> dict[str, Any]:
    cache: list[tuple[dict[str, Any], dict[str, np.ndarray]]] = []
    for record in records:
        member, _ = load_artifact(Path(record["member_artifact"]))
        nonmember, _ = load_artifact(Path(record["nonmember_artifact"]))
        cache.append((record, artifact_delta(member, nonmember)))

    within: list[dict[str, float]] = []
    between: list[dict[str, float]] = []
    grouped: dict[int, list[int]] = defaultdict(list)
    for position, (record, _) in enumerate(cache):
        grouped[int(record["target_index"])].append(position)
    for positions in grouped.values():
        for left, right in combinations(positions, 2):
            within.append(_delta_similarity(cache[left][1], cache[right][1]))
    for left, right in combinations(range(len(cache)), 2):
        if cache[left][0]["target_index"] != cache[right][0]["target_index"]:
            between.append(_delta_similarity(cache[left][1], cache[right][1]))

    def aggregate(values: list[dict[str, float]]) -> dict[str, float | int]:
        if not values:
            return {"comparisons": 0, "mean_signed_delta_cosine": float("nan"), "mean_flip_mask_jaccard": float("nan")}
        return {
            "comparisons": len(values),
            "mean_signed_delta_cosine": float(
                np.mean([value["signed_delta_cosine"] for value in values])
            ),
            "mean_flip_mask_jaccard": float(
                np.mean([value["flip_mask_jaccard"] for value in values])
            ),
        }

    return {"within_target": aggregate(within), "between_target": aggregate(between)}

