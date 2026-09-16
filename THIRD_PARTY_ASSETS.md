# Third-party assets and release boundaries

This audit covers the principal external models, datasets, metadata, and software used by
CalibTrace. It was checked against the linked upstream sources on August 24, 2026.

| Asset | Version or revision | License or terms | Compliance and release boundary |
|---|---|---|---|
| Meta OPT-125M | `27dcfa74d334bc871f3234de431e71c6eeba5dd6` | [OPT-175B License Agreement](https://huggingface.co/facebook/opt-125m/blob/27dcfa74d334bc871f3234de431e71c6eeba5dd6/LICENSE.md) | Noncommercial research use only. Do not bundle the checkpoint or quantized derivatives. Release configurations, hashes, scores, and regeneration instructions. |
| EleutherAI Pythia-410M | `9879c9b5f8bea9051dcb0e68dff21493d67e9d4f` | [Apache License 2.0](https://huggingface.co/EleutherAI/pythia-410m/blob/9879c9b5f8bea9051dcb0e68dff21493d67e9d4f/README.md) | Fetch weights from the upstream repository; do not bundle them in the supplement. |
| EleutherAI Pythia-1.4B | `fedc38a16eea3bd36a96b906d78d11d2ce18ed79` | [Apache License 2.0](https://huggingface.co/EleutherAI/pythia-1.4b/blob/fedc38a16eea3bd36a96b906d78d11d2ce18ed79/README.md) | Used for the larger-model replication. Fetch weights upstream; do not bundle them in the supplement. |
| CIFAR-100 Python archive | MD5 `eb9058c3a382ffc7106e4002c42a8d85` | [Official download page and citation request](https://www.cs.toronto.edu/~kriz/cifar.html); no named license is stated | Use locally for research and cite the creators. Do not redistribute the archive or images. Release split indices, hashes, and download instructions. |
| arXiv API metadata | 2024 cs.LG query | [CC0 1.0 metadata and API Terms of Use](https://info.arxiv.org/help/api/tou.html) | The terms explicitly include titles and abstracts within descriptive metadata. Respect the one-request-per-three-seconds limit. Do not redistribute e-print PDFs or sources. |
| Stack Exchange question corpus | 2025 questions from Cross Validated, Artificial Intelligence, Data Science, and Stack Overflow | [CC BY-SA 4.0](https://stackoverflow.com/help/licensing); [API documentation](https://api.stackexchange.com/docs/questions) | Each JSONL row retains the canonical question URL, title, creation time, author display name, source site, and license. Redistributed text must preserve attribution and share-alike terms. |
| LLM Compressor | 0.13.0 | [Apache License 2.0](https://github.com/vllm-project/llm-compressor/blob/main/LICENSE) | Used for the named GPTQ and AWQ implementations; upstream source is not vendored. |
| AutoRound | 0.14.2 | [Apache License 2.0](https://github.com/intel/auto-round/blob/main/LICENSE) | Installed as a dependency; upstream source is not vendored. |
| Hugging Face Transformers | 5.14.1 | [Apache License 2.0](https://github.com/huggingface/transformers/blob/v5.14.1/LICENSE) | Installed as a dependency; upstream source is not vendored. |
| PyTorch | 2.13.0+cu130 | [Upstream license and bundled notices](https://github.com/pytorch/pytorch/blob/main/LICENSE) | Installed as a dependency; retain the license files shipped with any redistributed environment. |
| NumPy; scikit-learn; PyArrow; Pillow; PyYAML; Matplotlib | 2.4.6; 1.9.0; 24.0.0; 12.2.0; 6.0.3; 3.10.9 | BSD-3-Clause expression and bundled notices; BSD-3-Clause; Apache-2.0; MIT-CMU; MIT; Matplotlib license | Installed as unmodified dependencies. Exact versions are recorded in the paper and environment metadata. |

The CIFAR-100 archive and model caches are already excluded by `.gitignore`. Before making a
supplementary archive, verify that it does not contain `data/cifar-100-python.tar.gz`, OPT weights,
Pythia weights, or generated quantized model weights.
