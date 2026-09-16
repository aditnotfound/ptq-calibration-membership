# CalibTrace

CalibTrace studies whether post-training quantization encodes membership information about records
that never trained the full-precision base model. The repository contains the causal pilot,
held-out artifact populations, named-library replications, statistical evaluation, and manuscript
asset generation.

The completed causal pilot is summarized in [`reports/pilot_report.md`](reports/pilot_report.md).
The held-out fixed-margin confirmation and full-paper go/no-go assessment are summarized in
[`reports/flagship_decision.md`](reports/flagship_decision.md).

The first experiment holds one CIFAR ResNet-18 checkpoint fixed and repeatedly applies a
deterministic, Hessian-aware W4 quantizer to calibration sets that differ in exactly one record.
It measures whether those swaps create reproducible changes in the integer weight codes.

## Causal design

The official CIFAR-100 training split is deterministically divided per class:

- 400 records per class (40,000 total) train the full-precision base model.
- 100 records per class (10,000 total) form a calibration-only pool.
- The untouched official test split measures utility.

For each target and background set, the pilot constructs equal-size calibrations

```text
S_in  = B union {target}
S_out = B union {class-matched replacement}
```

and quantizes the exact same base checkpoint. Calibration is unlabeled and unaugmented. BatchNorm
statistics are frozen. Weight grids and scales depend only on the full-precision weights, so the
only calibration-dependent stored values are the Hessian-informed integer codes. Round-to-nearest
(RTN) is serialized once as the calibration-free negative control.

The vision implementation is deliberately described as **GPTQ-style**, rather than a bit-exact
reproduction of a particular deployment library. It implements GPTQ's Hessian-informed sequential
error compensation on fixed per-output-channel W4 grids. Separate language-model experiments use
llm-compressor GPTQ and AWQ, together with AutoRound, directly.

## Environment

The project requires Python 3.11 or later and does not require `torchvision`. Install the complete
language-model, plotting, and test environment with:

```powershell
python -m pip install -e ".[gptq,autoround,paper,test]"
```

The reported environment uses llm-compressor 0.13.0, AutoRound 0.14.2, and Transformers 5.14.x.
Strengthened natural-text configurations pin full Hugging Face commit revisions and run with
offline model loading. OPT-125M runs use FP16 model compute. The pinned Pythia-410M checkpoint uses
BF16 because FP16 produces non-finite logits on the reported RTX 5070; compute dtype is part of the
hashed experiment contract, and score arrays are validated before serialization.

PowerShell commands from the project root:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
python -m calibtrace --config configs/pilot.yaml prepare
python -m calibtrace --config configs/pilot.yaml train
python -m calibtrace --config configs/pilot.yaml pilot
python -m calibtrace --config configs/pilot.yaml score
python -m calibtrace --config configs/pilot.yaml attack-generate
python -m calibtrace --config configs/pilot.yaml attack-score
python -m calibtrace --config configs/pilot.yaml attack-evaluate
python -m calibtrace --config configs/confirmation.yaml attack-generate
python -m calibtrace --config configs/confirmation.yaml attack-score
python -m calibtrace --config configs/confirmation.yaml attack-evaluate
```

Configuration values can be overridden without editing the registered pilot:

```powershell
python -m calibtrace --config configs/pilot.yaml `
  --set train.epochs=1 `
  --set paths.base_checkpoint=artifacts/smoke/base.pt `
  train

python -m calibtrace --config configs/pilot.yaml `
  --set quantization.calibration_sizes=[32] `
  --set quantization.targets=1 `
  --set quantization.backgrounds_per_target=1 `
  --set paths.base_checkpoint=artifacts/smoke/base.pt `
  --set paths.artifact_dir=artifacts/smoke `
  --set paths.result_dir=results/smoke `
  pilot
```

## Outputs

- `artifacts/base/cifar100_split_manifest.json`: immutable data-provenance manifest and digest.
- `artifacts/base/resnet18_cifar100.pt`: best full-precision checkpoint.
- `artifacts/pilot/rtn_w4.npz`: calibration-free negative-control artifact.
- `artifacts/pilot/n*/.../*.npz`: inference-complete packed W4 code/scale artifacts.
- `results/pilot_results.json`: global/layerwise code flips and within-target versus between-target
  fingerprint similarity, followed by candidate-specific reconstruction margins.

Each artifact contains only packed integer codes, necessary per-row scales, tensor shapes, and an
experiment manifest. It contains no examples, activations, Hessians, observers, optimizer state,
data paths, or labels.

## Pilot interpretation

This stage tests causal influence and fingerprint reproducibility. It does **not** by itself establish
a deployable membership attack, because the analysis observes paired counterfactual artifacts.

That gate has now passed. The single-artifact attack and an independent fixed-margin confirmation
show that W4/N=128 artifacts reveal calibration membership beyond matched output-only scores.
Named-library OPT-125M experiments now cover llm-compressor GPTQ and AWQ together with AutoRound.
Strengthened runs add exact shared-population comparisons, nonce-free exchangeable records, dated
natural text, candidate cross-fitting, calibration-size and bit-width sweeps, a Pythia-410M
replication, and zero-shot cross-quantizer transfer.

The completed attack follows this protocol:

1. Generate independent shadow artifacts with controlled target inclusion.
2. Fit candidate-conditioned in/out score distributions.
3. Evaluate membership from one held-out artifact at a time.
4. Compare against fixed-query output attacks and report cluster-aware uncertainty and low-FPR risk.

## Strengthened language-model experiments

Long populations are executed with one quantization per child process. Every row carries hashes of
the record pool, population, experiment contract, calibration indices, and quantized weights. Resume
logic rejects a stale row or a manifest produced by a different contract.

```powershell
$env:PYTHONPATH = "src"
python scripts/run_isolated_population.py --config configs/matched_gptq.yaml --method gptq
python -m calibtrace --config configs/matched_gptq.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/matched_autoround.yaml --method autoround
python -m calibtrace --config configs/matched_autoround.yaml autoround-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_homogeneous_no_nonce.yaml --method gptq
python -m calibtrace --config configs/gptq_homogeneous_no_nonce.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_natural_postcutoff.yaml --method gptq
python -m calibtrace --config configs/gptq_natural_postcutoff.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_natural_fresh1.yaml --method gptq
python -m calibtrace --config configs/gptq_natural_fresh1.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_natural_fresh2.yaml --method gptq
python -m calibtrace --config configs/gptq_natural_fresh2.yaml gptq-attack-evaluate
python scripts/verify_population_record_disjointness.py
python scripts/summarize_population_replications.py
python scripts/run_isolated_population.py --config configs/gptq_pythia410m_natural.yaml --method gptq
python -m calibtrace --config configs/gptq_pythia410m_natural.yaml gptq-attack-evaluate
python scripts/fetch_stackexchange_questions.py --output data/stackexchange_questions_2025.jsonl
python scripts/run_isolated_population.py --config configs/gptq_pythia1p4b_stackexchange.yaml --method gptq
python -m calibtrace --config configs/gptq_pythia1p4b_stackexchange.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/awq_natural_postcutoff.yaml --method awq
python -m calibtrace --config configs/awq_natural_postcutoff.yaml awq-attack-evaluate
python scripts/run_isolated_population.py --config configs/autoround_natural_postcutoff_iters0.yaml --method autoround
python scripts/run_isolated_population.py --config configs/autoround_natural_postcutoff_iters50.yaml --method autoround
python scripts/run_isolated_population.py --config configs/autoround_natural_postcutoff_iters200.yaml --method autoround
python -m calibtrace --config configs/autoround_natural_postcutoff_iters200.yaml autoround-attack-evaluate
python scripts/run_isolated_population.py --config configs/scale_gptq_n64_w4.yaml --method gptq
python -m calibtrace --config configs/scale_gptq_n64_w4.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/scale_gptq_n128_w4.yaml --method gptq
python -m calibtrace --config configs/scale_gptq_n128_w4.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/scale_gptq_n256_w4.yaml --method gptq
python -m calibtrace --config configs/scale_gptq_n256_w4.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/scale_gptq_n128_w8.yaml --method gptq
python -m calibtrace --config configs/scale_gptq_n128_w8.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_n256_damp01.yaml --method gptq
python -m calibtrace --config configs/gptq_n256_damp01.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_n256_damp1.yaml --method gptq
python -m calibtrace --config configs/gptq_n256_damp1.yaml gptq-attack-evaluate
python scripts/run_isolated_population.py --config configs/gptq_n256_independent.yaml --method gptq
python -m calibtrace --config configs/gptq_n256_independent.yaml gptq-attack-evaluate
python scripts/summarize_autoround_trajectory.py
python scripts/summarize_gptq_interventions.py
python scripts/summarize_elite_experiments.py
python scripts/evaluate_cross_quantizer_transfer.py
python scripts/evaluate_cross_quantizer_transfer.py --first-config configs/gptq_natural_postcutoff.yaml --second-config configs/awq_natural_postcutoff.yaml --second-section awq_attack --output reports/cross_quantizer_transfer_natural_awq.json
python scripts/render_paper_assets.py
```

The dated natural-text corpus is generated by `scripts/fetch_arxiv_abstracts.py`. Its path, SHA-256
digest, text field, record count, token packing procedure, and publication-date range are stored in
the population manifest.

The independent-domain replication uses `scripts/fetch_stackexchange_questions.py` to collect
attributed questions created in 2025. Code blocks are excluded from the text stream, while every
row retains its canonical URL, author display name, site, creation time, and CC BY-SA 4.0 license.
The Pythia-1.4B configuration records the source-file and packed-token SHA-256 digests and rejects
any record whose timestamp does not postdate the declared cutoff.
The two `gptq_natural_fresh*` configurations repeat the complete OPT-125M natural-text
construction with new record packing, candidates, references, backgrounds, fixed-margin matrices,
shadow artifacts, and test artifacts. The record-disjointness audit verifies zero exact tokenized
candidate or reference overlap. `scripts/summarize_population_replications.py` verifies that the
record-pool and population hashes are distinct before producing the replication table.
Natural-text configurations may set `record_row_published_after` to filter the source JSONL before
packing. The filtered document count, date range, cutoff, source-file hash, and packed-pool hash are
then recorded together in the population manifest.

## Licenses and data redistribution

Third-party checkpoints, datasets, metadata, and libraries remain governed by their original
licenses and terms. The supplementary release does not bundle model weights, quantized checkpoint
derivatives, or the CIFAR-100 archive. Exact revisions, upstream terms, acquisition instructions,
and redistribution boundaries are documented in [`THIRD_PARTY_ASSETS.md`](THIRD_PARTY_ASSETS.md).
