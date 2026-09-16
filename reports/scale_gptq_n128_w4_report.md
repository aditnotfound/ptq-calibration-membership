# CalibTrace named-library attack report

Library `llm-compressor` 0.13.0 quantizes `facebook/opt-125m` to W4A16 from 24 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 32 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 1.0000 | 1.0000 | 1.0000 |
| artifact_layer_combination | 1.0000 | 1.0000 | 1.0000 |
| output_logit_mse | 0.8262 | 0.2266 | 0.1719 |
| output_kl | 0.7301 | 0.0625 | 0.0234 |
| output_logprob | 0.4801 | 0.0195 | 0.0078 |
| output_logprob_gap | 0.4801 | 0.0195 | 0.0078 |
| output_combination | 0.8279 | 0.2461 | 0.1797 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_combination`: 0.1721 AUROC, crossed-bootstrap 95% interval [0.1103, 0.2323]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 640 calibration-excluded reference scores, mean token log probability changes by -0.046090; the corresponding perplexity ratio is 1.047169.

## Generation runtime

The 40 quantize-and-score jobs took 28.2 minutes in aggregate, with mean 42.3 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.0.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.1.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.10.fc1 | 1.0000 | 1.0000 |
| model.decoder.layers.10.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.10.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.11.fc1 | 1.0000 | 1.0000 |
| model.decoder.layers.11.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.11.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.2.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.2.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.3.fc2 | 1.0000 | 1.0000 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.6977 | 0.0859 |
| artifact_layer_combination | 0.9940 | 0.8281 |
| selected_artifact | 0.9940 | 0.8281 |
| selected_output | 0.6312 | 0.0586 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": 0.17205810546875,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.362762451171875,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.9818846289637483,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.6995326572928141,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.7201113018557403,
          "upper_95": 1.0
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": 0.29335496455043386,
        "upper_95": 0.42758467616936946
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.6224071857987582,
          "upper_95": 0.7974427613624832
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.023713080825371137,
          "upper_95": 0.20091070449143755
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.026907894736842106,
          "upper_95": 0.207196113505163
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.5768861339922186,
          "upper_95": 0.7181413562297838
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.15386792452830186
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.007838629704755466,
          "upper_95": 0.18147595647595646
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.5456961315230905,
          "upper_95": 0.6849115169924845
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.004047368421052632,
          "upper_95": 0.10802373540856029
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.011535171102661598,
          "upper_95": 0.1288001209816799
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.5752042261488304,
          "upper_95": 0.7106888393873158
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.1478782835622646
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.16981504959355656
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4384196754135962,
          "upper_95": 0.5629029752675733
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.048983172216254915
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.060383076043453394
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.45732894882245695,
          "upper_95": 0.6202560582976957
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.05085078099036225
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.06178033279803191
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.9818846289637483,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.6995326572928141,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.7201113018557403,
          "upper_95": 1.0
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.5641663611925709,
          "upper_95": 0.6996048301195992
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.1380775967103259
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.1578999375910131
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.99395751953125,
        "tpr_at_0_1pct_fpr": 0.8203125,
        "tpr_at_1pct_fpr": 0.828125
      },
      "artifact_reconstruction": {
        "auroc": 0.6977081298828125,
        "tpr_at_0_1pct_fpr": 0.05859375,
        "tpr_at_1pct_fpr": 0.0859375
      },
      "output_combination": {
        "auroc": 0.646453857421875,
        "tpr_at_0_1pct_fpr": 0.01953125,
        "tpr_at_1pct_fpr": 0.0390625
      },
      "output_kl": {
        "auroc": 0.6107330322265625,
        "tpr_at_0_1pct_fpr": 0.02734375,
        "tpr_at_1pct_fpr": 0.05078125
      },
      "output_logit_mse": {
        "auroc": 0.6407470703125,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.0625
      },
      "output_logprob": {
        "auroc": 0.50323486328125,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.015625
      },
      "output_logprob_gap": {
        "auroc": 0.5385284423828125,
        "tpr_at_0_1pct_fpr": 0.01171875,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "selected_artifact": {
        "auroc": 0.99395751953125,
        "tpr_at_0_1pct_fpr": 0.8203125,
        "tpr_at_1pct_fpr": 0.828125
      },
      "selected_output": {
        "auroc": 0.631195068359375,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.05859375
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20260933,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          26,
          23,
          11,
          0,
          22,
          2,
          14,
          4,
          16,
          10,
          9,
          31,
          7,
          5,
          27,
          8
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 0.01,
        "output_validation_auroc": 0.6822079895788102,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_logit_mse",
        "training_candidates": [
          1,
          3,
          6,
          12,
          13,
          15,
          17,
          18,
          19,
          20,
          21,
          24,
          25,
          28,
          29,
          30
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          24,
          12,
          30,
          21,
          3,
          19,
          20,
          15,
          17,
          29,
          28,
          13,
          18,
          1,
          25,
          6
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.6569148936170213,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
        "training_candidates": [
          0,
          2,
          4,
          5,
          7,
          8,
          9,
          10,
          11,
          14,
          16,
          22,
          23,
          26,
          27,
          31
        ]
      }
    ]
  },
  "cluster_bootstrap": {
    "artifact_layer_combination": {
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
    "artifact_minus_output_combination_auroc": {
      "lower_95": 0.11026021800495167,
      "upper_95": 0.2323252091490537
    },
    "artifact_reconstruction": {
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
    "output_combination": {
      "auroc": {
        "lower_95": 0.7676747908509461,
        "upper_95": 0.8897397819950483
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.11376371384531689,
        "upper_95": 0.3700897198607146
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.13383212352362206,
        "upper_95": 0.42694999999999994
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.6568202499499586,
        "upper_95": 0.8021645561273938
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.003532608695652179,
        "upper_95": 0.15605256916996044
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.007574333561175667,
        "upper_95": 0.24219341856060606
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.7663659431369065,
        "upper_95": 0.8891827154212332
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.10456681277810985,
        "upper_95": 0.3617990205492606
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.12550567595459236,
        "upper_95": 0.42641648168701446
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.37840486646764626,
        "upper_95": 0.5746349842488454
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06136374044053664
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06896865203761755
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.37840486646764626,
        "upper_95": 0.5746349842488454
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06136374044053664
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06896865203761755
      }
    }
  },
  "empirical_test_fpr_resolution": 0.00390625,
  "experiment_sha256": "dc2b7e7227cf6d7df1cf9b97fa50eb7c0eb203822d8476cdbe9ebd76aa360cd1",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4491416931152344,
    "null_mean": 0.4997588409423828,
    "null_upper_95": 0.5522312164306641,
    "observed_auroc": 1.0,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 40,
    "maximum_seconds": 43.46382270002505,
    "mean_seconds_per_artifact": 42.2800766150016,
    "minimum_seconds": 40.70061790000182,
    "total_seconds": 1691.203064600064
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.06756086485228231,
      "model.decoder.layers.0.fc2": 0.23864679155057847,
      "model.decoder.layers.0.self_attn.k_proj": 0.10907440232324656,
      "model.decoder.layers.0.self_attn.out_proj": 0.3102058335360831,
      "model.decoder.layers.0.self_attn.q_proj": 0.10255548273396736,
      "model.decoder.layers.0.self_attn.v_proj": 0.14433759883790312,
      "model.decoder.layers.1.fc1": 0.046460306106005496,
      "model.decoder.layers.1.fc2": 0.2587352989645919,
      "model.decoder.layers.1.self_attn.k_proj": 0.08946247460167897,
      "model.decoder.layers.1.self_attn.out_proj": 0.32358104375536534,
      "model.decoder.layers.1.self_attn.q_proj": 0.11428662709697811,
      "model.decoder.layers.1.self_attn.v_proj": 0.12529856421124314,
      "model.decoder.layers.10.fc1": 0.12578254108328304,
      "model.decoder.layers.10.fc2": 0.29160172259940415,
      "model.decoder.layers.10.self_attn.k_proj": 0.08261267726730381,
      "model.decoder.layers.10.self_attn.out_proj": 0.2786851458867925,
      "model.decoder.layers.10.self_attn.q_proj": 0.09844410331598463,
      "model.decoder.layers.10.self_attn.v_proj": 0.0711079152459417,
      "model.decoder.layers.11.fc1": 0.19244154100716637,
      "model.decoder.layers.11.fc2": 0.2947099862061099,
      "model.decoder.layers.11.self_attn.k_proj": 0.15655294992009003,
      "model.decoder.layers.11.self_attn.out_proj": 0.3190811045761551,
      "model.decoder.layers.11.self_attn.q_proj": 0.10988443304073979,
      "model.decoder.layers.11.self_attn.v_proj": 0.1162603533125336,
      "model.decoder.layers.2.fc1": 0.05838809884003772,
      "model.decoder.layers.2.fc2": 0.23297433948012888,
      "model.decoder.layers.2.self_attn.k_proj": 0.1480307736234563,
      "model.decoder.layers.2.self_attn.out_proj": 0.24091434578457932,
      "model.decoder.layers.2.self_attn.q_proj": 0.08470624393685798,
      "model.decoder.layers.2.self_attn.v_proj": 0.085287472567905,
      "model.decoder.layers.3.fc1": 0.10020260743989406,
      "model.decoder.layers.3.fc2": 0.22944551396654214,
      "model.decoder.layers.3.self_attn.k_proj": 0.07187700108967407,
      "model.decoder.layers.3.self_attn.out_proj": 0.2312074452863084,
      "model.decoder.layers.3.self_attn.q_proj": 0.08523261182233573,
      "model.decoder.layers.3.self_attn.v_proj": 0.10202064096166201,
      "model.decoder.layers.4.fc1": 0.02264467266603299,
      "model.decoder.layers.4.fc2": 0.2411090478360901,
      "model.decoder.layers.4.self_attn.k_proj": 0.03236651994944146,
      "model.decoder.layers.4.self_attn.out_proj": 0.1490265447420163,
      "model.decoder.layers.4.self_attn.q_proj": 0.028636228011053748,
      "model.decoder.layers.4.self_attn.v_proj": -0.0010536265085742437,
      "model.decoder.layers.5.fc1": 0.08739083485315585,
      "model.decoder.layers.5.fc2": 0.27082839213186005,
      "model.decoder.layers.5.self_attn.k_proj": 0.09553476150338856,
      "model.decoder.layers.5.self_attn.out_proj": 0.18657190039400487,
      "model.decoder.layers.5.self_attn.q_proj": 0.02476816723414173,
      "model.decoder.layers.5.self_attn.v_proj": 0.040353403544685175,
      "model.decoder.layers.6.fc1": 0.047016422470798694,
      "model.decoder.layers.6.fc2": 0.28580996925981195,
      "model.decoder.layers.6.self_attn.k_proj": 0.10091040254378396,
      "model.decoder.layers.6.self_attn.out_proj": 0.20180520248489744,
      "model.decoder.layers.6.self_attn.q_proj": 0.050224717880533155,
      "model.decoder.layers.6.self_attn.v_proj": 0.028169178657920946,
      "model.decoder.layers.7.fc1": 0.08928973622230572,
      "model.decoder.layers.7.fc2": 0.29977662200426775,
      "model.decoder.layers.7.self_attn.k_proj": 0.011325700279135572,
      "model.decoder.layers.7.self_attn.out_proj": 0.2461234247485099,
      "model.decoder.layers.7.self_attn.q_proj": 0.010409360222884969,
      "model.decoder.layers.7.self_attn.v_proj": 0.04819266059929223,
      "model.decoder.layers.8.fc1": 0.0640652698931437,
      "model.decoder.layers.8.fc2": 0.31330838523016535,
      "model.decoder.layers.8.self_attn.k_proj": 0.037666833014678734,
      "model.decoder.layers.8.self_attn.out_proj": 0.26475630756923296,
      "model.decoder.layers.8.self_attn.q_proj": 0.0493826249771718,
      "model.decoder.layers.8.self_attn.v_proj": 0.08046868609867135,
      "model.decoder.layers.9.fc1": 0.09211547761541819,
      "model.decoder.layers.9.fc2": 0.2693813373393351,
      "model.decoder.layers.9.self_attn.k_proj": 0.07298835835704973,
      "model.decoder.layers.9.self_attn.out_proj": 0.22785564651765042,
      "model.decoder.layers.9.self_attn.q_proj": 0.06660202388810497,
      "model.decoder.layers.9.self_attn.v_proj": 0.059589681242072125
    },
    "regularization": 1.0,
    "shadow_split_auroc": 1.0
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999847412109375,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999969482421875,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.99993896484375,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.999847412109375,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.9921875,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.99981689453125,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.953125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9997406005859375,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.9997100830078125,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.999542236328125,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.98046875,
      "tpr_at_1pct_fpr": 0.98828125
    },
    {
      "auroc": 0.9995269775390625,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.984375
    },
    {
      "auroc": 0.99951171875,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.98046875,
      "tpr_at_1pct_fpr": 0.98828125
    },
    {
      "auroc": 0.99945068359375,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.9993896484375,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.921875,
      "tpr_at_1pct_fpr": 0.98828125
    },
    {
      "auroc": 0.9993896484375,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.9609375,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.99908447265625,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.921875,
      "tpr_at_1pct_fpr": 0.98046875
    },
    {
      "auroc": 0.9990386962890625,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.93359375,
      "tpr_at_1pct_fpr": 0.98046875
    },
    {
      "auroc": 0.9989776611328125,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.96484375,
      "tpr_at_1pct_fpr": 0.98046875
    },
    {
      "auroc": 0.9989471435546875,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.97265625,
      "tpr_at_1pct_fpr": 0.9765625
    },
    {
      "auroc": 0.9988861083984375,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.94140625,
      "tpr_at_1pct_fpr": 0.96875
    },
    {
      "auroc": 0.9986724853515625,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.96875,
      "tpr_at_1pct_fpr": 0.98046875
    },
    {
      "auroc": 0.998565673828125,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.94140625,
      "tpr_at_1pct_fpr": 0.9765625
    },
    {
      "auroc": 0.99847412109375,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.90234375,
      "tpr_at_1pct_fpr": 0.9765625
    },
    {
      "auroc": 0.9984283447265625,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.93359375,
      "tpr_at_1pct_fpr": 0.9609375
    },
    {
      "auroc": 0.9983367919921875,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 0.94921875
    },
    {
      "auroc": 0.9983367919921875,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.859375,
      "tpr_at_1pct_fpr": 0.92578125
    },
    {
      "auroc": 0.998321533203125,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.94921875,
      "tpr_at_1pct_fpr": 0.97265625
    },
    {
      "auroc": 0.997955322265625,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.89453125,
      "tpr_at_1pct_fpr": 0.95703125
    },
    {
      "auroc": 0.997955322265625,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.953125,
      "tpr_at_1pct_fpr": 0.953125
    },
    {
      "auroc": 0.99749755859375,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.85546875,
      "tpr_at_1pct_fpr": 0.94921875
    },
    {
      "auroc": 0.9974517822265625,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.85546875,
      "tpr_at_1pct_fpr": 0.9375
    },
    {
      "auroc": 0.9974212646484375,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.8203125,
      "tpr_at_1pct_fpr": 0.91015625
    },
    {
      "auroc": 0.997283935546875,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.8828125,
      "tpr_at_1pct_fpr": 0.95703125
    },
    {
      "auroc": 0.99725341796875,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.875,
      "tpr_at_1pct_fpr": 0.94140625
    },
    {
      "auroc": 0.997222900390625,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.90625,
      "tpr_at_1pct_fpr": 0.91796875
    },
    {
      "auroc": 0.996734619140625,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.8828125,
      "tpr_at_1pct_fpr": 0.89453125
    },
    {
      "auroc": 0.996673583984375,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.78125,
      "tpr_at_1pct_fpr": 0.89453125
    },
    {
      "auroc": 0.9964599609375,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.87890625,
      "tpr_at_1pct_fpr": 0.9140625
    },
    {
      "auroc": 0.99639892578125,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.91796875,
      "tpr_at_1pct_fpr": 0.953125
    },
    {
      "auroc": 0.996368408203125,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.82421875,
      "tpr_at_1pct_fpr": 0.921875
    },
    {
      "auroc": 0.996337890625,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.8671875,
      "tpr_at_1pct_fpr": 0.92578125
    },
    {
      "auroc": 0.99554443359375,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.734375,
      "tpr_at_1pct_fpr": 0.89453125
    },
    {
      "auroc": 0.9952392578125,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.6328125,
      "tpr_at_1pct_fpr": 0.9296875
    },
    {
      "auroc": 0.992828369140625,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.66015625,
      "tpr_at_1pct_fpr": 0.91015625
    },
    {
      "auroc": 0.9908294677734375,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.80859375,
      "tpr_at_1pct_fpr": 0.87109375
    },
    {
      "auroc": 0.9904632568359375,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.8203125,
      "tpr_at_1pct_fpr": 0.84375
    },
    {
      "auroc": 0.9872589111328125,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.69140625,
      "tpr_at_1pct_fpr": 0.82421875
    }
  ],
  "library": "llm-compressor",
  "library_version": "0.13.0",
  "mean_changed_weight_fraction_vs_artifact0": null,
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "artifact_reconstruction": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.82794189453125,
      "tpr_at_0_1pct_fpr": 0.1796875,
      "tpr_at_1pct_fpr": 0.24609375
    },
    "output_kl": {
      "auroc": 0.7300567626953125,
      "tpr_at_0_1pct_fpr": 0.0234375,
      "tpr_at_1pct_fpr": 0.0625
    },
    "output_logit_mse": {
      "auroc": 0.8261871337890625,
      "tpr_at_0_1pct_fpr": 0.171875,
      "tpr_at_1pct_fpr": 0.2265625
    },
    "output_logprob": {
      "auroc": 0.4801025390625,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    "output_logprob_gap": {
      "auroc": 0.4801025390625,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01953125
    }
  },
  "model": "facebook/opt-125m",
  "model_dtype": "float16",
  "model_revision": "27dcfa74d334bc871f3234de431e71c6eeba5dd6",
  "output_combination": {
    "coefficients": {
      "output_kl": 0.06812794598126615,
      "output_logit_mse": 2.0650692594107976,
      "output_logprob": 0.024250981994473633,
      "output_logprob_gap": 0.0242509819944741
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 1.0,
    "shadow_split_auroc": 0.8819173177083334
  },
  "parameters": 125239296,
  "per_target_auroc": {
    "artifact_layer_combination": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 32,
      "upper_quartile": 1.0
    },
    "artifact_reconstruction": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 32,
      "upper_quartile": 1.0
    },
    "output_combination": {
      "lower_quartile": 0.75,
      "maximum": 1.0,
      "median": 0.8125,
      "minimum": 0.53125,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 13,
      "upper_quartile": 0.9375
    },
    "output_kl": {
      "lower_quartile": 0.6328125,
      "maximum": 0.921875,
      "median": 0.71875,
      "minimum": 0.46875,
      "targets_above_chance": 30,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.8359375
    },
    "output_logit_mse": {
      "lower_quartile": 0.765625,
      "maximum": 1.0,
      "median": 0.8203125,
      "minimum": 0.53125,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 13,
      "upper_quartile": 0.921875
    },
    "output_logprob": {
      "lower_quartile": 0.34765625,
      "maximum": 0.84375,
      "median": 0.4765625,
      "minimum": 0.125,
      "targets_above_chance": 13,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.625
    },
    "output_logprob_gap": {
      "lower_quartile": 0.34765625,
      "maximum": 0.84375,
      "median": 0.4765625,
      "minimum": 0.125,
      "targets_above_chance": 13,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.625
    }
  },
  "population_sha256": "fb2c48f3d9d3f06bb85386fd23cb9ba154be863679ac930291742fe70e954ac5",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "document_count": 4000,
    "earliest_published": "2024-01-01T00:54:02Z",
    "identifier_sha256": "6cf2151daecdb3ec893ce81d946bcdfa1c21bbd06d03b7b05064f1782132e412",
    "latest_published": "2024-02-10T00:49:46Z",
    "path": "data\\arxiv_cs_lg_2024.jsonl",
    "pool_sha256": "78ac160354ed41ac00061996278574f67a1e0656d5202a412d0ff92808b1fb61",
    "queries": [
      "cat:cs.LG AND submittedDate:[202401010000 TO 202412312359]"
    ],
    "required_published_after": "2023-12-31T23:59:59Z",
    "seed": 20260932,
    "sha256": "bdb4a18acfeb49e89ecc29bb54c3dcdd9f0ce67a1a9936a92db7d95cdc79e454",
    "source": "text_jsonl",
    "sources": [
      "arXiv API"
    ],
    "text_field": "text"
  },
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.003088825965993313,
    "base_mean_logprob": -3.8099349588155746,
    "base_perplexity": 45.147502323796665,
    "mean_logprob_change": -0.04609011560678482,
    "perplexity_ratio_quantized_over_base": 1.0471687729545098,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -3.8560250744223596,
    "quantized_perplexity": 47.277054610371046,
    "reference_decisions": 640
  },
  "selected_artifact_feature": "artifact_layer_combination",
  "selected_output_baseline": "output_combination",
  "sequence_length": 512,
  "shadow_artifacts": 24,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -1.506983394258677
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -0.3881782169498345
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 2,
        "test_fpr": 0.0078125,
        "test_tpr": 0.24609375,
        "test_true_positives": 63,
        "threshold": 1.3978985034830365
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 6,
        "test_fpr": 0.0234375,
        "test_tpr": 0.109375,
        "test_true_positives": 28,
        "threshold": 1.5489835905701113
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.01171875,
        "test_tpr": 0.24609375,
        "test_true_positives": 63,
        "threshold": 1.3935153554838444
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 6,
        "test_fpr": 0.0234375,
        "test_tpr": 0.03515625,
        "test_true_positives": 9,
        "threshold": 2.264638014252747
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 6,
        "test_fpr": 0.0234375,
        "test_tpr": 0.03515625,
        "test_true_positives": 9,
        "threshold": 2.26463801425275
      }
    }
  },
  "shadow_metrics": {
    "artifact_layer_combination": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "artifact_reconstruction": {
      "auroc": 0.9998643663194445,
      "tpr_at_0_1pct_fpr": 0.9479166666666666,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.8889092339409721,
      "tpr_at_0_1pct_fpr": 0.20572916666666666,
      "tpr_at_1pct_fpr": 0.3020833333333333
    },
    "output_kl": {
      "auroc": 0.7564629448784722,
      "tpr_at_0_1pct_fpr": 0.059895833333333336,
      "tpr_at_1pct_fpr": 0.16145833333333334
    },
    "output_logit_mse": {
      "auroc": 0.8888888888888888,
      "tpr_at_0_1pct_fpr": 0.18229166666666666,
      "tpr_at_1pct_fpr": 0.2994791666666667
    },
    "output_logprob": {
      "auroc": 0.6108194986979166,
      "tpr_at_0_1pct_fpr": 0.0026041666666666665,
      "tpr_at_1pct_fpr": 0.010416666666666666
    },
    "output_logprob_gap": {
      "auroc": 0.6108194986979166,
      "tpr_at_0_1pct_fpr": 0.0026041666666666665,
      "tpr_at_1pct_fpr": 0.010416666666666666
    }
  },
  "targets": 32,
  "test_artifacts": 16,
  "test_decisions": 512,
  "test_members": 256,
  "test_nonmembers": 256,
  "threat_model": "public base, released llm-compressor W4 artifact, one held-out artifact"
}
```
