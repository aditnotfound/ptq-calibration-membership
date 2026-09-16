from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"Expected a mapping in {config_path}")
    return config


def apply_overrides(config: dict[str, Any], overrides: list[str]) -> dict[str, Any]:
    result = deepcopy(config)
    for override in overrides:
        if "=" not in override:
            raise ValueError(f"Override must have the form key=value: {override!r}")
        dotted_key, raw_value = override.split("=", 1)
        value = yaml.safe_load(raw_value)
        cursor: dict[str, Any] = result
        keys = dotted_key.split(".")
        for key in keys[:-1]:
            child = cursor.get(key)
            if not isinstance(child, dict):
                child = {}
                cursor[key] = child
            cursor = child
        cursor[keys[-1]] = value
    return result


def resolve_path(config_path: str | Path, value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    # Configs live one directory below the project root by convention.
    return Path(config_path).resolve().parent.parent / path

