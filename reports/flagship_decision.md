# CalibTrace flagship decision

Run date: 2026-08-23

## Decision

**GO.** The kill-first pilot has passed both gates: a single calibration-only record has a
deterministic causal effect on the stripped W4 artifact, and membership is recoverable from one
previously unseen artifact substantially better than from matched output-only scores.

The central phenomenon is now empirically verified for one CIFAR-100 ResNet-18 and the controlled
GPTQ-style quantizer in this repository. The result is strong enough to anchor a full paper. The
current evidence package is not yet broad enough to make a production-PTQ generalization claim;
a named-library replication and cross-model/method validation remain the main full-paper gates.

## Evidence chain

1. The full-precision base was trained on 40,000 records. All 10,000 possible calibration records
   were excluded from base training, and the official CIFAR-100 test split was used only for
   utility evaluation.
2. At W4/N=128, a class-matched one-record swap changed 15.625% of integer codes on average, while
   repeating an identical calibration changed zero codes. The mechanism-linked reconstruction
   score moved in the predicted direction in 47/48 comparisons.
3. The exploratory single-artifact population used 72 shadow and 24 held-out artifacts over 64
   candidates. Artifact AUROC was 0.9631 versus 0.9063 for the strongest one-query output baseline;
   the AUROC gap was 0.0568 with crossed-bootstrap 95% interval [0.0094, 0.0951].
4. A separate confirmation used a new seed, new candidates and backgrounds, and a randomized
   fixed-degree design. Every artifact contained exactly 32 of 64 tracked targets, and every target
   appeared in exactly half of each split. This removes total tracked-target count as a confound.

## Fixed-margin confirmation

The confirmation contains 1,536 held-out decisions: 768 members and 768 nonmembers.

| Feature | AUROC | Crossed-bootstrap 95% interval | ROC TPR at FPR <= 1% |
|---|---:|---:|---:|
| Artifact reconstruction | 0.9917 | [0.9829, 0.9977] | 0.8802 |
| Output logit MSE | 0.9130 | [0.8814, 0.9382] | 0.4010 |
| Output KL | 0.6038 | [0.5524, 0.6543] | 0.0169 |
| Output true-label log probability | 0.5413 | [0.4844, 0.5924] | 0.0026 |

Artifact minus output-logit-MSE AUROC is **0.0787**, with crossed-bootstrap 95% interval
**[0.0528, 0.1100]**. All 64 candidates have per-target AUROC above 0.5; 61/64 reach at least 0.9,
and the median per-target AUROC is 1.0.

Layerwise scoring localizes the effect to later representations. Each of the four `layer4`
convolutions reaches AUROC 1.0 alone, the four main `layer3` convolutions range from 0.9545 to
0.9800, and the input stem is at chance (0.4950). The fully connected layer reaches 0.9998. This
depth structure argues against leakage from a single explicit scale or metadata field and supplies
a concrete mechanism result for the paper.

Thresholds selected only from shadow nonmembers also transfer to the held-out population:

| Score | Shadow target | Held-out FPR | Held-out TPR | False positives / nonmembers |
|---|---:|---:|---:|---:|
| Artifact reconstruction | 1% | 0.91% | 87.76% | 7 / 768 |
| Output logit MSE | 1% | 1.43% | 46.22% | 11 / 768 |
| Artifact reconstruction | 0.1% | 0.13% | 70.18% | 1 / 768 |
| Output logit MSE | 0.1% | 0.13% | 25.65% | 1 / 768 |

The held-out FPR resolution is 1/768 = 0.130%. Consequently, the strict operating point is evidence
of threshold transfer with one observed false positive, not a statistically resolved estimate at
exactly 0.1% FPR. A much larger test population is required for a defensible 0.1% claim.

## What the result supports

Under a public-base, known-quantizer threat model, a record that never trained the base can become
membership-inferable because it was used for calibration. The information persists in the final
inference-complete quantized codes and scales after examples, activations, Hessians, observers,
record identifiers, labels, and calibration hashes are removed. The attack uses the public
full-precision base, the released W4 artifact, and the candidate record. Each membership decision
is candidate-local even though candidates are batched for efficient evaluation.

The causal paired experiment, independent held-out attack, fixed-margin confirmation, output
baselines, RTN negative control, and deterministic repeat collectively rule out the easiest
alternative explanations. The mechanism is also interpretable: calibration-sensitive rounding
reduces layerwise quantization residual energy along member activations.

## What remains unproven

- The implementation is GPTQ-style, not a bit-exact invocation of a named production PTQ library.
- Evidence currently comes from one trained base checkpoint, architecture, and dataset.
- The attack assumes the full-precision base is public; quantized-artifact-only access is untested.
- Calibration-size, bit-width, model-size, damping, and Hessian-sampling laws are not established.
- The experiment has no mitigation result and does not yet connect sample geometry to leakage;
  layerwise localization is complete for the confirmation checkpoint.
- Output-logit MSE is a matched one-query baseline, not an exhaustive multi-query or learned
  output-only attack.

## Full-paper readiness

The **finding** is full-paper caliber; the **current experimental breadth** is not yet comfortably
full-paper ready. For a workshop extended abstract, the controlled result is already unusually
complete. For an 8--12 page full paper, the most likely reviewer objection is that the effect might
be peculiar to this repository's quantizer or checkpoint.

The next experiments, in priority order, are:

1. Reproduce the attack with a named PTQ implementation and its native released checkpoint format.
2. Repeat across at least three independently trained base checkpoints and a second architecture or
   dataset.
3. Add a second calibration-sensitive mechanism and keep RTN/data-free quantization as negative
   controls.
4. Measure N and bit-width scaling, plus layerwise leakage localization.
5. Test artifact-only features without the public FP base and stronger multi-query output attacks.
6. Add one mechanism-targeted mitigation and quantify its privacy/utility trade-off.
7. Increase held-out nonmembers to at least 10,000 before making a resolved 0.1% FPR claim.

## Reproduction

From the project root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
python -m calibtrace --config configs/confirmation.yaml attack-generate
python -m calibtrace --config configs/confirmation.yaml attack-score
python -m calibtrace --config configs/confirmation.yaml attack-evaluate
```

The detailed confirmation metrics are in `reports/attack_n128_fixed_report.md` and its JSON sidecar.
The original causal measurements are in `reports/pilot_report.md`.
