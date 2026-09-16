from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import apply_overrides, load_config, resolve_path
from .attack import evaluate_attack_population, generate_attack_population, score_attack_population
from .data import load_datasets, write_manifest
from .experiment import run_pilot
from .scores import score_saved_pairs
from .train import train_base


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="calibtrace")
    parser.add_argument("--config", default="configs/pilot.yaml")
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override a dotted configuration key; may be repeated.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare", help="Download CIFAR-100 and write the disjoint split manifest")
    subparsers.add_parser("train", help="Train the fixed full-precision base model")
    subparsers.add_parser("pilot", help="Generate paired W4 artifacts and analyze code fingerprints")
    score_parser = subparsers.add_parser(
        "score", help="Score saved pairs with candidate-specific reconstruction error"
    )
    score_parser.add_argument("--results", default=None)
    subparsers.add_parser(
        "attack-generate", help="Generate the balanced N=128 shadow/test artifact population"
    )
    subparsers.add_parser(
        "attack-score", help="Compute artifact and output scores for the attack population"
    )
    subparsers.add_parser(
        "attack-evaluate", help="Evaluate held-out single-artifact membership inference"
    )
    subparsers.add_parser(
        "autoround-pilot", help="Run the named AutoRound OPT-125M causal replication pilot"
    )
    subparsers.add_parser(
        "autoround-attack-generate",
        help="Quantize and score the named-library shadow/test artifact population",
    )
    subparsers.add_parser(
        "autoround-attack-evaluate",
        help="Evaluate held-out membership inference against the named-library population",
    )
    subparsers.add_parser(
        "gptq-attack-generate",
        help="Quantize and score the llm-compressor GPTQ artifact population",
    )
    subparsers.add_parser(
        "gptq-attack-evaluate",
        help="Evaluate held-out membership inference against the GPTQ population",
    )
    subparsers.add_parser(
        "awq-attack-generate",
        help="Quantize and score the llm-compressor AWQ artifact population",
    )
    subparsers.add_parser(
        "awq-attack-evaluate",
        help="Evaluate held-out membership inference against the AWQ population",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config)
    config = apply_overrides(load_config(config_path), args.set)
    if args.command == "prepare":
        data_cfg = config["data"]
        _, _, _, manifest = load_datasets(
            resolve_path(config_path, config["paths"]["data_dir"]),
            train_per_class=int(data_cfg["train_per_class"]),
            calibration_per_class=int(data_cfg["calibration_per_class"]),
            split_seed=int(data_cfg["split_seed"]),
        )
        path = resolve_path(config_path, config["paths"]["split_manifest"])
        write_manifest(manifest, path)
        print(json.dumps({"manifest": str(path), "sha256": manifest.to_json()["sha256"]}))
    elif args.command == "train":
        print(json.dumps({"checkpoint": str(train_base(config, config_path))}))
    elif args.command == "pilot":
        print(json.dumps({"results": str(run_pilot(config, config_path))}))
    elif args.command == "score":
        print(
            json.dumps(
                {"results": str(score_saved_pairs(config, config_path, args.results))}
            )
        )
    elif args.command == "attack-generate":
        print(json.dumps({"manifest": str(generate_attack_population(config, config_path))}))
    elif args.command == "attack-score":
        print(json.dumps({"scores": str(score_attack_population(config, config_path))}))
    elif args.command == "attack-evaluate":
        print(json.dumps({"report": str(evaluate_attack_population(config, config_path))}))
    elif args.command == "autoround-pilot":
        from .autoround_pilot import run_autoround_pilot

        print(json.dumps({"results": str(run_autoround_pilot(config, config_path))}))
    elif args.command == "autoround-attack-generate":
        from .autoround_attack import generate_autoround_attack

        print(json.dumps({"manifest": str(generate_autoround_attack(config, config_path))}))
    elif args.command == "autoround-attack-evaluate":
        from .autoround_attack import evaluate_autoround_attack

        print(json.dumps({"report": str(evaluate_autoround_attack(config, config_path))}))
    elif args.command == "gptq-attack-generate":
        from .gptq_attack import generate_gptq_attack

        print(json.dumps({"manifest": str(generate_gptq_attack(config, config_path))}))
    elif args.command == "gptq-attack-evaluate":
        from .gptq_attack import evaluate_gptq_attack

        print(json.dumps({"report": str(evaluate_gptq_attack(config, config_path))}))
    elif args.command == "awq-attack-generate":
        from .awq_attack import generate_awq_attack

        print(json.dumps({"manifest": str(generate_awq_attack(config, config_path))}))
    elif args.command == "awq-attack-evaluate":
        from .awq_attack import evaluate_awq_attack

        print(json.dumps({"report": str(evaluate_awq_attack(config, config_path))}))


if __name__ == "__main__":
    main()
