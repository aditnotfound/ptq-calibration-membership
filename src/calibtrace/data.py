from __future__ import annotations

import hashlib
import io
import json
import pickle
import shutil
import tarfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
import torch
import torch.nn.functional as F
import pyarrow.parquet as pq
from PIL import Image
from torch.utils.data import Dataset

CIFAR100_URL = "https://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz"
CIFAR100_MD5 = "eb9058c3a382ffc7106e4002c42a8d85"
CIFAR100_ARCHIVE = "cifar-100-python.tar.gz"
CIFAR100_FOLDER = "cifar-100-python"
HF_FOLDER = "cifar100-parquet"
HF_FILES = {
    "train": (
        "https://huggingface.co/datasets/uoft-cs/cifar100/resolve/main/"
        "cifar100/train-00000-of-00001.parquet?download=true",
        "694865d6b990e234804f01268586c41e88bcbbb75e20858432c05ad4081aca23",
    ),
    "test": (
        "https://huggingface.co/datasets/uoft-cs/cifar100/resolve/main/"
        "cifar100/test-00000-of-00001.parquet?download=true",
        "98776c529bb146a9c791229df74a5cf076be9b43d82dbbd334b6a7788d73dc68",
    ),
}
MEAN = torch.tensor((0.5071, 0.4867, 0.4408), dtype=torch.float32).view(3, 1, 1)
STD = torch.tensor((0.2675, 0.2565, 0.2761), dtype=torch.float32).view(3, 1, 1)


def _md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - required to verify the published dataset archive
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, path: Path, expected_digest: str, algorithm: str) -> None:
    partial = path.with_suffix(path.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "calibtrace/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as out:
            shutil.copyfileobj(response, out)
        actual = _md5(partial) if algorithm == "md5" else _sha256(partial)
        if actual != expected_digest:
            raise RuntimeError(
                f"Digest mismatch for {path.name}: expected {expected_digest}, received {actual}"
            )
        partial.replace(path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def _safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    root = destination.resolve()
    for member in archive.getmembers():
        target = (destination / member.name).resolve()
        if target != root and root not in target.parents:
            raise RuntimeError(f"Unsafe path in CIFAR archive: {member.name}")
    archive.extractall(destination, filter="data")


def prepare_cifar100(root: str | Path) -> Path:
    root = Path(root)
    extracted = root / CIFAR100_FOLDER
    if (extracted / "train").is_file() and (extracted / "test").is_file():
        return extracted

    root.mkdir(parents=True, exist_ok=True)
    parquet_root = root / HF_FOLDER
    parquet_paths = {split: parquet_root / f"{split}.parquet" for split in HF_FILES}
    if all(
        path.is_file() and _sha256(path) == HF_FILES[split][1]
        for split, path in parquet_paths.items()
    ):
        return parquet_root

    archive_path = root / CIFAR100_ARCHIVE
    try:
        if not archive_path.exists() or _md5(archive_path) != CIFAR100_MD5:
            _download(CIFAR100_URL, archive_path, CIFAR100_MD5, "md5")
        with tarfile.open(archive_path, "r:gz") as archive:
            _safe_extract(archive, root)
        return extracted
    except (OSError, RuntimeError, urllib.error.URLError):
        # The University of Toronto host is occasionally unavailable. The fallback is the
        # University of Toronto Computer Science dataset repository on Hugging Face, with
        # immutable SHA-256 checks from each Xet object.
        parquet_root.mkdir(parents=True, exist_ok=True)
        for split, (url, digest) in HF_FILES.items():
            path = parquet_paths[split]
            if not path.exists() or _sha256(path) != digest:
                _download(url, path, digest, "sha256")
        return parquet_root


def _load_batch(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("rb") as handle:
        payload = pickle.load(handle, encoding="bytes")  # noqa: S301 - official CIFAR archive
    images = payload[b"data"].reshape(-1, 3, 32, 32).astype(np.uint8, copy=False)
    labels = np.asarray(payload[b"fine_labels"], dtype=np.int64)
    return images, labels


def _load_parquet(path: Path) -> tuple[np.ndarray, np.ndarray]:
    table = pq.read_table(path, columns=["img", "fine_label"])
    labels = table["fine_label"].to_numpy(zero_copy_only=False).astype(np.int64, copy=False)
    image_rows = table["img"].to_pylist()
    images = np.empty((len(image_rows), 3, 32, 32), dtype=np.uint8)
    for position, row in enumerate(image_rows):
        if not isinstance(row, dict) or row.get("bytes") is None:
            raise RuntimeError(f"Unexpected image payload at row {position} in {path}")
        with Image.open(io.BytesIO(row["bytes"])) as image:
            array = np.asarray(image.convert("RGB"), dtype=np.uint8)
        images[position] = array.transpose(2, 0, 1)
    return images, labels


@dataclass(frozen=True)
class SplitManifest:
    train_indices: list[int]
    calibration_indices: list[int]
    split_seed: int
    train_per_class: int
    calibration_per_class: int

    def validate(self, labels: np.ndarray) -> None:
        train = set(self.train_indices)
        calibration = set(self.calibration_indices)
        if train & calibration:
            raise ValueError("Base-training and calibration indices overlap")
        if len(train) != len(self.train_indices) or len(calibration) != len(self.calibration_indices):
            raise ValueError("Duplicate indices in split manifest")
        for class_id in range(100):
            train_count = sum(int(labels[index]) == class_id for index in self.train_indices)
            calibration_count = sum(int(labels[index]) == class_id for index in self.calibration_indices)
            if train_count != self.train_per_class or calibration_count != self.calibration_per_class:
                raise ValueError(f"Incorrect class counts for class {class_id}")

    def to_json(self) -> dict[str, object]:
        body: dict[str, object] = {
            "dataset": "CIFAR-100",
            "source_split": "train",
            "split_seed": self.split_seed,
            "train_per_class": self.train_per_class,
            "calibration_per_class": self.calibration_per_class,
            "train_indices": self.train_indices,
            "calibration_indices": self.calibration_indices,
        }
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        body["sha256"] = hashlib.sha256(canonical).hexdigest()
        return body


def make_split_manifest(
    labels: np.ndarray,
    *,
    train_per_class: int,
    calibration_per_class: int,
    seed: int,
) -> SplitManifest:
    if train_per_class + calibration_per_class > 500:
        raise ValueError("CIFAR-100 has only 500 training examples per class")
    rng = np.random.default_rng(seed)
    train_indices: list[int] = []
    calibration_indices: list[int] = []
    for class_id in range(100):
        class_indices = np.flatnonzero(labels == class_id)
        shuffled = rng.permutation(class_indices)
        train_indices.extend(int(index) for index in shuffled[:train_per_class])
        start = train_per_class
        stop = start + calibration_per_class
        calibration_indices.extend(int(index) for index in shuffled[start:stop])
    manifest = SplitManifest(
        train_indices=sorted(train_indices),
        calibration_indices=sorted(calibration_indices),
        split_seed=seed,
        train_per_class=train_per_class,
        calibration_per_class=calibration_per_class,
    )
    manifest.validate(labels)
    return manifest


def write_manifest(manifest: SplitManifest, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(manifest.to_json(), handle, indent=2, sort_keys=True)
        handle.write("\n")


class CIFAR100Dataset(Dataset[tuple[torch.Tensor, int, int]]):
    def __init__(
        self,
        images: np.ndarray,
        labels: np.ndarray,
        indices: Sequence[int] | None = None,
        *,
        augment: bool = False,
    ) -> None:
        self.images = images
        self.labels = labels
        self.indices = np.arange(len(labels)) if indices is None else np.asarray(indices, dtype=np.int64)
        self.augment = augment

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, position: int) -> tuple[torch.Tensor, int, int]:
        source_index = int(self.indices[position])
        image = torch.from_numpy(self.images[source_index].copy()).float().div_(255.0)
        if self.augment:
            image = F.pad(image, (4, 4, 4, 4), mode="reflect")
            top = int(torch.randint(0, 9, ()).item())
            left = int(torch.randint(0, 9, ()).item())
            image = image[:, top : top + 32, left : left + 32]
            if bool(torch.rand(()) < 0.5):
                image = image.flip(-1)
        image = (image - MEAN) / STD
        return image, int(self.labels[source_index]), source_index


def load_datasets(
    root: str | Path,
    *,
    train_per_class: int,
    calibration_per_class: int,
    split_seed: int,
) -> tuple[CIFAR100Dataset, CIFAR100Dataset, CIFAR100Dataset, SplitManifest]:
    extracted = prepare_cifar100(root)
    if extracted.name == HF_FOLDER:
        train_images, train_labels = _load_parquet(extracted / "train.parquet")
        test_images, test_labels = _load_parquet(extracted / "test.parquet")
    else:
        train_images, train_labels = _load_batch(extracted / "train")
        test_images, test_labels = _load_batch(extracted / "test")
    manifest = make_split_manifest(
        train_labels,
        train_per_class=train_per_class,
        calibration_per_class=calibration_per_class,
        seed=split_seed,
    )
    train = CIFAR100Dataset(train_images, train_labels, manifest.train_indices, augment=True)
    calibration = CIFAR100Dataset(
        train_images, train_labels, manifest.calibration_indices, augment=False
    )
    evaluation = CIFAR100Dataset(test_images, test_labels, augment=False)
    return train, calibration, evaluation, manifest


def subset_by_source_indices(
    dataset: CIFAR100Dataset, source_indices: Sequence[int]
) -> CIFAR100Dataset:
    allowed = set(int(index) for index in dataset.indices)
    requested = [int(index) for index in source_indices]
    missing = set(requested) - allowed
    if missing:
        raise ValueError(f"Requested indices are outside the calibration pool: {sorted(missing)[:5]}")
    return CIFAR100Dataset(dataset.images, dataset.labels, requested, augment=False)
