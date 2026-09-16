# CalibTrace: PTQ calibration membership

Code and supplementary reports for **Calibration Data Leaves a Membership Trace: Leakage from Post-Training Quantization Artifacts**.

This project asks whether a released quantized model reveals whether a known candidate record was used for calibration, while the pretrained checkpoint stays fixed. The experiments cover GPTQ, AutoRound and AWQ on language models, plus a controlled CIFAR-100 experiment with a GPTQ-style quantizer.

**Status:** manuscript submitted to a NeurIPS 2026 workshop; not an acceptance or publication claim. This repository organizes the original author-supplied supplement. It does **not** contain the later disjoint-pool/frozen-threshold follow-up experiment.

## Start here

- [Reproduction guide](docs/reproduction.md): installation, CPU checks and GPU experiment prerequisites.
- [Experiment map](docs/experiments.md): configurations and corresponding reports.
- [What is included, and what is missing](docs/release_notes.md): provenance and limitations.
- [Verification record](reproducibility/import_validation.json): actual test outcomes for this import.
- [Third-party assets](THIRD_PARTY_ASSETS.md): model/data terms and redistribution boundaries.

## Repository layout

```text
src/calibtrace/       Experiment, quantization, attack and analysis implementations
configs/             29 original experiment/analysis configurations
scripts/             Original corpus, experiment and report-generation utilities
tests/               Original supplement tests, retained unchanged
reports/             78 supplied summary reports; not raw score files
docs/                Setup, experiment map and release notes
reproducibility/     Original-file fingerprints and import validation
tools/               Lightweight repository-integrity checker
.github/workflows/   Integrity checks; not a GPU reproduction job
```

## Quick checks

The integrity check needs only Python 3.11+ and does not download data or models:

```bash
python tools/verify_repository.py
```

For CPU tests, create a virtual environment, install a suitable CPU PyTorch build, then the project and test dependencies:

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[test]"
python -m calibtrace --help
python -m pytest --ignore=tests/test_awq_attack.py --ignore=tests/test_manuscript.py
```

Those two exclusions are explicit: the AWQ test imports the optional `llmcompressor` package, and the manuscript test needs `paper/sections/abstract.tex`, which was not supplied in the archive. The unchanged full suite was also run during packaging: **25 passed, 2 failed, 1 skipped**. The failures were those two missing prerequisites; the skipped test requires CUDA. See the [test notes](docs/reproduction.md#test-status). Do not interpret a green repository-integrity check as a fully passing scientific test suite.

## Research scope

The attack assumes a known candidate, the original base checkpoint, the quantized artifact, and appropriate quantizer/shadow access. It targets membership in the separate calibration set, not recovery of unknown text or generic pretraining-data membership. Candidate cross-fitting, matched output attacks, synthetic controls and calibration-free controls are part of the supplied evaluation.

The original summaries are preserved, not independently regenerated here. Raw `*_scores.jsonl`, population manifests, original corpus snapshots and model checkpoints were absent from the supplied ZIP. Fresh API downloads need not reproduce the original corpus hashes. Full report reproduction requires those exact inputs or clearly labelled new experiments.

## Attribution and use

Research/code supplied by Adit Patil. The import keeps all original source, tests and configurations byte-for-byte unchanged. Packaging additions and path-only report sanitation are documented separately in [release notes](docs/release_notes.md).

No open-source license was supplied or added. Repository visibility alone does not grant an open-source license. Third-party software, datasets and checkpoints retain their own terms; consult [THIRD_PARTY_ASSETS.md](THIRD_PARTY_ASSETS.md). No model weights, corpus text, credentials or cloud access files are included.

The repository was created private. Confirm the workshop's anonymity rules before making it public or linking an identifying repository in an anonymous submission.
