from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.optim import SGD
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

from .config import resolve_path
from .data import load_datasets, write_manifest
from .model import CIFARResNet18
from .repro import default_device, seed_everything


@torch.inference_mode()
def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> dict[str, float]:
    model.eval()
    total = 0
    correct = 0
    loss_sum = 0.0
    criterion = nn.CrossEntropyLoss(reduction="sum")
    for images, labels, _ in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        logits = model(images)
        loss_sum += float(criterion(logits, labels))
        correct += int((logits.argmax(1) == labels).sum())
        total += labels.numel()
    return {"loss": loss_sum / total, "accuracy": correct / total}


def train_base(config: dict[str, Any], config_path: str | Path) -> Path:
    seed = int(config["seed"])
    seed_everything(seed)
    device = default_device()
    paths = config["paths"]
    data_cfg = config["data"]
    train_cfg = config["train"]

    train_dataset, _, eval_dataset, manifest = load_datasets(
        resolve_path(config_path, paths["data_dir"]),
        train_per_class=int(data_cfg["train_per_class"]),
        calibration_per_class=int(data_cfg["calibration_per_class"]),
        split_seed=int(data_cfg["split_seed"]),
    )
    manifest_path = resolve_path(config_path, paths["split_manifest"])
    write_manifest(manifest, manifest_path)

    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        train_dataset,
        batch_size=int(train_cfg["batch_size"]),
        shuffle=True,
        num_workers=int(train_cfg["num_workers"]),
        pin_memory=device.type == "cuda",
        persistent_workers=int(train_cfg["num_workers"]) > 0,
        generator=generator,
    )
    eval_loader = DataLoader(
        eval_dataset,
        batch_size=int(train_cfg["eval_batch_size"]),
        shuffle=False,
        num_workers=int(train_cfg["num_workers"]),
        pin_memory=device.type == "cuda",
        persistent_workers=int(train_cfg["num_workers"]) > 0,
    )

    model = CIFARResNet18().to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=float(train_cfg["label_smoothing"]))
    optimizer = SGD(
        model.parameters(),
        lr=float(train_cfg["learning_rate"]),
        momentum=float(train_cfg["momentum"]),
        weight_decay=float(train_cfg["weight_decay"]),
    )
    epochs = int(train_cfg["epochs"])
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")

    checkpoint_path = resolve_path(config_path, paths["base_checkpoint"])
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = checkpoint_path.with_suffix(".train.jsonl")
    best_accuracy = -1.0
    for epoch in range(1, epochs + 1):
        started = time.perf_counter()
        model.train()
        seen = 0
        train_loss = 0.0
        train_correct = 0
        for images, labels, _ in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                logits = model(images)
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            seen += labels.numel()
            train_loss += float(loss.detach()) * labels.numel()
            train_correct += int((logits.detach().argmax(1) == labels).sum())
        scheduler.step()
        metrics = evaluate(model, eval_loader, device)
        record = {
            "epoch": epoch,
            "train_loss": train_loss / seen,
            "train_accuracy": train_correct / seen,
            "eval_loss": metrics["loss"],
            "eval_accuracy": metrics["accuracy"],
            "learning_rate": scheduler.get_last_lr()[0],
            "seconds": time.perf_counter() - started,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        print(json.dumps(record, sort_keys=True), flush=True)
        if metrics["accuracy"] > best_accuracy:
            best_accuracy = metrics["accuracy"]
            torch.save(
                {
                    "model": model.state_dict(),
                    "epoch": epoch,
                    "eval_accuracy": best_accuracy,
                    "seed": seed,
                    "split_manifest_sha256": manifest.to_json()["sha256"],
                },
                checkpoint_path,
            )
    return checkpoint_path


def load_base_model(path: str | Path, device: torch.device | None = None) -> CIFARResNet18:
    device = default_device() if device is None else device
    checkpoint = torch.load(Path(path), map_location="cpu", weights_only=True)
    model = CIFARResNet18()
    model.load_state_dict(checkpoint["model"])
    model.eval()
    return model.to(device)

