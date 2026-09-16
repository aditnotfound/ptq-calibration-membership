# Reproduction guide

Run commands from the repository root. Python 3.11 or later is required. The original configurations and implementation have not been changed to accommodate a different machine or dataset.

## Environment

Use an isolated environment:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

For CPU checks, install CPU PyTorch followed by the base/test extras:

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[test]"
```

For quantization experiments, install the PyTorch build appropriate for your CUDA driver, then:

```bash
python -m pip install -e ".[gptq,autoround,paper,test]"
```

The supplement pins `llmcompressor==0.13.0`, `auto-round==0.14.2` and Transformers `>=5.14,<5.15`. Other dependencies have lower bounds, so this is not a fully locked environment. Check `pyproject.toml` and the historical environment notes in `THIRD_PARTY_ASSETS.md`; record the resolved versions for any new run. The import's CPU validation environment differs from the paper's GPU environment.

## Test status

```bash
# No dependencies beyond the Python standard library:
python tools/verify_repository.py

# Explicit CPU-compatible subset:
python -m pytest --ignore=tests/test_awq_attack.py --ignore=tests/test_manuscript.py

# Unchanged full suite, including tests with extra prerequisites:
python -m pytest
```

During this import the full original suite returned **25 passed, 2 failed, 1 skipped**:

- `test_awq_registered_recipe_rejects_nonstandard_shape_before_loading_model`: the function imports `llmcompressor` before validating its arguments; that optional library is absent from the CPU validation environment.
- `test_abstract_respects_style_contract`: requires `paper/sections/abstract.tex`, absent from the original ZIP. A different paper version was not substituted to make the test pass.
- The CUDA reconstruction test was skipped because the validation environment was CPU-only.

Tests and scientific implementation were not edited to hide those outcomes. The explicit subset is useful for basic development; it does not test named-library quantization, GPU behavior or manuscript files. GitHub Actions runs only the lightweight integrity checker.

## Model and data prerequisites

1. Inspect the chosen YAML. Each model revision, data path, output path and seed is part of the experiment definition.
2. Download the specified model/tokenizer revision into `artifacts/hf_cache` using upstream Hugging Face tooling. Accept/check applicable model terms yourself; no access token is stored here.
3. Supply the expected corpus snapshot. The original archive omitted both natural-text JSONL files and original population/score files. Corpus acquisition scripts exist, but new live downloads can differ from the old snapshots.
4. Keep the recorded compute dtype. In particular, the original documentation uses BF16 for Pythia-410M because FP16 produced nonfinite logits on the reported hardware.

The isolated runner sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. It will not fetch missing model files. An empty cache is a missing prerequisite, not a reason to silently load another checkpoint.

Optional corpus collection commands below make real external requests. Respect API terms, backoff and quotas; they were **not run** as part of this repository upload:

```bash
python scripts/fetch_arxiv_abstracts.py --output data/arxiv_cs_lg_2024.jsonl
python scripts/fetch_stackexchange_questions.py --output data/stackexchange_questions_2025.jsonl
```

## Example: GPTQ natural-text population

After satisfying the prerequisites:

```bash
python scripts/run_isolated_population.py --config configs/gptq_natural_postcutoff.yaml --method gptq
python -m calibtrace --config configs/gptq_natural_postcutoff.yaml gptq-attack-evaluate
```

The runner starts one quantization per child process and resumes from score rows. Use a separate working copy/output configuration for new experiments. Do not overwrite the supplied `reports/` and then claim the regenerated numbers are the archived paper evidence. A changed source snapshot or protocol constitutes a new experiment, even if the filename stays the same.

AWQ and AutoRound use the corresponding method and evaluation command:

```bash
python scripts/run_isolated_population.py --config configs/awq_natural_postcutoff.yaml --method awq
python -m calibtrace --config configs/awq_natural_postcutoff.yaml awq-attack-evaluate
python scripts/run_isolated_population.py --config configs/autoround_natural_postcutoff_iters50.yaml --method autoround
python -m calibtrace --config configs/autoround_natural_postcutoff_iters50.yaml autoround-attack-evaluate
```

## Vision pilot and paper assets

The CIFAR path requires downloading CIFAR-100 and training or restoring the fixed base checkpoint:

```bash
python -m calibtrace --config configs/pilot.yaml prepare
python -m calibtrace --config configs/pilot.yaml train
python -m calibtrace --config configs/pilot.yaml pilot
python -m calibtrace --config configs/pilot.yaml score
```

Its quantizer is deliberately called GPTQ-style, not a bit-exact deployment-library reproduction. See the historical README for its paired-swap design. Later attack stages have their own CLI commands.

`scripts/render_paper_assets.py` and the summary scripts expect their recorded reports/raw inputs. The manuscript and complete original raw results are not bundled. Figure generation, a successful unit test, and a full scientific reproduction are different checks.
