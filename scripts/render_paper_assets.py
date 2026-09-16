"""Render manuscript tables and figures directly from completed JSON reports."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter, NullLocator

# --- Camera-ready figure style -------------------------------------------------
# Figures are rendered at their final printed width so no LaTeX rescaling occurs and
# every figure carries the same physical type size. NeurIPS text width is 5.5in.
TEXT_WIDTH_IN = 5.5
NARROW_WIDTH_IN = 0.72 * TEXT_WIDTH_IN

# Okabe-Ito bluish green and reddish purple, chosen for color-vision accessibility.
ARTIFACT_COLOR = "#009E73"
OUTPUT_COLOR = "#CC79A7"
RULE_COLOR = "#595959"
BAND_ALPHA = 0.15


def _style() -> None:
    """Match the manuscript's Times typography and embed Type 42 fonts.

    Matplotlib defaults to Type 3 fonts in PDF output, which camera-ready checks at
    most venues reject, so the font type is pinned explicitly.
    """
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIXGeneral", "Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 8.0,
            "axes.labelsize": 8.0,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "axes.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "lines.linewidth": 1.3,
            "lines.markersize": 3.6,
            "legend.frameon": False,
            "legend.handlelength": 1.6,
            "legend.columnspacing": 1.4,
            "legend.handletextpad": 0.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.012,
        }
    )


def _chance_line(axis, *, orientation: str = "h") -> None:
    """Draw the AUROC chance reference, which is the meaningful baseline for every panel.

    Each caller annotates the rule itself, because the free space differs per panel.
    """
    draw = axis.axhline if orientation == "h" else axis.axvline
    draw(0.5, color=RULE_COLOR, linewidth=0.7, linestyle=(0, (1, 2)), zorder=1)


def _save(fig, figure_dir: Path, name: str) -> None:
    for suffix in ("pdf", "png"):
        fig.savefig(figure_dir / f"{name}.{suffix}", dpi=400)
    plt.close(fig)


DEFAULT_REPORTS = (
    "reports/gptq_natural_postcutoff_report.json",
    "reports/autoround_natural_postcutoff_iters200_report.json",
    "reports/awq_natural_postcutoff_report.json",
    "reports/gptq_pythia410m_natural_report.json",
    "reports/gptq_pythia1p4b_stackexchange_report.json",
    "reports/gptq_homogeneous_no_nonce_report.json",
    "reports/matched_gptq_report.json",
    "reports/matched_autoround_report.json",
    "reports/scale_gptq_n64_w4_report.json",
    "reports/scale_gptq_n128_w4_report.json",
    "reports/scale_gptq_n256_w4_report.json",
    "reports/scale_gptq_n128_w8_report.json",
)

AUXILIARY_REPORTS = (
    "reports/gptq_natural_fresh1_report.json",
    "reports/gptq_natural_fresh2_report.json",
    "reports/autoround_iters0_report.json",
    "reports/autoround_iters10_report.json",
    "reports/autoround_iters50_report.json",
    "reports/autoround_iters200_report.json",
    "reports/autoround_natural_postcutoff_iters0_report.json",
    "reports/autoround_natural_postcutoff_iters50_report.json",
    "reports/gptq_n256_damp01_report.json",
    "reports/gptq_n256_damp1_report.json",
    "reports/gptq_n256_independent_report.json",
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _selected(report: dict[str, Any], kind: str) -> tuple[str, float, tuple[float, float]]:
    if kind == "artifact":
        key = report["selected_artifact_feature"]
    else:
        key = report["selected_output_baseline"]
    point = float(report["metrics"][key]["auroc"])
    interval = report["cluster_bootstrap"][key]["auroc"]
    return key, point, (float(interval["lower_95"]), float(interval["upper_95"]))


def _crossfit(report: dict[str, Any], kind: str) -> float:
    key = "selected_artifact" if kind == "artifact" else "selected_output"
    return float(report["candidate_generalization"]["metrics"][key]["auroc"])


def _source(report: dict[str, Any]) -> str:
    metadata = report.get("record_metadata") or {}
    source = metadata.get("source", "legacy")
    if source == "text_jsonl":
        sources = metadata.get("sources") or []
        if any("Stack Exchange" in str(value) for value in sources):
            return "Stack Ex."
        return "natural language"
    distribution = metadata.get("distribution") or {}
    nonce = distribution.get("nonce_length")
    if source == "synthetic" and nonce == 0:
        if distribution.get("topic_size") == distribution.get("vocabulary_size"):
            return "shared support"
        return "latent topics"
    return str(source)


def _method(report: dict[str, Any]) -> str:
    if report.get("method"):
        return str(report["method"])
    library = str(report["library"])
    if "llmcompressor" in library.lower() or "llm-compressor" in library.lower():
        return "GPTQ"
    if "round" in library.lower():
        return "AutoRound"
    return library


def _model(report: dict[str, Any]) -> str:
    name = str(report["model"])
    if "opt-125m" in name.lower():
        return "OPT-125M"
    if "pythia-410m" in name.lower():
        return "Pythia-410M"
    if "pythia-1.4b" in name.lower():
        return "Pythia-1.4B"
    return name.replace("_", r"\_")


def _dtype(report: dict[str, Any]) -> str:
    value = str(report.get("model_dtype", "float16")).lower()
    return {
        "float16": "FP16",
        "bfloat16": "BF16",
        "float32": "FP32",
    }.get(value, value)


def _write_table(reports: list[tuple[Path, dict[str, Any]]], output: Path) -> None:
    rows = []
    for path, report in reports:
        if path.stem.startswith("scale_gptq_"):
            continue
        _, artifact, artifact_ci = _selected(report, "artifact")
        _, output_score, output_ci = _selected(report, "output")
        rows.append(
            (
                _model(report),
                _method(report),
                int(report["bits"]),
                int(report["calibration_size"]),
                _source(report),
                artifact,
                artifact_ci,
                output_score,
                output_ci,
                _crossfit(report, "artifact"),
                _crossfit(report, "output"),
            )
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("% Generated by scripts/render_paper_assets.py.\n")
        handle.write("\\begin{tabular}{llrrlrrrr}\n")
        handle.write("\\toprule\n")
        handle.write(
            "Model & PTQ & W & N & Records & Artifact & Output & "
            "Artifact CF & Output CF \\\\\n"
        )
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{row[0]} & {row[1]} & {row[2]} & {row[3]} & {row[4]} & "
                f"{row[5]:.3f} & {row[7]:.3f} & {row[9]:.3f} & {row[10]:.3f} \\\\\n"
            )
        handle.write("\\bottomrule\n\\end{tabular}\n")


def _write_settings_table(reports: list[tuple[Path, dict[str, Any]]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("% Generated by scripts/render_paper_assets.py.\n")
        handle.write("\\begin{tabular}{llllrrrrrrrrr}\n")
        handle.write("\\toprule\n")
        handle.write(
            "Model & PTQ & Compute & Records & W & N & Length & Targets & Shadow & Test & Refs & Mean s & Total min \\\\\n"
        )
        handle.write("\\midrule\n")
        for _, report in reports:
            runtime = report.get("generation_runtime") or {}
            mean_seconds = runtime.get("mean_seconds_per_artifact")
            total_seconds = runtime.get("total_seconds")
            mean_text = "--" if mean_seconds is None else f"{float(mean_seconds):.1f}"
            total_text = "--" if total_seconds is None else f"{float(total_seconds) / 60:.1f}"
            handle.write(
                f"{_model(report)} & {_method(report)} & {_dtype(report)} & {_source(report)} & "
                f"{int(report['bits'])} & {int(report['calibration_size'])} & "
                f"{int(report['sequence_length'])} & {int(report['targets'])} & "
                f"{int(report['shadow_artifacts'])} & {int(report['test_artifacts'])} & "
                f"{int(report['reference_records'])} & {mean_text} & {total_text} \\\\\n"
            )
        handle.write("\\bottomrule\n\\end{tabular}\n")


def _write_macros(
    reports: list[tuple[Path, dict[str, Any]]],
    output: Path,
    transfer_reports: list[dict[str, Any]] | None = None,
) -> None:
    prefixes = {
        "matched_gptq_report": "matchedGptq",
        "matched_autoround_report": "matchedAutoround",
        "autoround_iters0_report": "autoroundIterZero",
        "autoround_iters10_report": "autoroundIterTen",
        "autoround_iters50_report": "autoroundIterFifty",
        "autoround_iters200_report": "autoroundIterTwoHundred",
        "gptq_homogeneous_no_nonce_report": "noNonce",
        "gptq_natural_postcutoff_report": "natural",
        "gptq_natural_fresh1_report": "freshOne",
        "gptq_natural_fresh2_report": "freshTwo",
        "autoround_natural_postcutoff_iters0_report": "naturalAutoroundIterZero",
        "autoround_natural_postcutoff_iters50_report": "naturalAutoroundIterFifty",
        "autoround_natural_postcutoff_iters200_report": "naturalAutoround",
        "awq_natural_postcutoff_report": "awqNatural",
        "gptq_pythia410m_natural_report": "pythia",
        "gptq_pythia1p4b_stackexchange_report": "pythiaOneFour",
        "scale_gptq_n64_w4_report": "scaleNsixtyfourWfour",
        "scale_gptq_n128_w4_report": "scaleNoneTwentyeightWfour",
        "scale_gptq_n256_w4_report": "scaleNtwoFiftysixWfour",
        "scale_gptq_n128_w8_report": "scaleNoneTwentyeightWeight",
        "gptq_n256_damp01_report": "gptqDampPointOne",
        "gptq_n256_damp1_report": "gptqDampOne",
        "gptq_n256_independent_report": "gptqIndependent",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("% Generated by scripts/render_paper_assets.py.\n")
        for path, report in reports:
            prefix = prefixes.get(path.stem)
            if prefix is None:
                continue
            artifact_key, artifact, _ = _selected(report, "artifact")
            output_key, output_score, _ = _selected(report, "output")
            difference_key = f"artifact_minus_{output_key}_auroc"
            difference = float(report[difference_key])
            interval = report["cluster_bootstrap"][difference_key]
            crossfit = report["candidate_generalization"]
            crossfit_bootstrap = crossfit["cluster_bootstrap"]
            utility = report.get("reference_utility") or {}
            artifact_interval = report["cluster_bootstrap"][artifact_key]["auroc"]
            output_interval = report["cluster_bootstrap"][output_key]["auroc"]
            artifact_metrics = report["metrics"][artifact_key]
            operating_point = report["shadow_calibrated_operating_points"][artifact_key][
                "1pct_target_fpr"
            ]
            values = {
                "ArtifactAuroc": artifact,
                "ArtifactAurocLow": float(artifact_interval["lower_95"]),
                "ArtifactAurocHigh": float(artifact_interval["upper_95"]),
                "OutputAuroc": output_score,
                "OutputAurocLow": float(output_interval["lower_95"]),
                "OutputAurocHigh": float(output_interval["upper_95"]),
                "Gap": difference,
                "GapLow": float(interval["lower_95"]),
                "GapHigh": float(interval["upper_95"]),
                "CrossfitArtifactAuroc": float(
                    crossfit["metrics"]["selected_artifact"]["auroc"]
                ),
                "CrossfitArtifactAurocLow": float(
                    crossfit_bootstrap["selected_artifact"]["auroc"]["lower_95"]
                ),
                "CrossfitArtifactAurocHigh": float(
                    crossfit_bootstrap["selected_artifact"]["auroc"]["upper_95"]
                ),
                "CrossfitOutputAuroc": float(
                    crossfit["metrics"]["selected_output"]["auroc"]
                ),
                "CrossfitOutputAurocLow": float(
                    crossfit_bootstrap["selected_output"]["auroc"]["lower_95"]
                ),
                "CrossfitOutputAurocHigh": float(
                    crossfit_bootstrap["selected_output"]["auroc"]["upper_95"]
                ),
                "RandomizationP": float(
                    report["fixed_degree_randomization_test"]["p_value_greater_equal"]
                ),
                "ArtifactTprAtOnePctFpr": float(artifact_metrics["tpr_at_1pct_fpr"]),
                "ArtifactTprAtPointOnePctFpr": float(
                    artifact_metrics["tpr_at_0_1pct_fpr"]
                ),
                "ShadowThresholdTestFpr": float(operating_point["test_fpr"]),
                "ShadowThresholdTestTpr": float(operating_point["test_tpr"]),
                "TestDecisions": int(report["test_decisions"]),
                "TestNonmembers": int(report["test_nonmembers"]),
            }
            fit_free = report.get("fit_free_fixed_score") or {}
            fit_free_metrics = fit_free.get("metrics") or {}
            fit_free_bootstrap = fit_free.get("cluster_bootstrap") or {}
            raw_fixed = fit_free_metrics.get("raw_fixed_formula")
            raw_fixed_ci = (
                fit_free_bootstrap.get("raw_fixed_formula", {}).get("auroc")
                if fit_free_bootstrap
                else None
            )
            if raw_fixed is not None and raw_fixed_ci is not None:
                values.update(
                    {
                        "RawFixedAuroc": float(raw_fixed["auroc"]),
                        "RawFixedAurocLow": float(raw_fixed_ci["lower_95"]),
                        "RawFixedAurocHigh": float(raw_fixed_ci["upper_95"]),
                    }
                )
            per_artifact = (
                report.get("per_artifact_auroc", {}).get(artifact_key)
                or {}
            )
            if per_artifact:
                values.update(
                    {
                        "PerArtifactAurocMin": float(per_artifact["minimum"]),
                        "PerArtifactAurocMedian": float(per_artifact["median"]),
                        "PerArtifactAurocMax": float(per_artifact["maximum"]),
                    }
                )
            crossfit_per_artifact = (
                crossfit.get("per_artifact_auroc", {}).get("selected_artifact")
                or {}
            )
            if crossfit_per_artifact:
                values.update(
                    {
                        "CrossfitPerArtifactAurocMin": float(
                            crossfit_per_artifact["minimum"]
                        ),
                        "CrossfitPerArtifactAurocMedian": float(
                            crossfit_per_artifact["median"]
                        ),
                        "CrossfitPerArtifactAurocMax": float(
                            crossfit_per_artifact["maximum"]
                        ),
                    }
                )
            ratio = utility.get("perplexity_ratio_quantized_over_base")
            if ratio is not None:
                values["ReferencePplRatio"] = float(ratio)
            handle.write(f"% {path.as_posix()}; artifact={artifact_key}; output={output_key}\n")
            for suffix, value in values.items():
                formatted = (
                    f"{value:,}".replace(",", "{,}")
                    if isinstance(value, int)
                    else f"{value:.4f}"
                )
                handle.write(f"\\providecommand{{\\{prefix}{suffix}}}{{}}\n")
                handle.write(f"\\renewcommand{{\\{prefix}{suffix}}}{{{formatted}}}\n")
        for transfer_report in transfer_reports or []:
            for transfer in transfer_report["transfers"]:
                direction = (transfer["source_method"], transfer["target_method"])
                prefix = {
                    ("GPTQ", "AutoRound"): "transferGptqToAutoround",
                    ("AutoRound", "GPTQ"): "transferAutoroundToGptq",
                    ("GPTQ", "AWQ"): "transferGptqToAwq",
                    ("AWQ", "GPTQ"): "transferAwqToGptq",
                }.get(direction)
                if prefix is None:
                    continue
                for key, suffix in (
                    ("selected_artifact", "ArtifactAuroc"),
                    ("selected_output", "OutputAuroc"),
                ):
                    point = float(transfer["metrics"][key]["auroc"])
                    interval = transfer["cluster_bootstrap"][key]["auroc"]
                    values = {
                        suffix: point,
                        f"{suffix}Low": float(interval["lower_95"]),
                        f"{suffix}High": float(interval["upper_95"]),
                    }
                    for name, value in values.items():
                        handle.write(f"\\providecommand{{\\{prefix}{name}}}{{}}\n")
                        handle.write(f"\\renewcommand{{\\{prefix}{name}}}{{{value:.4f}}}\n")


def _mechanism_figure(by_stem: dict[str, dict[str, Any]], figure_dir: Path) -> None:
    natural_keys = (
        "gptq_natural_postcutoff_report",
        "autoround_natural_postcutoff_iters200_report",
    )
    synthetic_keys = ("matched_gptq_report", "matched_autoround_report")
    keys = natural_keys if all(key in by_stem for key in natural_keys) else synthetic_keys
    if any(key not in by_stem for key in keys):
        return
    reports = [by_stem[key] for key in keys]
    artifact_selected = [
        (
            "selected_artifact",
            float(report["candidate_generalization"]["metrics"]["selected_artifact"]["auroc"]),
            (
                float(report["candidate_generalization"]["cluster_bootstrap"]["selected_artifact"]["auroc"]["lower_95"]),
                float(report["candidate_generalization"]["cluster_bootstrap"]["selected_artifact"]["auroc"]["upper_95"]),
            ),
        )
        for report in reports
    ]
    output_selected = [
        (
            "selected_output",
            float(report["candidate_generalization"]["metrics"]["selected_output"]["auroc"]),
            (
                float(report["candidate_generalization"]["cluster_bootstrap"]["selected_output"]["auroc"]["lower_95"]),
                float(report["candidate_generalization"]["cluster_bootstrap"]["selected_output"]["auroc"]["upper_95"]),
            ),
        )
        for report in reports
    ]
    artifact = np.asarray([value[1] for value in artifact_selected])
    output = np.asarray([value[1] for value in output_selected])
    artifact_error = np.asarray(
        [[point - interval[0], interval[1] - point] for _, point, interval in artifact_selected]
    ).T
    output_error = np.asarray(
        [[point - interval[0], interval[1] - point] for _, point, interval in output_selected]
    ).T
    # A dot-and-interval plot, not bars: AUROC is bounded below by chance at 0.5, so bars
    # drawn from zero waste the panel and bars truncated at 0.45 would exaggerate the contrast.
    _style()
    fig, axis = plt.subplots(figsize=(NARROW_WIDTH_IN, 1.72))
    rows = np.asarray([1.0, 0.0])
    names = ("GPTQ", "AutoRound")
    axis.set_axisbelow(True)
    axis.grid(axis="x", color="0.90", linewidth=0.5)
    for index, row in enumerate(rows):
        axis.plot(
            [output[index], artifact[index]],
            [row, row],
            color="0.75",
            linewidth=0.9,
            solid_capstyle="round",
            zorder=2,
        )
    for values, errors, color, label in (
        (artifact, artifact_error, ARTIFACT_COLOR, "Artifact"),
        (output, output_error, OUTPUT_COLOR, "Output (one candidate query)"),
    ):
        axis.errorbar(
            values,
            rows,
            xerr=errors,
            fmt="o",
            color=color,
            markersize=4.4,
            markeredgecolor="white",
            markeredgewidth=0.6,
            elinewidth=1.0,
            capsize=1.8,
            capthick=0.9,
            label=label,
            zorder=3,
        )
        for index, value in enumerate(values):
            axis.annotate(
                f"{value:.3f}",
                xy=(value, rows[index]),
                xytext=(0, -7.5),
                textcoords="offset points",
                ha="center",
                va="top",
                fontsize=6.8,
                color="0.25",
            )
    # Direct labels on the top row carry series identity, so colour is never the only cue.
    for value, color, label, align in (
        (artifact[0], ARTIFACT_COLOR, "Artifact", "center"),
        (output[0], OUTPUT_COLOR, "Output", "center"),
    ):
        axis.annotate(
            label,
            xy=(value, rows[0]),
            xytext=(0, 8),
            textcoords="offset points",
            ha=align,
            va="bottom",
            fontsize=7.5,
            color=color,
        )
    _chance_line(axis, orientation="v")
    axis.annotate(
        "chance",
        xy=(0.5, -0.48),
        xytext=(0, 0),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=6.8,
        color=RULE_COLOR,
    )
    axis.set_yticks(rows, names)
    axis.set_ylim(-0.58, 1.46)
    axis.set_xlim(0.44, 1.06)
    axis.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    axis.set_xlabel("Candidate-cross-fitted held-out AUROC")
    axis.spines["left"].set_visible(False)
    axis.tick_params(axis="y", length=0)
    fig.tight_layout(pad=0.2)
    _save(fig, figure_dir, "mechanism_locus")


def _autoround_trajectory_figure(
    by_stem: dict[str, dict[str, Any]], figure_dir: Path
) -> None:
    groups = (
        (
            "exchangeable synthetic",
            (
                "autoround_iters0_report",
                "autoround_iters10_report",
                "autoround_iters50_report",
                "autoround_iters200_report",
            ),
        ),
        (
            "natural language",
            (
                "autoround_natural_postcutoff_iters0_report",
                "autoround_natural_postcutoff_iters50_report",
                "autoround_natural_postcutoff_iters200_report",
            ),
        ),
    )
    if any(any(key not in by_stem for key in keys) for _, keys in groups):
        return
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(TEXT_WIDTH_IN, 2.05), sharey=True)
    for axis, (title, keys) in zip(axes, groups, strict=True):
        reports = [by_stem[key] for key in keys]
        iterations = np.asarray([int(report["iters"]) for report in reports])
        for kind, label, color in (
            ("selected_artifact", "Artifact", ARTIFACT_COLOR),
            ("selected_output", "Output", OUTPUT_COLOR),
        ):
            points = np.asarray(
                [report["candidate_generalization"]["metrics"][kind]["auroc"] for report in reports]
            )
            intervals = [
                report["candidate_generalization"]["cluster_bootstrap"][kind]["auroc"]
                for report in reports
            ]
            lower = np.asarray([value["lower_95"] for value in intervals])
            upper = np.asarray([value["upper_95"] for value in intervals])
            axis.fill_between(iterations, lower, upper, color=color, alpha=BAND_ALPHA, linewidth=0)
            axis.plot(iterations, points, marker="o", color=color, label=label, zorder=3)
        _chance_line(axis)
        axis.grid(axis="y", color="0.90", linewidth=0.5)
        axis.set_title(title)
        axis.set_xlabel("AutoRound optimization steps")
        axis.set_xticks(iterations)
        axis.set_ylim(0.45, 1.04)
        axis.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    axes[0].set_ylabel("Candidate-cross-fitted AUROC")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=2)
    fig.subplots_adjust(left=0.09, right=0.995, top=0.83, bottom=0.21, wspace=0.08)
    _save(fig, figure_dir, "autoround_trajectory")


def _gptq_damping_figure(by_stem: dict[str, dict[str, Any]], figure_dir: Path) -> None:
    keys = (
        "scale_gptq_n256_w4_report",
        "gptq_n256_damp01_report",
        "gptq_n256_damp1_report",
    )
    if any(key not in by_stem for key in keys):
        return
    reports = [by_stem[key] for key in keys]
    damping = np.asarray([0.01, 0.10, 1.00])
    _style()
    fig, (leakage_axis, utility_axis) = plt.subplots(1, 2, figsize=(TEXT_WIDTH_IN, 1.92))

    conventional = np.asarray([_selected(report, "artifact")[1] for report in reports])
    leakage_axis.plot(
        damping,
        conventional,
        marker="o",
        color=RULE_COLOR,
        linestyle=(0, (3, 2)),
        label="Artifact",
        zorder=3,
    )
    for kind, label, color in (
        ("selected_artifact", "Artifact CF", ARTIFACT_COLOR),
        ("selected_output", "Output CF", OUTPUT_COLOR),
    ):
        points = np.asarray(
            [report["candidate_generalization"]["metrics"][kind]["auroc"] for report in reports]
        )
        intervals = [
            report["candidate_generalization"]["cluster_bootstrap"][kind]["auroc"]
            for report in reports
        ]
        lower = np.asarray([interval["lower_95"] for interval in intervals])
        upper = np.asarray([interval["upper_95"] for interval in intervals])
        leakage_axis.errorbar(
            damping,
            points,
            yerr=np.vstack((points - lower, upper - points)),
            marker="o",
            capsize=2.0,
            color=color,
            label=label,
            zorder=3,
        )
    _chance_line(leakage_axis)
    leakage_axis.set_ylabel("Held-out AUROC")
    leakage_axis.set_ylim(0.45, 1.04)
    leakage_axis.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    leakage_axis.set_title("(a) membership inference")
    leakage_axis.legend(loc="lower left")

    perplexity = np.asarray(
        [
            report["reference_utility"]["perplexity_ratio_quantized_over_base"]
            for report in reports
        ]
    )
    utility_axis.plot(damping, perplexity, marker="o", color=ARTIFACT_COLOR, zorder=3)
    utility_axis.axhline(1.0, color=RULE_COLOR, linewidth=0.7, linestyle=(0, (1, 2)), zorder=1)
    utility_axis.set_ylabel("Quantized/base perplexity")
    utility_axis.set_ylim(min(0.995, float(perplexity.min()) - 0.01), float(perplexity.max()) + 0.01)
    utility_axis.set_title("(b) public-reference utility")

    for axis in (leakage_axis, utility_axis):
        axis.set_xscale("log", base=10)
        axis.set_xticks(damping)
        axis.set_xticklabels(("0.01", "0.10", "1.00"))
        axis.xaxis.set_minor_locator(NullLocator())
        axis.xaxis.set_minor_formatter(NullFormatter())
        axis.set_xlabel("GPTQ Hessian damping fraction")
        axis.set_axisbelow(True)
        axis.grid(axis="y", color="0.90", linewidth=0.5)
    fig.subplots_adjust(left=0.09, right=0.995, top=0.84, bottom=0.24, wspace=0.30)
    _save(fig, figure_dir, "gptq_damping_intervention")


def _layer_figure(by_stem: dict[str, dict[str, Any]], figure_dir: Path) -> None:
    if all(
        key in by_stem
        for key in (
            "gptq_natural_postcutoff_report",
            "autoround_natural_postcutoff_iters200_report",
        )
    ):
        selected = [
            ("GPTQ", by_stem.get("gptq_natural_postcutoff_report"), ARTIFACT_COLOR),
            (
                "AutoRound",
                by_stem.get("autoround_natural_postcutoff_iters200_report"),
                OUTPUT_COLOR,
            ),
        ]
    else:
        selected = [
            ("GPTQ", by_stem.get("matched_gptq_report"), ARTIFACT_COLOR),
            ("AutoRound", by_stem.get("matched_autoround_report"), OUTPUT_COLOR),
        ]
    if any(report is None for _, report, _ in selected):
        return
    _style()
    fig, axis = plt.subplots(figsize=(NARROW_WIDTH_IN, 2.05))
    axis.set_axisbelow(True)
    axis.grid(axis="y", color="0.90", linewidth=0.5)
    last_block = 0
    for label, report, color in selected:
        blocks: dict[int, list[float]] = defaultdict(list)
        assert report is not None
        for row in report["layerwise_artifact_reconstruction"]:
            match = re.search(r"layers\.(\d+)\.", row["layer"])
            if match:
                blocks[int(match.group(1))].append(float(row["auroc"]))
        indices = sorted(blocks)
        last_block = max(last_block, indices[-1])
        median = np.asarray([float(np.median(blocks[index])) for index in indices])
        lower = np.asarray([float(np.percentile(blocks[index], 25)) for index in indices])
        upper = np.asarray([float(np.percentile(blocks[index], 75)) for index in indices])
        # The band shows the interquartile spread of the linear layers inside each block,
        # which the previous median-only line discarded.
        axis.fill_between(indices, lower, upper, color=color, alpha=BAND_ALPHA, linewidth=0)
        axis.plot(indices, median, marker="o", color=color, zorder=3)
        axis.annotate(
            label,
            xy=(indices[-1], median[-1]),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=7.5,
            color=color,
        )
    _chance_line(axis)
    # AutoRound tracks chance closely, so the reference label sits below the rule to avoid it.
    axis.annotate(
        "chance",
        xy=(0, 0.5),
        xytext=(1, -3.0),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=6.8,
        color=RULE_COLOR,
    )
    axis.set_xlabel("Transformer block")
    axis.set_ylabel("Layerwise artifact AUROC")
    axis.set_ylim(0.42, 1.04)
    axis.set_xlim(-0.5, last_block + 2.9)
    axis.set_xticks(range(0, last_block + 1, 2))
    axis.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    fig.tight_layout(pad=0.2)
    _save(fig, figure_dir, "layer_localization")


def _scaling_figure(by_stem: dict[str, dict[str, Any]], figure_dir: Path) -> None:
    keys = ("scale_gptq_n64_w4_report", "scale_gptq_n128_w4_report", "scale_gptq_n256_w4_report")
    if any(key not in by_stem for key in keys):
        return
    reports = sorted((by_stem[key] for key in keys), key=lambda report: report["calibration_size"])
    n_values = np.asarray([report["calibration_size"] for report in reports])
    bit_keys = ("scale_gptq_n128_w4_report", "scale_gptq_n128_w8_report")
    has_bits = all(key in by_stem for key in bit_keys)
    _style()
    if has_bits:
        fig, axes = plt.subplots(
            1,
            2,
            figsize=(TEXT_WIDTH_IN, 2.15),
            sharey=True,
            gridspec_kw={"width_ratios": (1.6, 1.0), "wspace": 0.07},
        )
        size_axis, bit_axis = axes
    else:
        fig, size_axis = plt.subplots(figsize=(NARROW_WIDTH_IN, 2.05))
        bit_axis = None
    for kind, legend_label, color in (
        ("artifact", "Artifact", ARTIFACT_COLOR),
        ("output", "Output (one candidate query)", OUTPUT_COLOR),
    ):
        selected = [_selected(report, kind) for report in reports]
        points = np.asarray([value[1] for value in selected])
        lower = np.asarray([value[2][0] for value in selected])
        upper = np.asarray([value[2][1] for value in selected])
        size_axis.fill_between(n_values, lower, upper, color=color, alpha=BAND_ALPHA, linewidth=0)
        size_axis.plot(n_values, points, marker="o", color=color, label=legend_label, zorder=3)
        if bit_axis is not None:
            bit_reports = [by_stem[key] for key in bit_keys]
            bit_selected = [_selected(report, kind) for report in bit_reports]
            bit_values = np.asarray([report["bits"] for report in bit_reports])
            bit_points = np.asarray([value[1] for value in bit_selected])
            bit_lower = np.asarray([value[2][0] for value in bit_selected])
            bit_upper = np.asarray([value[2][1] for value in bit_selected])
            bit_axis.fill_between(
                bit_values, bit_lower, bit_upper, color=color, alpha=BAND_ALPHA, linewidth=0
            )
            bit_axis.plot(bit_values, bit_points, marker="o", color=color, zorder=3)
    for axis in (size_axis, bit_axis):
        if axis is None:
            continue
        axis.set_axisbelow(True)
        axis.grid(axis="y", color="0.90", linewidth=0.5)
        _chance_line(axis)
        axis.set_ylim(0.45, 1.05)
        axis.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    # Calibration size doubles between settings, so a log scale keeps the spacing honest.
    size_axis.set_xscale("log", base=2)
    size_axis.set_xticks(n_values)
    size_axis.set_xticklabels([str(int(value)) for value in n_values])
    size_axis.xaxis.set_minor_locator(NullLocator())
    size_axis.xaxis.set_minor_formatter(NullFormatter())
    size_axis.set_xlabel("Calibration sequences $N$")
    size_axis.set_ylabel("Held-out AUROC")
    size_axis.annotate(
        "chance",
        xy=(n_values[0], 0.5),
        xytext=(1, 2.5),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=6.8,
        color=RULE_COLOR,
    )
    if bit_axis is not None:
        size_axis.set_title("(a) calibration size", fontsize=8.0, pad=3.0)
        bit_axis.set_title("(b) weight precision", fontsize=8.0, pad=3.0)
        bit_axis.set_xlabel("Weight bits")
        bit_axis.set_xlim(3.4, 8.6)
        bit_axis.set_xticks([4, 8])
        bit_axis.spines["left"].set_visible(False)
        bit_axis.tick_params(axis="y", length=0)
    handles, labels = size_axis.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.0),
        ncols=2,
        borderaxespad=0.0,
    )
    # tight_layout cannot account for a figure-level legend; savefig's tight bbox does.
    fig.subplots_adjust(left=0.093, right=0.995, top=0.90, bottom=0.20)
    _save(fig, figure_dir, "calibration_scaling")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument("--figure-dir", type=Path, default=Path("paper/figures"))
    parser.add_argument("--table", type=Path, default=Path("paper/results_table.tex"))
    parser.add_argument(
        "--settings-table", type=Path, default=Path("paper/experiment_settings.tex")
    )
    parser.add_argument(
        "--macros", type=Path, default=Path("paper/generated_result_macros.tex")
    )
    parser.add_argument(
        "--transfer-report", type=Path, default=Path("reports/cross_quantizer_transfer.json")
    )
    parser.add_argument(
        "--additional-transfer-report",
        type=Path,
        default=Path("reports/cross_quantizer_transfer_natural_awq.json"),
    )
    args = parser.parse_args()
    paths = args.reports or [Path(path) for path in DEFAULT_REPORTS]
    reports = [(path, _load(path)) for path in paths if path.exists()]
    if not reports:
        raise RuntimeError("No completed strengthened reports were found")
    args.figure_dir.mkdir(parents=True, exist_ok=True)
    auxiliary = [
        (Path(path), _load(Path(path))) for path in AUXILIARY_REPORTS if Path(path).exists()
    ]
    _write_table(reports, args.table)
    _write_settings_table(reports, args.settings_table)
    transfer_reports = [
        _load(path)
        for path in (args.transfer_report, args.additional_transfer_report)
        if path.exists()
    ]
    _write_macros([*reports, *auxiliary], args.macros, transfer_reports)
    by_stem = {path.stem: report for path, report in reports}
    figure_reports = {**by_stem, **{path.stem: report for path, report in auxiliary}}
    # The attack schematic is authored in TikZ at paper/figures/attack_pipeline.tex so it
    # inherits the manuscript's Times fonts and math rather than approximating them.
    _mechanism_figure(figure_reports, args.figure_dir)
    _autoround_trajectory_figure(figure_reports, args.figure_dir)
    _gptq_damping_figure(figure_reports, args.figure_dir)
    _layer_figure(figure_reports, args.figure_dir)
    _scaling_figure(by_stem, args.figure_dir)
    print(
        json.dumps(
            {
                "macros": str(args.macros),
                "reports": len(reports),
                "settings_table": str(args.settings_table),
                "table": str(args.table),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
