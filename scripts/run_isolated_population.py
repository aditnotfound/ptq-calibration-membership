"""Complete a population with one quantization per child process."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


COMMANDS = {
    "gptq": ("gptq_attack", "gptq-attack-generate"),
    "autoround": ("autoround_attack", "autoround-attack-generate"),
    "awq": ("awq_attack", "awq-attack-generate"),
}


def _resolve(config_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else config_path.resolve().parent.parent / path


def _completed(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(bool(line.strip()) for line in handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--method", choices=tuple(COMMANDS), required=True)
    parser.add_argument("--hf-home", type=Path, default=Path("artifacts/hf_cache"))
    args = parser.parse_args()
    section, command = COMMANDS[args.method]
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    cfg = config[section]
    expected = int(cfg["shadow_artifacts"]) + int(cfg["test_artifacts"])
    scores_path = _resolve(args.config, cfg["scores"])
    environment = os.environ.copy()
    source = str(Path("src").resolve())
    environment["PYTHONPATH"] = (
        source
        if not environment.get("PYTHONPATH")
        else source + os.pathsep + environment["PYTHONPATH"]
    )
    environment["HF_HOME"] = str(args.hf_home.resolve())
    environment["HF_HUB_OFFLINE"] = "1"
    environment["TRANSFORMERS_OFFLINE"] = "1"
    environment["LLM_COMPRESSOR_LOG_LEVEL"] = "ERROR"
    environment["AR_LOG_LEVEL"] = "ERROR"
    environment["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    environment["TQDM_DISABLE"] = "1"
    while _completed(scores_path) < expected:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "calibtrace",
                "--config",
                str(args.config),
                command,
            ],
            env=environment,
            check=True,
        )
        print(
            json.dumps(
                {"completed": _completed(scores_path), "expected": expected}, sort_keys=True
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
