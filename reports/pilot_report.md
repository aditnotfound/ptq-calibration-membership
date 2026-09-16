# CalibTrace causal pilot report

Run date: 2026-08-22

## Outcome

The controlled causal pilot passes its mechanism-linked gate but does not yet establish deployable
single-artifact membership inference.

Replacing one calibration-only record changes a large number of final W4 integer codes. Repeating
the exact same calibration set yields byte-identical codes, and the resulting quantized models
retain essentially all base-model utility. Raw signed code deltas are not target-stable across
backgrounds. However, a candidate-specific score tied directly to the quantizer objective moves in
the predicted direction for 95 of 96 target/replacement comparisons.

## Registered setup

- Model: CIFAR ResNet-18 trained from scratch.
- Base-training records: 40,000, stratified as 400 per CIFAR-100 class.
- Calibration-only pool: 10,000, stratified as 100 per class and disjoint from base training.
- Utility evaluation: untouched official 10,000-record test split.
- Base checkpoint accuracy: 75.44%.
- Quantization: deterministic GPTQ-style Hessian-aware W4 weight quantization.
- Grid: fixed per-output-channel grid determined only by full-precision weights.
- Calibration labels and augmentation: unused.
- BatchNorm: frozen; no calibration-dependent running-statistic updates.
- Design per calibration size: 6 targets x 4 independent backgrounds = 24 matched swaps.
- Each nonmember calibration replaces the target with a class-matched record at fixed set size.

The data split manifest SHA-256 is
`ac086c6bd1f321709e56c329514f7094c1cd5ad4b40cdc6189c8fd5865f29ff5`.

## Results

| Measurement | N=32 | N=128 |
|---|---:|---:|
| Mean changed-code fraction | 7.245% | 15.625% |
| Repeat-same-set changed codes | 0 | 0 |
| First member artifact accuracy | 74.84% | 75.03% |
| First nonmember artifact accuracy | 74.84% | 74.75% |
| Reconstruction comparisons in predicted direction | 48/48 | 47/48 |
| Directional win rate | 100.0% | 97.9% |
| Mean directional score margin | 1.757e-4 | 8.048e-5 |
| Within-target signed-delta cosine | 0.00325 | 0.000325 |
| Between-target signed-delta cosine | -0.000003 | -0.000033 |
| Within-target flip-mask Jaccard | 0.21061 | 0.24201 |
| Between-target flip-mask Jaccard | 0.20975 | 0.24187 |

The calibration-free RTN checkpoint reaches 74.19% accuracy. All six target-level mean
reconstruction margins are positive at both calibration sizes.

## Interpretation

Three conclusions are supported:

1. A one-record calibration swap deterministically changes the final inference-complete integer
   codes while the full-precision weights and quantization grid are fixed.
2. The change is utility-preserving and is not explained by stochastic backend variation.
3. The artifact fits the record that actually calibrated it better under a candidate-specific local
   reconstruction score, including the predicted reversal for the replacement record.

The raw code-delta fingerprint hypothesis is not supported: repeated swaps involving the same
target are scarcely more aligned than swaps involving different targets. The mechanism-linked
reconstruction score is therefore the appropriate attack feature for the next stage.

The larger changed-code fraction at N=128 than at N=32 is not yet interpretable as a scaling law.
It may reflect calibration-Hessian rank, damping, and error-propagation dynamics. It requires an
ablation over patches per image, damping, and calibration size before scientific interpretation.

## What this does not prove

The reconstruction comparison sees both paired counterfactual artifacts. A deployment attacker
sees one released artifact. Consequently, these results establish causal sample influence, not yet
membership AUROC or low-FPR privacy risk.

The implementation reproduces the core GPTQ-style Hessian/error-compensation mechanism but is not
a bit-exact run of a named production GPTQ library. External-library replication remains necessary
for the full paper.

## Next gate

Generate a held-out population of single artifacts with balanced target inclusion. For each target,
estimate in/out distributions of its reconstruction score from shadow artifacts, then classify
membership in unseen artifacts without observing a paired counterpart. Split and bootstrap by
artifact and target. Compare against fixed-query output scores, the FP base, RTN, codes-only and
scales-only access, and report AUROC plus TPR at low FPR.

The flagship proceeds only if that single-artifact evaluation works at W4 and N=128.

