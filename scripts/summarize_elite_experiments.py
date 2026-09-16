"""Summarize the strengthened experiment matrix and enforce matched-population claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_REPORTS = (
    "reports/gptq_natural_postcutoff_report.json",
    "reports/awq_natural_postcutoff_report.json",
    "reports/gptq_pythia410m_natural_report.json",
    "reports/gptq_homogeneous_no_nonce_report.json",
    "reports/matched_gptq_report.json",
    "reports/matched_autoround_report.json",
    "reports/scale_gptq_n64_w4_report.json",
    "reports/scale_gptq_n128_w4_report.json",
    "reports/scale_gptq_n256_w4_report.json",
    "reports/scale_gptq_n128_w8_report.json",
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _row(path: Path, report: dict[str, Any]) -> dict[str, Any]:
    artifact = report["selected_artifact_feature"]
    output = report["selected_output_baseline"]
    crossfit = report["candidate_generalization"]["metrics"]
    utility = report.get("reference_utility") or {}
    return {
        "report": str(path),
        "library": report["library"],
        "method": report.get("method") or (
            "AutoRound" if "round" in report["library"].lower() else "GPTQ"
        ),
        "model": report["model"],
        "model_dtype": report.get("model_dtype", "float16"),
        "bits": report["bits"],
        "calibration_size": report["calibration_size"],
        "record_source": (report.get("record_metadata") or {}).get("source", "legacy"),
        "record_pool_sha256": (report.get("record_metadata") or {}).get("pool_sha256"),
        "selected_artifact_feature": artifact,
        "artifact_auroc": report["metrics"][artifact]["auroc"],
        "selected_output_feature": output,
        "output_auroc": report["metrics"][output]["auroc"],
        "unseen_candidate_artifact_auroc": crossfit["selected_artifact"]["auroc"],
        "unseen_candidate_output_auroc": crossfit["selected_output"]["auroc"],
        "randomization_p": report["fixed_degree_randomization_test"]["p_value_greater_equal"],
        "reference_logprob_change": utility.get("mean_logprob_change"),
        "reference_perplexity_ratio": utility.get("perplexity_ratio_quantized_over_base"),
        "population_sha256": report.get("population_sha256"),
        "experiment_sha256": report.get("experiment_sha256"),
    }


def _scaling_manifest(report_path: str) -> dict[str, Any]:
    stem = Path(report_path).stem.removesuffix("_report")
    path = Path("results") / f"{stem}_population.json"
    if not path.exists():
        raise RuntimeError(f"Missing scaling population manifest {path}")
    return _load(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/elite_experiment_summary.md"))
    args = parser.parse_args()
    paths = args.reports or [Path(value) for value in DEFAULT_REPORTS]
    rows = [_row(path, _load(path)) for path in paths if path.exists()]
    if not rows:
        raise RuntimeError("No completed strengthened reports were found")

    by_name = {Path(row["report"]).stem: row for row in rows}
    gptq = by_name.get("matched_gptq_report")
    autoround = by_name.get("matched_autoround_report")
    matched_population = None
    if gptq and autoround:
        matched_population = gptq["population_sha256"] == autoround["population_sha256"]
        if not matched_population:
            raise RuntimeError("The matched GPTQ and AutoRound population hashes differ")

    natural_gptq = by_name.get("gptq_natural_postcutoff_report")
    natural_awq = by_name.get("awq_natural_postcutoff_report")
    awq_natural_population_match = None
    if natural_gptq and natural_awq:
        awq_natural_population_match = (
            natural_gptq["population_sha256"] == natural_awq["population_sha256"]
            and natural_gptq["record_pool_sha256"] == natural_awq["record_pool_sha256"]
        )
        if not awq_natural_population_match:
            raise RuntimeError("The natural-text GPTQ and AWQ populations differ")

    scaling = [row for row in rows if Path(row["report"]).stem.startswith("scale_gptq_")]
    scaling_record_pool_verified = None
    scaling_membership_verified = None
    if len(scaling) >= 2:
        scaling_record_pool_verified = len(
            {row["record_pool_sha256"] for row in scaling}
        ) == 1
        if not scaling_record_pool_verified:
            raise RuntimeError("Scaling runs do not share one tokenized record pool")
        manifests = [_scaling_manifest(row["report"]) for row in scaling]
        reference = manifests[0]
        scaling_membership_verified = all(
            manifest["membership"] == reference["membership"]
            and manifest["targets"] == reference["targets"]
            and manifest["reference_records"] == reference["reference_records"]
            and manifest["shadow_artifacts"] == reference["shadow_artifacts"]
            and manifest["test_artifacts"] == reference["test_artifacts"]
            for manifest in manifests[1:]
        )
        if not scaling_membership_verified:
            raise RuntimeError("Scaling runs do not share the same membership design")

    payload = {
        "matched_population_verified": matched_population,
        "awq_natural_population_match": awq_natural_population_match,
        "scaling_record_pool_verified": scaling_record_pool_verified,
        "scaling_membership_verified": scaling_membership_verified,
        "runs": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        handle.write("# Strengthened experiment summary\n\n")
        handle.write(f"Exact GPTQ/AutoRound population match: `{matched_population}`.\n\n")
        handle.write(
            f"Exact natural-text GPTQ/AWQ population match: `{awq_natural_population_match}`.\n\n"
        )
        handle.write(
            f"Scaling sweep token-pool match: `{scaling_record_pool_verified}`.\n\n"
        )
        handle.write(
            f"Scaling sweep membership-design match: `{scaling_membership_verified}`.\n\n"
        )
        handle.write(
            "| Run | Method | Compute | W | N | Source | Artifact AUROC | Output AUROC | "
            "Unseen-candidate artifact | Unseen-candidate output | Reference PPL ratio |\n"
        )
        handle.write("|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|\n")
        for row in rows:
            ratio = row["reference_perplexity_ratio"]
            ratio_text = f"{ratio:.4f}" if ratio is not None else "n/a"
            handle.write(
                f"| {Path(row['report']).stem} | {row['method']} | {row['model_dtype']} | "
                f"{row['bits']} | "
                f"{row['calibration_size']} | {row['record_source']} | "
                f"{row['artifact_auroc']:.4f} | {row['output_auroc']:.4f} | "
                f"{row['unseen_candidate_artifact_auroc']:.4f} | "
                f"{row['unseen_candidate_output_auroc']:.4f} | "
                f"{ratio_text} |\n"
            )
    with args.output.with_suffix(".json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "runs": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
