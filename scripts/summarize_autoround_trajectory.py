"""Validate matched AutoRound populations and summarize optimization trajectories."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent


def _read(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _population_signature(manifest: dict[str, Any]) -> str:
    payload = {
        "seed": manifest["seed"],
        "calibration_size": manifest["calibration_size"],
        "targets": manifest["targets"],
        "shadow_artifacts": manifest["shadow_artifacts"],
        "test_artifacts": manifest["test_artifacts"],
        "pool_size": manifest["pool_size"],
        "reference_records": manifest.get("reference_records", 0),
        "record_pool_sha256": manifest.get("record_pool_sha256"),
        "membership": manifest["membership"],
        "calibration_indices_sha256": [
            artifact["calibration_indices_sha256"] for artifact in manifest["artifacts"]
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _row(label: str, corpus: str, manifest_path: Path, report_path: Path) -> dict[str, Any]:
    manifest = _read(manifest_path)
    report = _read(report_path)
    generalization = report["candidate_generalization"]["metrics"]
    utility = report.get("reference_utility") or {}
    return {
        "label": label,
        "corpus": corpus,
        "iters": int(report["iters"]),
        "population_signature": _population_signature(manifest),
        "selected_artifact_auroc": report["metrics"][report["selected_artifact_feature"]]["auroc"],
        "selected_output_auroc": report["metrics"][report["selected_output_baseline"]]["auroc"],
        "crossfit_artifact_auroc": generalization["selected_artifact"]["auroc"],
        "crossfit_output_auroc": generalization["selected_output"]["auroc"],
        "perplexity_ratio": utility.get("perplexity_ratio_quantized_over_base"),
        "changed_weight_fraction": report.get("mean_changed_weight_fraction_vs_artifact0"),
        "runtime_seconds": report["generation_runtime"]["total_seconds"],
    }


def main() -> None:
    specifications = [
        ("Synthetic 0", "exchangeable synthetic", "autoround_iters0"),
        ("Synthetic 10", "exchangeable synthetic", "autoround_iters10"),
        ("Synthetic 50", "exchangeable synthetic", "autoround_iters50"),
        ("Synthetic 200", "exchangeable synthetic", "autoround_iters200"),
        ("Natural 0", "2024 arXiv cs.LG", "autoround_natural_postcutoff_iters0"),
        ("Natural 50", "2024 arXiv cs.LG", "autoround_natural_postcutoff_iters50"),
        ("Natural 200", "2024 arXiv cs.LG", "autoround_natural_postcutoff_iters200"),
    ]
    rows = [
        _row(
            label,
            corpus,
            ROOT / "results" / f"{stem}_population.json",
            ROOT / "reports" / f"{stem}_report.json",
        )
        for label, corpus, stem in specifications
    ]
    for corpus in sorted({row["corpus"] for row in rows}):
        signatures = {row["population_signature"] for row in rows if row["corpus"] == corpus}
        if len(signatures) != 1:
            raise RuntimeError(f"AutoRound trajectory is not population-matched for {corpus}")
    result = {"protocol": "only AutoRound optimization iterations vary within each corpus", "rows": rows}
    output = ROOT / "reports" / "autoround_optimization_trajectory.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with output.with_suffix(".md").open("w", encoding="utf-8") as handle:
        handle.write("# AutoRound optimization trajectory\n\n")
        handle.write("| Corpus | Iterations | Artifact CF AUROC | Output CF AUROC | PPL ratio |\n")
        handle.write("|---|---:|---:|---:|---:|\n")
        for row in rows:
            ppl = row["perplexity_ratio"]
            handle.write(
                f"| {row['corpus']} | {row['iters']} | {row['crossfit_artifact_auroc']:.4f} | "
                f"{row['crossfit_output_auroc']:.4f} | "
                f"{ppl:.4f} |\n" if ppl is not None else
                f"| {row['corpus']} | {row['iters']} | {row['crossfit_artifact_auroc']:.4f} | "
                f"{row['crossfit_output_auroc']:.4f} | n/a |\n"
            )


if __name__ == "__main__":
    main()
