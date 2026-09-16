"""Collect every named-library replication report into one comparison table.

Usage (from the project root):

    python scripts/summarize_replications.py reports/named_library_replication.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ARTIFACT_FEATURES = ("artifact_reconstruction", "artifact_layer_combination")
ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _interval(report: dict[str, Any]) -> tuple[float, float] | None:
    bootstrap = report.get("cluster_bootstrap", {})
    for key, values in bootstrap.items():
        if key.startswith("artifact_minus_"):
            return values["lower_95"], values["upper_95"]
    return None


def _difference(report: dict[str, Any]) -> float | None:
    for key, value in report.items():
        if key.startswith("artifact_minus_") and isinstance(value, (int, float)):
            return float(value)
    return None


def rows(reports: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    collected = []
    for label, report in reports:
        metrics = report["metrics"]
        artifact_key = report.get("selected_artifact_feature", "artifact_reconstruction")
        baseline_key = report.get("selected_output_baseline", "output_logit_mse")
        best_artifact = max(
            (name for name in ARTIFACT_FEATURES if name in metrics),
            key=lambda name: metrics[name]["auroc"],
        )
        collected.append(
            {
                "label": label,
                "method": report.get("method", "AutoRound"),
                "library": f"{report.get('library', '?')} {report.get('library_version', '')}".strip(),
                "iters": report.get("iters"),
                "fixed_aggregate": metrics.get("artifact_reconstruction", {}).get("auroc"),
                "artifact_selected": metrics[artifact_key]["auroc"],
                "artifact_selected_key": artifact_key,
                "artifact_best_key": best_artifact,
                "artifact_best": metrics[best_artifact]["auroc"],
                "artifact_tpr": metrics[artifact_key]["tpr_at_1pct_fpr"],
                "baseline_key": baseline_key,
                "baseline": metrics[baseline_key]["auroc"],
                "baseline_tpr": metrics[baseline_key]["tpr_at_1pct_fpr"],
                "difference": _difference(report),
                "interval": _interval(report),
                "changed": report.get("mean_changed_weight_fraction_vs_artifact0"),
                "decisions": report.get("test_decisions"),
            }
        )
    return collected


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports/named_library_replication.md"
    candidates: list[tuple[str, Path]] = [
        ("AutoRound iters=0", ROOT / "reports/autoround_iters0_report.json"),
        ("AutoRound iters=10", ROOT / "reports/autoround_iters10_report.json"),
        ("AutoRound iters=50", ROOT / "reports/autoround_iters50_report.json"),
        ("AutoRound iters=200", ROOT / "reports/autoround_iters200_report.json"),
        ("AutoRound iters=200 (no reference)", ROOT / "reports/autoround_attack_report.json"),
        ("GPTQ one-shot", ROOT / "reports/gptq_attack_report.json"),
    ]
    reports = [(label, report) for label, path in candidates if (report := _load(path)) is not None]
    if not reports:
        raise SystemExit("No replication reports found; run the attack pipelines first.")
    table = rows(reports)

    lines = [
        "# CalibTrace named-library replication summary",
        "",
        "Every row is a held-out single-artifact membership evaluation on `facebook/opt-125m` at",
        "W4/N=128 with the same population design: 32 shadow artifacts, 16 held-out artifacts, 32",
        "tracked candidate records, and fixed row and column membership margins. The artifact",
        "feature and the output baseline are both selected on shadow artifacts only.",
        "",
        "| Run | Method | Weights changed by one swap | Artifact AUROC | Output AUROC | Artifact - output | 95% interval |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in table:
        changed = f"{row['changed']:.1%}" if row["changed"] is not None else "n/a"
        interval = (
            f"[{row['interval'][0]:+.4f}, {row['interval'][1]:+.4f}]" if row["interval"] else "n/a"
        )
        difference = f"{row['difference']:+.4f}" if row["difference"] is not None else "n/a"
        lines.append(
            f"| {row['label']} | {row['method']} | {changed} | "
            f"{row['artifact_selected']:.4f} | {row['baseline']:.4f} | {difference} | {interval} |"
        )
    lines += [
        "",
        "## Selected features",
        "",
        "| Run | Artifact feature | Fixed aggregate AUROC | Output baseline | Held-out decisions |",
        "|---|---|---:|---|---:|",
    ]
    for row in table:
        aggregate = f"{row['fixed_aggregate']:.4f}" if row["fixed_aggregate"] is not None else "n/a"
        lines.append(
            f"| {row['label']} | `{row['artifact_selected_key']}` | {aggregate} | "
            f"`{row['baseline_key']}` | {row['decisions']} |"
        )
    lines += [
        "",
        "A positive `artifact - output` value means white-box artifact access recovers calibration",
        "membership better than ordinary output observation of the same released model. A negative",
        "value means the artifact adds nothing beyond what outputs already reveal.",
        "",
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": str(destination), "runs": len(table)}))


if __name__ == "__main__":
    main()
