from __future__ import annotations

import json
import os
import time

import torch
from auto_round import AutoRound
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    seed = 20260827
    torch.manual_seed(seed)
    model_name = "facebook/opt-125m"
    if not os.environ.get("HF_HOME"):
        raise RuntimeError("Set HF_HOME to the project-local Hugging Face cache")
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        local_files_only=True,
        dtype=torch.float16,
        attn_implementation="eager",
    ).eval()
    generator = torch.Generator().manual_seed(seed + 1)
    examples = [
        {
            "input_ids": torch.randint(
                3, model.config.vocab_size, (64,), generator=generator
            ),
            "attention_mask": torch.ones(64, dtype=torch.long),
        }
        for _ in range(8)
    ]
    loader = DataLoader(examples, batch_size=2, shuffle=False)
    started = time.perf_counter()
    compressor = AutoRound(
        model,
        tokenizer=tokenizer,
        scheme="W4A16",
        dataset=loader,
        iters=2,
        seqlen=64,
        nsamples=8,
        batch_size=2,
        device_map=0,
        enable_torch_compile=False,
        enable_deterministic_algorithms=True,
        seed=seed,
        low_cpu_mem_usage=False,
    )
    quantized_model, layer_config = compressor.quantize()
    quantized_layers = [
        name
        for name, settings in layer_config.items()
        if isinstance(settings, dict) and int(settings.get("bits", 16)) < 16
    ]
    print(
        json.dumps(
            {
                "auto_round_version": __import__("auto_round").__version__,
                "model": model_name,
                "parameters": sum(parameter.numel() for parameter in quantized_model.parameters()),
                "quantized_layers": len(quantized_layers),
                "seconds": time.perf_counter() - started,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
