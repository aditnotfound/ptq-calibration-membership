from __future__ import annotations

import json

import torch
from auto_round import AutoRound
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from torch.utils.data import DataLoader
from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast


def main() -> None:
    torch.manual_seed(20260823)
    config = GPT2Config(
        vocab_size=256,
        n_positions=64,
        n_embd=64,
        n_layer=2,
        n_head=2,
        bos_token_id=1,
        eos_token_id=2,
    )
    model = GPT2LMHeadModel(config).eval()
    vocabulary = {"<pad>": 0, "<bos>": 1, "<eos>": 2}
    vocabulary.update({f"token_{index}": index for index in range(3, 256)})
    tokenizer_backend = Tokenizer(WordLevel(vocabulary, unk_token="<pad>"))
    tokenizer_backend.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_backend,
        bos_token="<bos>",
        eos_token="<eos>",
        pad_token="<pad>",
        model_max_length=64,
    )
    generator = torch.Generator().manual_seed(20260824)
    examples = [
        {
            "input_ids": torch.randint(3, 256, (32,), generator=generator),
            "attention_mask": torch.ones(32, dtype=torch.long),
        }
        for _ in range(4)
    ]
    loader = DataLoader(examples, batch_size=2, shuffle=False)
    compressor = AutoRound(
        model,
        tokenizer=tokenizer,
        scheme="W4A16",
        dataset=loader,
        iters=2,
        seqlen=32,
        nsamples=4,
        batch_size=2,
        device_map=0,
        enable_torch_compile=False,
        seed=20260825,
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
                "cuda": torch.cuda.is_available(),
                "model_class": type(quantized_model).__name__,
                "quantized_layers": len(quantized_layers),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
