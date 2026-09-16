# CalibTrace named-library attack report

Library `auto-round` 0.14.2 quantizes `facebook/opt-125m` to W4A16 from 4 shadow and 2 held-out calibration assignments of N=8 sequences of 128 tokens, tracking 4 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.5000 | 0.0000 | 0.0000 |
| output_logit_mse | 0.5000 | 0.0000 | 0.0000 |
| output_kl | 0.5000 | 0.0000 | 0.0000 |
| output_logprob | 0.5000 | 0.0000 | 0.0000 |
| output_logprob_gap | 0.5000 | 0.0000 | 0.0000 |

Artifact minus `output_logit_mse` AUROC: 0.0000 with crossed-bootstrap 95% interval [0.0000, 0.0000]. The baseline was selected on shadow artifacts only.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.0.fc1 | 0.5000 | 0.0000 |
| model.decoder.layers.0.fc2 | 0.5000 | 0.0000 |
| model.decoder.layers.0.self_attn.k_proj | 0.5000 | 0.0000 |
| model.decoder.layers.0.self_attn.out_proj | 0.5000 | 0.0000 |
| model.decoder.layers.0.self_attn.q_proj | 0.5000 | 0.0000 |
| model.decoder.layers.0.self_attn.v_proj | 0.5000 | 0.0000 |
| model.decoder.layers.1.fc1 | 0.5000 | 0.0000 |
| model.decoder.layers.1.fc2 | 0.5000 | 0.0000 |
| model.decoder.layers.1.self_attn.k_proj | 0.5000 | 0.0000 |
| model.decoder.layers.1.self_attn.out_proj | 0.5000 | 0.0000 |
| model.decoder.layers.1.self_attn.q_proj | 0.5000 | 0.0000 |
| model.decoder.layers.1.self_attn.v_proj | 0.5000 | 0.0000 |

Full metrics and metadata:

```json
{
  "artifact_minus_output_logit_mse_auroc": 0.0,
  "baseline_selection": "highest shadow-split AUROC among output-only features",
  "bits": 4,
  "calibration_size": 8,
  "cluster_bootstrap": {
    "artifact_minus_output_logit_mse_auroc": {
      "lower_95": 0.0,
      "upper_95": 0.0
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.5,
        "upper_95": 0.5
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.5,
        "upper_95": 0.5
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.5,
        "upper_95": 0.5
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.5,
        "upper_95": 0.5
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.5,
        "upper_95": 0.5
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      }
    }
  },
  "empirical_test_fpr_resolution": 0.25,
  "iters": 2,
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    }
  ],
  "library": "auto-round",
  "library_version": "0.14.2",
  "mean_changed_weight_fraction_vs_artifact0": 0.0,
  "metrics": {
    "artifact_reconstruction": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_kl": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logit_mse": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logprob": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logprob_gap": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    }
  },
  "model": "facebook/opt-125m",
  "parameters": 125239296,
  "per_target_auroc": {
    "artifact_reconstruction": {
      "lower_quartile": 0.5,
      "maximum": 0.5,
      "median": 0.5,
      "minimum": 0.5,
      "targets_above_chance": 0,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5
    },
    "output_kl": {
      "lower_quartile": 0.5,
      "maximum": 0.5,
      "median": 0.5,
      "minimum": 0.5,
      "targets_above_chance": 0,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5
    },
    "output_logit_mse": {
      "lower_quartile": 0.5,
      "maximum": 0.5,
      "median": 0.5,
      "minimum": 0.5,
      "targets_above_chance": 0,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5
    },
    "output_logprob": {
      "lower_quartile": 0.5,
      "maximum": 0.5,
      "median": 0.5,
      "minimum": 0.5,
      "targets_above_chance": 0,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5
    },
    "output_logprob_gap": {
      "lower_quartile": 0.5,
      "maximum": 0.5,
      "median": 0.5,
      "minimum": 0.5,
      "targets_above_chance": 0,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5
    }
  },
  "quantizer_seed": "fixed",
  "selected_output_baseline": "output_logit_mse",
  "sequence_length": 128,
  "shadow_artifacts": 4,
  "shadow_calibrated_operating_points": {
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 0,
        "shadow_false_positives": 0,
        "shadow_fpr": 0.0,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.0,
        "test_true_positives": 0,
        "threshold": 0.0
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 0,
        "shadow_false_positives": 0,
        "shadow_fpr": 0.0,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.0,
        "test_true_positives": 0,
        "threshold": 0.0
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 0,
        "shadow_false_positives": 0,
        "shadow_fpr": 0.0,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.0,
        "test_true_positives": 0,
        "threshold": 0.0
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 0,
        "shadow_false_positives": 0,
        "shadow_fpr": 0.0,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.0,
        "test_true_positives": 0,
        "threshold": 0.0
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 0,
        "shadow_false_positives": 0,
        "shadow_fpr": 0.0,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.0,
        "test_true_positives": 0,
        "threshold": 0.0
      }
    }
  },
  "shadow_metrics": {
    "artifact_reconstruction": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_kl": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logit_mse": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logprob": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logprob_gap": {
      "auroc": 0.5,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    }
  },
  "targets": 4,
  "test_artifacts": 2,
  "test_decisions": 8,
  "test_members": 4,
  "test_nonmembers": 4,
  "threat_model": "public base, released auto-round W4 artifact, one held-out artifact"
}
```
