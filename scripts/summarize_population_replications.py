"""Summarize fully independent natural-text population replications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPORTS = (
    ("original", Path("reports/gptq_natural_postcutoff_report.json")),
    ("fresh 1", Path("reports/gptq_natural_fresh1_report.json")),
    ("fresh 2", Path("reports/gptq_natural_fresh2_report.json")),
)
DISJOINTNESS_REPORT = Path("reports/gptq_population_record_disjointness.json")


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    missing = [str(path) for _, path in REPORTS if not path.exists()]
    if not DISJOINTNESS_REPORT.exists():
        missing.append(str(DISJOINTNESS_REPORT))
    if missing:
        raise FileNotFoundError(f"Population reports remain incomplete: {missing}")
    rows = []
    for name, path in REPORTS:
        report = _load(path)
        artifact_key = report["selected_artifact_feature"]
        raw = report["fit_free_fixed_score"]["metrics"]["raw_fixed_formula"]["auroc"]
        rows.append(
            {
                "population": name,
                "report": str(path),
                "population_sha256": report["population_sha256"],
                "record_pool_sha256": report["record_metadata"]["pool_sha256"],
                "shadow_artifacts": int(report["shadow_artifacts"]),
                "test_artifacts": int(report["test_artifacts"]),
                "test_decisions": int(report["test_decisions"]),
                "selected_artifact_feature": artifact_key,
                "artifact_auroc": float(report["metrics"][artifact_key]["auroc"]),
                "candidate_crossfit_artifact_auroc": float(
                    report["candidate_generalization"]["metrics"]["selected_artifact"]["auroc"]
                ),
                "raw_fixed_auroc": float(raw),
                "minimum_per_artifact_auroc": float(
                    report["per_artifact_auroc"][artifact_key]["minimum"]
                ),
                "minimum_crossfit_per_artifact_auroc": float(
                    report["candidate_generalization"]["per_artifact_auroc"][
                        "selected_artifact"
                    ]["minimum"]
                ),
            }
        )
    population_hashes = {row["population_sha256"] for row in rows}
    record_hashes = {row["record_pool_sha256"] for row in rows}
    if len(population_hashes) != len(rows) or len(record_hashes) != len(rows):
        raise RuntimeError("Fresh replications must have distinct population and record-pool hashes")
    disjointness = _load(DISJOINTNESS_REPORT)
    if any(
        comparison["exact_candidate_or_reference_overlap"]
        for comparison in disjointness["comparisons"]
    ):
        raise RuntimeError("Fresh replications contain an exactly repeated audit record")
    summary = {
        "protocol": (
            "three independently constructed record pools, candidate sets, background sets, "
            "fixed-margin membership matrices, shadow artifacts, and test artifacts"
        ),
        "independent_populations": len(rows),
        "exact_candidate_or_reference_overlap_across_populations": 0,
        "record_disjointness_report": str(DISJOINTNESS_REPORT),
        "total_quantized_artifacts": sum(
            row["shadow_artifacts"] + row["test_artifacts"] for row in rows
        ),
        "total_test_decisions": sum(row["test_decisions"] for row in rows),
        "rows": rows,
        "artifact_auroc_range": [
            min(row["artifact_auroc"] for row in rows),
            max(row["artifact_auroc"] for row in rows),
        ],
        "candidate_crossfit_artifact_auroc_range": [
            min(row["candidate_crossfit_artifact_auroc"] for row in rows),
            max(row["candidate_crossfit_artifact_auroc"] for row in rows),
        ],
        "raw_fixed_auroc_range": [
            min(row["raw_fixed_auroc"] for row in rows),
            max(row["raw_fixed_auroc"] for row in rows),
        ],
    }
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    with (report_dir / "gptq_population_replications.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with (report_dir / "gptq_population_replications.md").open(
        "w", encoding="utf-8"
    ) as handle:
        handle.write("# Independent GPTQ population replications\n\n")
        handle.write(
            f"{summary['independent_populations']} independent populations contain "
            f"{summary['total_quantized_artifacts']} quantized artifacts and "
            f"{summary['total_test_decisions']} held-out decisions.\n\n"
        )
        handle.write(
            "| Population | Shadow | Test | Artifact AUROC | Artifact CF | "
            "Raw fixed | Min artifact AUROC | Min artifact CF AUROC |\n"
        )
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in rows:
            handle.write(
                f"| {row['population']} | {row['shadow_artifacts']} | "
                f"{row['test_artifacts']} | {row['artifact_auroc']:.4f} | "
                f"{row['candidate_crossfit_artifact_auroc']:.4f} | "
                f"{row['raw_fixed_auroc']:.4f} | "
                f"{row['minimum_per_artifact_auroc']:.4f} | "
                f"{row['minimum_crossfit_per_artifact_auroc']:.4f} |\n"
            )
    paper_table = Path("paper/population_replications.tex")
    with paper_table.open("w", encoding="utf-8") as handle:
        handle.write("% Generated by scripts/summarize_population_replications.py.\n")
        handle.write("\\begin{tabular}{lrrrrrr}\n")
        handle.write("\\toprule\n")
        handle.write(
            "Population & Shadow/Test & Decisions & Artifact & Artifact CF & "
            "Raw fixed & Min CF artifact \\\\\n"
        )
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{row['population'].title()} & "
                f"{row['shadow_artifacts']}/{row['test_artifacts']} & "
                f"{row['test_decisions']:,}".replace(",", "{,}")
                + f" & {row['artifact_auroc']:.4f} & "
                f"{row['candidate_crossfit_artifact_auroc']:.4f} & "
                f"{row['raw_fixed_auroc']:.4f} & "
                f"{row['minimum_crossfit_per_artifact_auroc']:.3f} \\\\\n"
            )
        handle.write("\\bottomrule\n\\end{tabular}\n")


if __name__ == "__main__":
    main()
