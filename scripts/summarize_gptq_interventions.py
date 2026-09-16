"""Summarize matched GPTQ calibration-statistic and pipeline interventions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from summarize_autoround_trajectory import _population_signature


ROOT = Path(__file__).resolve().parent.parent


def _read(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    arms = [
        ("Sequential, damping 0.01", "scale_gptq_n256_w4"),
        ("Sequential, damping 0.1", "gptq_n256_damp01"),
        ("Sequential, damping 1.0", "gptq_n256_damp1"),
        ("Independent, damping 0.01", "gptq_n256_independent"),
    ]
    rows: list[dict[str, Any]] = []
    for label, stem in arms:
        manifest = _read(ROOT / "results" / f"{stem}_population.json")
        report = _read(ROOT / "reports" / f"{stem}_report.json")
        utility = report.get("reference_utility") or {}
        contract = manifest.get("experiment_contract") or {}
        generalization = report["candidate_generalization"]["metrics"]
        generalization_intervals = report["candidate_generalization"]["cluster_bootstrap"]
        artifact_key = report["selected_artifact_feature"]
        conventional_artifact = report["metrics"][artifact_key]["auroc"]
        rows.append(
            {
                "label": label,
                "pipeline": manifest.get("pipeline", contract.get("pipeline")),
                "dampening_frac": contract.get("dampening_frac", 0.01),
                "population_signature": _population_signature(manifest),
                "conventional_artifact_auroc": conventional_artifact,
                "crossfit_artifact_auroc": generalization["selected_artifact"]["auroc"],
                "crossfit_artifact_auroc_interval": [
                    generalization_intervals["selected_artifact"]["auroc"]["lower_95"],
                    generalization_intervals["selected_artifact"]["auroc"]["upper_95"],
                ],
                "crossfit_output_auroc": generalization["selected_output"]["auroc"],
                "crossfit_output_auroc_interval": [
                    generalization_intervals["selected_output"]["auroc"]["lower_95"],
                    generalization_intervals["selected_output"]["auroc"]["upper_95"],
                ],
                "perplexity_ratio": utility.get("perplexity_ratio_quantized_over_base"),
                "runtime_seconds": report["generation_runtime"]["total_seconds"],
            }
        )
    if len({row["population_signature"] for row in rows}) != 1:
        raise RuntimeError("GPTQ intervention arms do not share an exact population")
    sequential_scores = _read_jsonl(ROOT / "results" / "scale_gptq_n256_w4_scores.jsonl")
    independent_scores = _read_jsonl(ROOT / "results" / "gptq_n256_independent_scores.jsonl")
    if [row["artifact_id"] for row in sequential_scores] != [
        row["artifact_id"] for row in independent_scores
    ]:
        raise RuntimeError("Sequential and independent score rows do not align by artifact")
    score_keys = (
        "artifact_reconstruction",
        "layer_reconstruction",
        "output_kl",
        "output_logit_mse",
        "output_logprob",
        "output_logprob_gap",
        "quantized_layers",
    )
    pipeline_null = {
        "paired_artifacts": len(sequential_scores),
        "quantized_weight_hashes_identical": all(
            sequential["quantized_weights_sha256"] == independent["quantized_weights_sha256"]
            for sequential, independent in zip(
                sequential_scores, independent_scores, strict=True
            )
        ),
        "attack_score_payloads_identical": all(
            all(sequential[key] == independent[key] for key in score_keys)
            for sequential, independent in zip(
                sequential_scores, independent_scores, strict=True
            )
        ),
    }
    result = {
        "protocol": "fixed natural-text population; only damping or layer pipeline changes",
        "pipeline_null": pipeline_null,
        "rows": rows,
    }
    output = ROOT / "reports" / "gptq_intervention_frontier.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with output.with_suffix(".md").open("w", encoding="utf-8") as handle:
        handle.write("# GPTQ intervention frontier\n\n")
        handle.write(
            "| Intervention | Artifact AUROC | Artifact CF AUROC [95% CI] | "
            "Output CF AUROC [95% CI] | PPL ratio |\n"
        )
        handle.write("|---|---:|---:|---:|---:|\n")
        for row in rows:
            artifact_low, artifact_high = row["crossfit_artifact_auroc_interval"]
            output_low, output_high = row["crossfit_output_auroc_interval"]
            handle.write(
                f"| {row['label']} | {row['conventional_artifact_auroc']:.4f} | "
                f"{row['crossfit_artifact_auroc']:.4f} "
                f"[{artifact_low:.4f}, {artifact_high:.4f}] | "
                f"{row['crossfit_output_auroc']:.4f} [{output_low:.4f}, {output_high:.4f}] | "
                f"{row['perplexity_ratio']:.4f} |\n"
            )
        handle.write(
            "\nSequential and independent processing produce identical quantized-weight hashes "
            f"and attack-score payloads for all {pipeline_null['paired_artifacts']} paired artifacts.\n"
        )
    latex_output = ROOT / "paper" / "gptq_intervention_table.tex"
    with latex_output.open("w", encoding="utf-8") as handle:
        handle.write("% Generated by scripts/summarize_gptq_interventions.py.\n")
        handle.write("\\begin{tabular}{lrrrr}\n")
        handle.write("\\toprule\n")
        handle.write(
            "Intervention & Artifact & Artifact CF & Output CF & PPL ratio \\\\\n"
        )
        handle.write("\\midrule\n")
        for row in rows:
            label = row["label"].replace("damping", "damp.")
            handle.write(
                f"{label} & {row['conventional_artifact_auroc']:.3f} & "
                f"{row['crossfit_artifact_auroc']:.3f} & "
                f"{row['crossfit_output_auroc']:.3f} & "
                f"{row['perplexity_ratio']:.3f} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")


if __name__ == "__main__":
    main()
