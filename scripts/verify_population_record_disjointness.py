"""Verify exact record disjointness across the independent OPT populations."""

from __future__ import annotations

import hashlib
import json
import os
from itertools import combinations
from pathlib import Path
from typing import Any

import yaml
from transformers import AutoTokenizer

from calibtrace.autoround_attack import load_record_pool


CONFIGS = (
    ("original", Path("configs/gptq_natural_postcutoff.yaml")),
    ("fresh 1", Path("configs/gptq_natural_fresh1.yaml")),
    ("fresh 2", Path("configs/gptq_natural_fresh2.yaml")),
)


def _config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)["gptq_attack"]


def _row_hashes(records) -> list[str]:
    return [hashlib.sha256(row.numpy().tobytes()).hexdigest() for row in records]


def main() -> None:
    if not os.environ.get("HF_HOME"):
        raise RuntimeError("Set HF_HOME to the project-local Hugging Face cache")
    first_cfg = _config(CONFIGS[0][1])
    tokenizer = AutoTokenizer.from_pretrained(
        first_cfg["model"],
        revision=first_cfg["model_revision"],
        local_files_only=True,
    )
    populations: dict[str, dict[str, Any]] = {}
    for label, path in CONFIGS:
        cfg = _config(path)
        if cfg["model"] != first_cfg["model"]:
            raise RuntimeError("Record-disjointness verification requires one tokenizer")
        records, metadata = load_record_pool(
            tokenizer,
            cfg=cfg,
            config_path=path,
            count=int(cfg["pool_size"]),
            seqlen=int(cfg["sequence_length"]),
            seed=int(cfg.get("record_seed", int(cfg["seed"]) + 101)),
        )
        manifest_path = path.parent.parent / str(cfg["manifest"])
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        if metadata["pool_sha256"] != manifest["record_metadata"]["pool_sha256"]:
            raise RuntimeError(f"Regenerated record pool disagrees with {manifest_path}")
        targets = int(cfg["targets"])
        references = int(cfg.get("reference_records", 0))
        populations[label] = {
            "config": str(path),
            "pool_sha256": metadata["pool_sha256"],
            "candidate_hashes": _row_hashes(records[:targets]),
            "candidate_reference_hashes": _row_hashes(records[: targets + references]),
        }

    comparisons = []
    for first, second in combinations(populations, 2):
        first_targets = set(populations[first]["candidate_hashes"])
        second_targets = set(populations[second]["candidate_hashes"])
        first_audit = set(populations[first]["candidate_reference_hashes"])
        second_audit = set(populations[second]["candidate_reference_hashes"])
        comparisons.append(
            {
                "first": first,
                "second": second,
                "exact_candidate_overlap": len(first_targets & second_targets),
                "exact_candidate_or_reference_overlap": len(first_audit & second_audit),
            }
        )
    if any(row["exact_candidate_or_reference_overlap"] for row in comparisons):
        raise RuntimeError("Independent populations contain an exactly repeated audit record")

    output = Path("reports/gptq_population_record_disjointness.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "protocol": "SHA-256 comparison of every tokenized candidate and reference row",
                "populations": populations,
                "comparisons": comparisons,
            },
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")
    print(json.dumps({"report": str(output), "comparisons": comparisons}, sort_keys=True))


if __name__ == "__main__":
    main()
