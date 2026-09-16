# Experiment map

All YAML files remain in `configs/`, preserving the code's existing path-resolution behavior. Report files are the historical summaries from the supplement, not newly produced results.

| Study | Configurations | Report entry points |
|---|---|---|
| CIFAR-100 pilot and artifact attack | `pilot.yaml`, `confirmation.yaml` | [pilot](../reports/pilot_report.md), [fixed N=128 attack](../reports/attack_n128_fixed_report.md) |
| GPTQ, dated natural text | `gptq_natural_postcutoff.yaml`, `gptq_natural_fresh1.yaml`, `gptq_natural_fresh2.yaml` | [main GPTQ](../reports/gptq_natural_postcutoff_report.md), [population replications](../reports/gptq_population_replications.md) |
| Larger/model-family replications | `gptq_pythia410m_natural.yaml`, `gptq_pythia1p4b_stackexchange.yaml` | [Pythia-410M](../reports/gptq_pythia410m_natural_report.md), [Pythia-1.4B](../reports/gptq_pythia1p4b_stackexchange_report.md) |
| AutoRound optimization | `autoround_natural_postcutoff_iters*.yaml`, `analysis_autoround_iters*.yaml` | [natural text, 50 steps](../reports/autoround_natural_postcutoff_iters50_report.md), [trajectory](../reports/autoround_optimization_trajectory.md) |
| AWQ | `awq_natural_postcutoff.yaml`, `awq_smoke.yaml` | [natural-text AWQ](../reports/awq_natural_postcutoff_report.md) |
| Matched populations and synthetic controls | `matched_gptq.yaml`, `matched_autoround.yaml`, `gptq_homogeneous*.yaml` | [matched GPTQ](../reports/matched_gptq_report.md), [nonce-free control](../reports/gptq_homogeneous_no_nonce_report.md) |
| Calibration size/precision | `scale_gptq_*.yaml` | [experiment summary](../reports/elite_experiment_summary.md) |
| Damping/background interventions | `gptq_n256_*.yaml` | [intervention frontier](../reports/gptq_intervention_frontier.md) |
| Cross-quantizer transfer | `scripts/evaluate_cross_quantizer_transfer.py` with matching configs | [transfer](../reports/cross_quantizer_transfer.md), [natural AWQ transfer](../reports/cross_quantizer_transfer_natural_awq.md) |

## Source map

- `data.py`, `model.py`, `train.py`: vision data, model and fixed-checkpoint training.
- `quantization.py`, `artifact_io.py`, `experiment.py`: GPTQ-style vision quantization, artifacts and paired pilot.
- `attack.py`, `scores.py`, `analysis.py`: vision attacks and statistical analysis.
- `gptq_attack.py`, `autoround_attack.py`, `awq_attack.py`: named-library language-model experiments and evaluation.
- `config.py`, `repro.py`, `cli.py`: configuration, experiment contracts and command routing.
- `scripts/`: corpus fetching, isolated population execution, replication/intervention summaries and figure generation.

The [original README](original_supplement_README.md) is retained verbatim as a historical document. Its relative links and commands assume the repository root, not `docs/`. Read its scientific conclusions alongside the supplied reports and current scope notes; it is not a validation performed during this import.
