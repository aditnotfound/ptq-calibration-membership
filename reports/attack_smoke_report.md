# CalibTrace single-artifact attack report

Evaluation uses 4 shadow artifacts, 2 completely held-out artifacts, and 4 candidate records at W4/N=128.

| Feature | AUROC | TPR@1% FPR | TPR@0.1% FPR |
|---|---:|---:|---:|
| artifact_reconstruction | 0.9375 | 0.7500 | 0.7500 |
| output_logit_mse | 1.0000 | 1.0000 | 1.0000 |
| output_kl | 0.2500 | 0.0000 | 0.0000 |
| output_true_logprob | 0.4375 | 0.0000 | 0.0000 |

Artifact minus output-logit-MSE AUROC: -0.0625.

Full crossed target/artifact bootstrap intervals and metadata:

```json
{
  "artifact_minus_output_logit_mse_auroc": -0.0625,
  "cluster_bootstrap": {
    "artifact_minus_output_logit_mse_auroc": {
      "lower_95": -0.7,
      "upper_95": 0.0
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.30000000000000004,
        "upper_95": 1.0
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.2,
        "upper_95": 1.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.2,
        "upper_95": 1.0
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.0,
        "upper_95": 0.6
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
        "lower_95": 1.0,
        "upper_95": 1.0
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 1.0,
        "upper_95": 1.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 1.0,
        "upper_95": 1.0
      }
    },
    "output_true_logprob": {
      "auroc": {
        "lower_95": 0.0,
        "upper_95": 0.8999999999999999
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.7999999999999998
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.7999999999999998
      }
    }
  },
  "metrics": {
    "artifact_reconstruction": {
      "auroc": 0.9375,
      "tpr_at_0_1pct_fpr": 0.75,
      "tpr_at_1pct_fpr": 0.75
    },
    "output_kl": {
      "auroc": 0.25,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logit_mse": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_true_logprob": {
      "auroc": 0.4375,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    }
  },
  "shadow_artifacts": 4,
  "targets": 4,
  "test_artifacts": 2,
  "test_decisions": 8,
  "test_members": 4,
  "test_nonmembers": 4,
  "threat_model": "public base, known quantizer, one held-out released artifact"
}
```
