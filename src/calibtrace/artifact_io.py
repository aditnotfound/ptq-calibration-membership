from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .quantization import Artifact, QuantizedTensor, signed_range


def _pack_nibbles(codes: np.ndarray, qmin: int) -> tuple[np.ndarray, int]:
    values = (codes.reshape(-1).astype(np.int16) - qmin).astype(np.uint8)
    length = len(values)
    if length % 2:
        values = np.pad(values, (0, 1))
    packed = values[0::2] | (values[1::2] << 4)
    return packed, length


def _unpack_nibbles(packed: np.ndarray, length: int, qmin: int) -> np.ndarray:
    values = np.empty(len(packed) * 2, dtype=np.int8)
    values[0::2] = (packed & 0x0F).astype(np.int8)
    values[1::2] = ((packed >> 4) & 0x0F).astype(np.int8)
    return values[:length] + np.int8(qmin)


def save_artifact(
    artifact: Artifact,
    path: str | Path,
    *,
    bits: int,
    metadata: dict[str, Any],
) -> str:
    if bits != 4:
        raise ValueError("Packed artifact serialization currently supports W4 only")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    qmin, _ = signed_range(bits)
    arrays: dict[str, np.ndarray] = {}
    layers: list[dict[str, Any]] = []
    for position, (name, tensor) in enumerate(artifact.items()):
        code_key = f"codes_{position:03d}"
        scale_key = f"scales_{position:03d}"
        packed, length = _pack_nibbles(tensor.codes.numpy(), qmin)
        arrays[code_key] = packed
        arrays[scale_key] = tensor.scales.numpy().astype(np.float32, copy=False)
        layers.append(
            {
                "name": name,
                "shape": list(tensor.shape),
                "length": length,
                "code_key": code_key,
                "scale_key": scale_key,
            }
        )
    header = {"format": "calibtrace-w4-v1", "bits": bits, "layers": layers, **metadata}
    arrays["header"] = np.asarray(json.dumps(header, sort_keys=True))
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    temporary.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def load_artifact(path: str | Path) -> tuple[Artifact, dict[str, Any]]:
    path = Path(path)
    artifact: Artifact = OrderedDict()
    with np.load(path, allow_pickle=False) as payload:
        header = json.loads(str(payload["header"]))
        if header["format"] != "calibtrace-w4-v1":
            raise ValueError(f"Unknown artifact format: {header['format']}")
        qmin, _ = signed_range(int(header["bits"]))
        for layer in header["layers"]:
            shape = tuple(layer["shape"])
            codes = _unpack_nibbles(
                payload[layer["code_key"]], int(layer["length"]), qmin
            ).reshape(shape[0], -1)
            scales = payload[layer["scale_key"]].copy()
            artifact[layer["name"]] = QuantizedTensor(
                torch.from_numpy(codes.copy()), torch.from_numpy(scales), shape
            )
    return artifact, header
