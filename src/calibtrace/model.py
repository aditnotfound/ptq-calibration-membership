from __future__ import annotations

from collections import OrderedDict

import torch
from torch import nn


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_channels: int, channels: int, stride: int = 1) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(
            in_channels, channels, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)
        if stride != 1 or in_channels != channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(channels),
            )
        else:
            self.shortcut = nn.Identity()

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(inputs)
        outputs = self.relu(self.bn1(self.conv1(inputs)))
        outputs = self.bn2(self.conv2(outputs))
        return self.relu(outputs + residual)


class CIFARResNet18(nn.Module):
    def __init__(self, num_classes: int = 100) -> None:
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(64, blocks=2, stride=1)
        self.layer2 = self._make_layer(128, blocks=2, stride=2)
        self.layer3 = self._make_layer(256, blocks=2, stride=2)
        self.layer4 = self._make_layer(512, blocks=2, stride=2)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
        self._initialize()

    def _make_layer(self, channels: int, blocks: int, stride: int) -> nn.Sequential:
        layers = [BasicBlock(self.in_channels, channels, stride)]
        self.in_channels = channels
        layers.extend(BasicBlock(self.in_channels, channels) for _ in range(1, blocks))
        return nn.Sequential(*layers)

    def _initialize(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        outputs = self.relu(self.bn1(self.conv1(inputs)))
        outputs = self.layer1(outputs)
        outputs = self.layer2(outputs)
        outputs = self.layer3(outputs)
        outputs = self.layer4(outputs)
        outputs = self.pool(outputs).flatten(1)
        return self.fc(outputs)


def quantizable_modules(model: nn.Module, include_linear: bool = True) -> OrderedDict[str, nn.Module]:
    types = (nn.Conv2d, nn.Linear) if include_linear else (nn.Conv2d,)
    return OrderedDict(
        (name, module) for name, module in model.named_modules() if isinstance(module, types)
    )

