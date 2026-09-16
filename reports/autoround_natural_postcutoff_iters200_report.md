# CalibTrace named-library attack report

Library `auto-round` 0.14.2 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 32 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 64 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.5776 | 0.0137 | 0.0010 |
| artifact_layer_combination | 0.9499 | 0.4316 | 0.1582 |
| output_logit_mse | 1.0000 | 1.0000 | 1.0000 |
| output_kl | 1.0000 | 1.0000 | 1.0000 |
| output_logprob | 0.6581 | 0.0137 | 0.0049 |
| output_logprob_gap | 0.6581 | 0.0137 | 0.0049 |
| output_combination | 1.0000 | 1.0000 | 1.0000 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_logit_mse`: -0.0501 AUROC, crossed-bootstrap 95% interval [-0.0673, -0.0351]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 1024 calibration-excluded reference scores, mean token log probability changes by -0.010847; the corresponding perplexity ratio is 1.010906.

## Generation runtime

The 64 quantize-and-score jobs took 59.3 minutes in aggregate, with mean 55.6 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.9.fc2 | 0.7206 | 0.0801 |
| model.decoder.layers.8.fc2 | 0.6980 | 0.0762 |
| model.decoder.layers.5.fc2 | 0.6876 | 0.0625 |
| model.decoder.layers.6.fc2 | 0.6865 | 0.0488 |
| model.decoder.layers.7.fc2 | 0.6823 | 0.0703 |
| model.decoder.layers.10.fc2 | 0.6698 | 0.0264 |
| model.decoder.layers.9.self_attn.out_proj | 0.6625 | 0.0352 |
| model.decoder.layers.10.self_attn.out_proj | 0.6335 | 0.0332 |
| model.decoder.layers.9.fc1 | 0.6287 | 0.0312 |
| model.decoder.layers.10.fc1 | 0.6240 | 0.0371 |
| model.decoder.layers.9.self_attn.v_proj | 0.6066 | 0.0439 |
| model.decoder.layers.5.self_attn.v_proj | 0.5916 | 0.0332 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.5205 | 0.0127 |
| artifact_layer_combination | 0.5883 | 0.0283 |
| selected_artifact | 0.5883 | 0.0283 |
| selected_output | 0.9999 | 0.9990 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_logit_mse_auroc": -0.05014991760253906,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": -0.4115896224975586,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.5566052365033861,
          "upper_95": 0.625189157777867
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.003842274971609826,
          "upper_95": 0.04586297745052921
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.010416420293282876,
          "upper_95": 0.06883084265598041
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": -0.4433873207485224,
        "upper_95": -0.3746897404478729
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.4879486698481223,
          "upper_95": 0.5579472874817912
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.014593940670053391
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.00282807958864297,
          "upper_95": 0.031686317737141506
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.9997375788332183,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9782145674726835,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9875065546509967,
          "upper_95": 1.0
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.9991872357040843,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.823518766384817,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9824338237064503,
          "upper_95": 1.0
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.9906520135117093,
          "upper_95": 0.9995975537253451
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.7497497136722546,
          "upper_95": 0.9722798208392267
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.8199764196342637,
          "upper_95": 0.9881799376539409
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4743641720984597,
          "upper_95": 0.538005787164869
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.011756677658177282
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.039377890263717026
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.563139738612852,
          "upper_95": 0.6563827531319281
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.007978079859113493
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.020760044532785075
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.5566052365033861,
          "upper_95": 0.625189157777867
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.003842274971609826,
          "upper_95": 0.04586297745052921
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.010416420293282876,
          "upper_95": 0.06883084265598041
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.9997375788332183,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9782145674726835,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9875065546509967,
          "upper_95": 1.0
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.588343620300293,
        "tpr_at_0_1pct_fpr": 0.013671875,
        "tpr_at_1pct_fpr": 0.0283203125
      },
      "artifact_reconstruction": {
        "auroc": 0.5205421447753906,
        "tpr_at_0_1pct_fpr": 0.0009765625,
        "tpr_at_1pct_fpr": 0.0126953125
      },
      "output_combination": {
        "auroc": 0.9999332427978516,
        "tpr_at_0_1pct_fpr": 0.9921875,
        "tpr_at_1pct_fpr": 0.9990234375
      },
      "output_kl": {
        "auroc": 0.9998054504394531,
        "tpr_at_0_1pct_fpr": 0.9755859375,
        "tpr_at_1pct_fpr": 1.0
      },
      "output_logit_mse": {
        "auroc": 0.9959249496459961,
        "tpr_at_0_1pct_fpr": 0.82421875,
        "tpr_at_1pct_fpr": 0.9248046875
      },
      "output_logprob": {
        "auroc": 0.506598949432373,
        "tpr_at_0_1pct_fpr": 0.0009765625,
        "tpr_at_1pct_fpr": 0.015625
      },
      "output_logprob_gap": {
        "auroc": 0.6095900535583496,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.005859375
      },
      "selected_artifact": {
        "auroc": 0.588343620300293,
        "tpr_at_0_1pct_fpr": 0.013671875,
        "tpr_at_1pct_fpr": 0.0283203125
      },
      "selected_output": {
        "auroc": 0.9999332427978516,
        "tpr_at_0_1pct_fpr": 0.9921875,
        "tpr_at_1pct_fpr": 0.9990234375
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20260923,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          31,
          50,
          7,
          53,
          16,
          34,
          13,
          19,
          44,
          17,
          57,
          59,
          14,
          0,
          33,
          3,
          56,
          15,
          32,
          35,
          28,
          37,
          48,
          42,
          58,
          26,
          25,
          18,
          24,
          21,
          36,
          61
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 0.7703445747800587,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.9999770894428153,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
        "training_candidates": [
          1,
          2,
          4,
          5,
          6,
          8,
          9,
          10,
          11,
          12,
          20,
          22,
          23,
          27,
          29,
          30,
          38,
          39,
          40,
          41,
          43,
          45,
          46,
          47,
          49,
          51,
          52,
          54,
          55,
          60,
          62,
          63
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          46,
          29,
          51,
          49,
          6,
          5,
          2,
          54,
          23,
          10,
          30,
          1,
          55,
          62,
          43,
          47,
          38,
          12,
          27,
          11,
          63,
          45,
          4,
          22,
          41,
          40,
          60,
          9,
          8,
          39,
          20,
          52
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 0.6997800586510264,
        "output_regularization": 1.0,
        "output_validation_auroc": 1.0,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
        "training_candidates": [
          0,
          3,
          7,
          13,
          14,
          15,
          16,
          17,
          18,
          19,
          21,
          24,
          25,
          26,
          28,
          31,
          32,
          33,
          34,
          35,
          36,
          37,
          42,
          44,
          48,
          50,
          53,
          56,
          57,
          58,
          59,
          61
        ]
      }
    ]
  },
  "cluster_bootstrap": {
    "artifact_layer_combination": {
      "auroc": {
        "lower_95": 0.9326701426344046,
        "upper_95": 0.964881235950385
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0794873780087878,
        "upper_95": 0.3640999943001539
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.15632770931546883,
        "upper_95": 0.6805194209990721
      }
    },
    "artifact_minus_output_logit_mse_auroc": {
      "lower_95": -0.06732985736559541,
      "upper_95": -0.03511876404961506
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.5305845120259566,
        "upper_95": 0.6290524846035391
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.01564065629465541
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.03893045606529825
      }
    },
    "output_combination": {
      "auroc": {
        "lower_95": 0.9999999999999999,
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
    "output_kl": {
      "auroc": {
        "lower_95": 0.9999999999999999,
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
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.9999999999999999,
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
    "output_logprob": {
      "auroc": {
        "lower_95": 0.6100189009095598,
        "upper_95": 0.7049129297007891
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.019439674108390908
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0019434464423302164,
        "upper_95": 0.05679566955467005
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.6100189009095598,
        "upper_95": 0.7049129297007891
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.019439674108390908
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0019434464423302164,
        "upper_95": 0.05679566955467005
      }
    }
  },
  "empirical_test_fpr_resolution": 0.0009765625,
  "experiment_sha256": "e39dd3d5532db9d8fd11623e21a4aa186260d6cdf0eace023126262553516a61",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.47576141357421875,
    "null_mean": 0.49997708320617673,
    "null_upper_95": 0.5246374130249023,
    "observed_auroc": 0.9498500823974609,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 64,
    "maximum_seconds": 72.42041899997275,
    "mean_seconds_per_artifact": 55.63698117030981,
    "minimum_seconds": 33.548192300018854,
    "total_seconds": 3560.766794899828
  },
  "iters": 200,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.08929248546550188,
      "model.decoder.layers.0.fc2": 0.03372518651641671,
      "model.decoder.layers.0.self_attn.k_proj": 0.05738953582931552,
      "model.decoder.layers.0.self_attn.out_proj": 0.02922932278086033,
      "model.decoder.layers.0.self_attn.q_proj": 0.049873754981224434,
      "model.decoder.layers.0.self_attn.v_proj": 0.04435777418644654,
      "model.decoder.layers.1.fc1": 0.005661437112784092,
      "model.decoder.layers.1.fc2": 0.04506614174443992,
      "model.decoder.layers.1.self_attn.k_proj": -0.0035287777983598408,
      "model.decoder.layers.1.self_attn.out_proj": -0.005626572695744009,
      "model.decoder.layers.1.self_attn.q_proj": -0.004916767199687815,
      "model.decoder.layers.1.self_attn.v_proj": 0.02678215641574187,
      "model.decoder.layers.10.fc1": 0.11321431847392568,
      "model.decoder.layers.10.fc2": 0.12775534626534846,
      "model.decoder.layers.10.self_attn.k_proj": -0.007570543977564117,
      "model.decoder.layers.10.self_attn.out_proj": 0.11124332518450704,
      "model.decoder.layers.10.self_attn.q_proj": 0.032293991882436854,
      "model.decoder.layers.10.self_attn.v_proj": 0.09590128724384683,
      "model.decoder.layers.11.fc1": 0.09409189287284535,
      "model.decoder.layers.11.fc2": 0.06509678982157145,
      "model.decoder.layers.11.self_attn.k_proj": 0.009971717940540472,
      "model.decoder.layers.11.self_attn.out_proj": 0.08843205751508627,
      "model.decoder.layers.11.self_attn.q_proj": 0.015629101399859683,
      "model.decoder.layers.11.self_attn.v_proj": 0.06573616672111528,
      "model.decoder.layers.2.fc1": -0.009586280217692741,
      "model.decoder.layers.2.fc2": 0.036998333528613016,
      "model.decoder.layers.2.self_attn.k_proj": 0.02099689086454005,
      "model.decoder.layers.2.self_attn.out_proj": 0.02372359611011106,
      "model.decoder.layers.2.self_attn.q_proj": 0.011078608810586433,
      "model.decoder.layers.2.self_attn.v_proj": 0.052326531746597515,
      "model.decoder.layers.3.fc1": -0.01204531093611604,
      "model.decoder.layers.3.fc2": 0.02086821782609616,
      "model.decoder.layers.3.self_attn.k_proj": 0.004067317177723508,
      "model.decoder.layers.3.self_attn.out_proj": 0.0067926808517695045,
      "model.decoder.layers.3.self_attn.q_proj": 0.017076055835074103,
      "model.decoder.layers.3.self_attn.v_proj": 0.07362737358861611,
      "model.decoder.layers.4.fc1": 0.0011232780142665874,
      "model.decoder.layers.4.fc2": 0.08488542773107118,
      "model.decoder.layers.4.self_attn.k_proj": 0.01902663177963867,
      "model.decoder.layers.4.self_attn.out_proj": 0.05790823958966093,
      "model.decoder.layers.4.self_attn.q_proj": 0.0166215557249563,
      "model.decoder.layers.4.self_attn.v_proj": 0.07510861033725055,
      "model.decoder.layers.5.fc1": 0.05693824771067367,
      "model.decoder.layers.5.fc2": 0.1695039148416416,
      "model.decoder.layers.5.self_attn.k_proj": 0.02485420186745555,
      "model.decoder.layers.5.self_attn.out_proj": 0.044546773753624626,
      "model.decoder.layers.5.self_attn.q_proj": 0.009858409584482536,
      "model.decoder.layers.5.self_attn.v_proj": 0.08234696748104853,
      "model.decoder.layers.6.fc1": 0.047496145952127485,
      "model.decoder.layers.6.fc2": 0.16416587474568808,
      "model.decoder.layers.6.self_attn.k_proj": 0.0021107262269357678,
      "model.decoder.layers.6.self_attn.out_proj": 0.046791749738599855,
      "model.decoder.layers.6.self_attn.q_proj": 0.0066137905087815,
      "model.decoder.layers.6.self_attn.v_proj": 0.05228147537567074,
      "model.decoder.layers.7.fc1": 0.09457951388558142,
      "model.decoder.layers.7.fc2": 0.1486515240863612,
      "model.decoder.layers.7.self_attn.k_proj": -0.006509531969569562,
      "model.decoder.layers.7.self_attn.out_proj": 0.053404966831879806,
      "model.decoder.layers.7.self_attn.q_proj": 0.021030199636772173,
      "model.decoder.layers.7.self_attn.v_proj": 0.0558697259062479,
      "model.decoder.layers.8.fc1": 0.0680763847517581,
      "model.decoder.layers.8.fc2": 0.16818606145820073,
      "model.decoder.layers.8.self_attn.k_proj": 0.03061333485084663,
      "model.decoder.layers.8.self_attn.out_proj": 0.051515483444363075,
      "model.decoder.layers.8.self_attn.q_proj": 0.02193221365523902,
      "model.decoder.layers.8.self_attn.v_proj": 0.07406153293350651,
      "model.decoder.layers.9.fc1": 0.09572138567280608,
      "model.decoder.layers.9.fc2": 0.16891555505010042,
      "model.decoder.layers.9.self_attn.k_proj": 0.0029388172207681215,
      "model.decoder.layers.9.self_attn.out_proj": 0.142091672628031,
      "model.decoder.layers.9.self_attn.q_proj": 0.03161861998278415,
      "model.decoder.layers.9.self_attn.v_proj": 0.08328089363410165
    },
    "regularization": 0.001,
    "shadow_split_auroc": 0.9485511779785156
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 0.7205820083618164,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 0.02734375,
      "tpr_at_1pct_fpr": 0.080078125
    },
    {
      "auroc": 0.6979598999023438,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 0.0224609375,
      "tpr_at_1pct_fpr": 0.076171875
    },
    {
      "auroc": 0.6875886917114258,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 0.021484375,
      "tpr_at_1pct_fpr": 0.0625
    },
    {
      "auroc": 0.6865158081054688,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.048828125
    },
    {
      "auroc": 0.6822996139526367,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 0.021484375,
      "tpr_at_1pct_fpr": 0.0703125
    },
    {
      "auroc": 0.6697721481323242,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0263671875
    },
    {
      "auroc": 0.6625490188598633,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.6334657669067383,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0146484375,
      "tpr_at_1pct_fpr": 0.033203125
    },
    {
      "auroc": 0.6286735534667969,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.0107421875,
      "tpr_at_1pct_fpr": 0.03125
    },
    {
      "auroc": 0.6239748001098633,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.0068359375,
      "tpr_at_1pct_fpr": 0.037109375
    },
    {
      "auroc": 0.6066169738769531,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0439453125
    },
    {
      "auroc": 0.5916109085083008,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.033203125
    },
    {
      "auroc": 0.5909261703491211,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0244140625
    },
    {
      "auroc": 0.5898666381835938,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 0.0146484375,
      "tpr_at_1pct_fpr": 0.041015625
    },
    {
      "auroc": 0.5835952758789062,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.0205078125
    },
    {
      "auroc": 0.5808544158935547,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0263671875
    },
    {
      "auroc": 0.5777578353881836,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.5726938247680664,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.0244140625
    },
    {
      "auroc": 0.5722684860229492,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.5709848403930664,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0185546875
    },
    {
      "auroc": 0.5650110244750977,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5629749298095703,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0224609375
    },
    {
      "auroc": 0.5593051910400391,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5563907623291016,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.009765625,
      "tpr_at_1pct_fpr": 0.0322265625
    },
    {
      "auroc": 0.5531148910522461,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5510740280151367,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0244140625
    },
    {
      "auroc": 0.550567626953125,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.021484375
    },
    {
      "auroc": 0.5502452850341797,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5472612380981445,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5450592041015625,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5417795181274414,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.5366334915161133,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.5334692001342773,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0068359375,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5304126739501953,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5265398025512695,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.5225448608398438,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.519953727722168,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.009765625,
      "tpr_at_1pct_fpr": 0.021484375
    },
    {
      "auroc": 0.5197067260742188,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5189933776855469,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5186882019042969,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.518000602722168,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5176410675048828,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5175561904907227,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.5152921676635742,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5146703720092773,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5125665664672852,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.5124130249023438,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5111761093139648,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5089702606201172,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5088119506835938,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.5079202651977539,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.5055990219116211,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.5053548812866211,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5029392242431641,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5016946792602539,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5014400482177734,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.5005397796630859,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5000829696655273,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5000486373901367,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.4998779296875,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.49970149993896484,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0205078125
    },
    {
      "auroc": 0.4988822937011719,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4988384246826172,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.49704551696777344,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.49623584747314453,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.4960641860961914,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.4924001693725586,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.492218017578125,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.49021053314208984,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.4875812530517578,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.4866218566894531,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.47428226470947266,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    }
  ],
  "library": "auto-round",
  "library_version": "0.14.2",
  "mean_changed_weight_fraction_vs_artifact0": null,
  "method": "AutoRound",
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 0.9498500823974609,
      "tpr_at_0_1pct_fpr": 0.158203125,
      "tpr_at_1pct_fpr": 0.431640625
    },
    "artifact_reconstruction": {
      "auroc": 0.5775547027587891,
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.013671875
    },
    "output_combination": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_kl": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_logit_mse": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_logprob": {
      "auroc": 0.6580681800842285,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    "output_logprob_gap": {
      "auroc": 0.6580681800842285,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.013671875
    }
  },
  "model": "facebook/opt-125m",
  "model_dtype": "float16",
  "model_revision": "27dcfa74d334bc871f3234de431e71c6eeba5dd6",
  "output_combination": {
    "coefficients": {
      "output_kl": 3.362545638999596,
      "output_logit_mse": 3.4955879099558844,
      "output_logprob": 0.1695291100951989,
      "output_logprob_gap": 0.1695291100951989
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 1.0,
    "shadow_split_auroc": 1.0
  },
  "parameters": 125239296,
  "per_target_auroc": {
    "artifact_layer_combination": {
      "lower_quartile": 0.9326171875,
      "maximum": 1.0,
      "median": 0.955078125,
      "minimum": 0.796875,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 56,
      "upper_quartile": 0.98046875
    },
    "artifact_reconstruction": {
      "lower_quartile": 0.53515625,
      "maximum": 0.859375,
      "median": 0.607421875,
      "minimum": 0.1796875,
      "targets_above_chance": 50,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6494140625
    },
    "output_combination": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 64,
      "upper_quartile": 1.0
    },
    "output_kl": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 64,
      "upper_quartile": 1.0
    },
    "output_logit_mse": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 64,
      "upper_quartile": 1.0
    },
    "output_logprob": {
      "lower_quartile": 0.57958984375,
      "maximum": 0.98828125,
      "median": 0.6640625,
      "minimum": 0.23828125,
      "targets_above_chance": 54,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.7392578125
    },
    "output_logprob_gap": {
      "lower_quartile": 0.57958984375,
      "maximum": 0.98828125,
      "median": 0.6640625,
      "minimum": 0.23828125,
      "targets_above_chance": 54,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.7392578125
    }
  },
  "population_sha256": "f2dadc85c4fc75300397fe4f1562efdc60d90becb7f717d0554d1e81f8f4f765",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "document_count": 4000,
    "earliest_published": "2024-01-01T00:54:02Z",
    "identifier_sha256": "6cf2151daecdb3ec893ce81d946bcdfa1c21bbd06d03b7b05064f1782132e412",
    "latest_published": "2024-02-10T00:49:46Z",
    "path": "data\\arxiv_cs_lg_2024.jsonl",
    "pool_sha256": "0f507b9770faeaeb93f062886772c8728eb57429226fb5d0532c26727f5f7e84",
    "queries": [
      "cat:cs.LG AND submittedDate:[202401010000 TO 202412312359]"
    ],
    "required_published_after": "2023-12-31T23:59:59Z",
    "seed": 20260922,
    "sha256": "bdb4a18acfeb49e89ecc29bb54c3dcdd9f0ce67a1a9936a92db7d95cdc79e454",
    "source": "text_jsonl",
    "sources": [
      "arXiv API"
    ],
    "text_field": "text"
  },
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.002002589313183234,
    "base_mean_logprob": -3.8453422486782074,
    "base_perplexity": 46.774690187658,
    "mean_logprob_change": -0.01084721996448934,
    "perplexity_ratio_quantized_over_base": 1.010906264350998,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -3.8561894686426967,
    "quantized_perplexity": 47.284827323780625,
    "reference_decisions": 1024
  },
  "selected_artifact_feature": "artifact_layer_combination",
  "selected_output_baseline": "output_logit_mse",
  "sequence_length": 512,
  "shadow_artifacts": 32,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 18,
        "test_fpr": 0.017578125,
        "test_tpr": 0.607421875,
        "test_true_positives": 622,
        "threshold": 1.0036997607540574
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 25,
        "test_fpr": 0.0244140625,
        "test_tpr": 0.0263671875,
        "test_true_positives": 27,
        "threshold": 2.0746702032212068
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 11,
        "test_fpr": 0.0107421875,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -2.055855287311194
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 12,
        "test_fpr": 0.01171875,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -1.407526129450246
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 17,
        "test_fpr": 0.0166015625,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -2.5371902307163223
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 20,
        "test_fpr": 0.01953125,
        "test_tpr": 0.04296875,
        "test_true_positives": 44,
        "threshold": 2.007656511151942
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 20,
        "test_fpr": 0.01953125,
        "test_tpr": 0.04296875,
        "test_true_positives": 44,
        "threshold": 2.007656511151942
      }
    }
  },
  "shadow_metrics": {
    "artifact_layer_combination": {
      "auroc": 0.9557418823242188,
      "tpr_at_0_1pct_fpr": 0.2978515625,
      "tpr_at_1pct_fpr": 0.587890625
    },
    "artifact_reconstruction": {
      "auroc": 0.6466894149780273,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.03125
    },
    "output_combination": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_kl": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_logit_mse": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_logprob": {
      "auroc": 0.7013740539550781,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0400390625
    },
    "output_logprob_gap": {
      "auroc": 0.7013740539550781,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0400390625
    }
  },
  "targets": 64,
  "test_artifacts": 32,
  "test_decisions": 2048,
  "test_members": 1024,
  "test_nonmembers": 1024,
  "threat_model": "public base, released auto-round W4 artifact, one held-out artifact"
}
```
