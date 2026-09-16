# CalibTrace named-library attack report

Library `llm-compressor` 0.13.0 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 32 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 1.0000 | 1.0000 | 1.0000 |
| artifact_layer_combination | 1.0000 | 1.0000 | 1.0000 |
| output_logit_mse | 0.4474 | 0.0078 | 0.0039 |
| output_kl | 0.4803 | 0.0000 | 0.0000 |
| output_logprob | 0.5045 | 0.0156 | 0.0000 |
| output_logprob_gap | 0.5045 | 0.0156 | 0.0000 |
| output_combination | 0.5474 | 0.0000 | 0.0000 |

Selected artifact feature `artifact_reconstruction` minus selected output baseline `output_combination`: 0.4526 AUROC, crossed-bootstrap 95% interval [0.3743, 0.5376]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 768 calibration-excluded reference scores, mean token log probability changes by -0.100726; the corresponding perplexity ratio is 1.105974.

## Generation runtime

The 48 quantize-and-score jobs took 45.3 minutes in aggregate, with mean 56.6 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.0.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.1.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.10.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.10.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.11.fc1 | 1.0000 | 1.0000 |
| model.decoder.layers.11.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.11.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.2.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.2.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.3.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.3.self_attn.out_proj | 1.0000 | 1.0000 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.7551 | 0.1641 |
| artifact_layer_combination | 0.9910 | 0.7188 |
| selected_artifact | 0.9910 | 0.7188 |
| selected_output | 0.5329 | 0.0000 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": 0.4526214599609375,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.4580535888671875,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.9677906426956853,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.555943637737116,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.5656087770131596,
          "upper_95": 1.0
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": 0.3725453146940994,
        "upper_95": 0.5397485763690255
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.688095915618444,
          "upper_95": 0.834735820192094
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.06337805312889998,
          "upper_95": 0.36419940622692576
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.07142151326933935,
          "upper_95": 0.38937628073770486
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.4413225202840646,
          "upper_95": 0.6260767075750451
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.04513438769337134
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.07730601539614411
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.4281477587132752,
          "upper_95": 0.6110163922342492
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.024014754098360642
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.07227834762873224
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.4272737631699906,
          "upper_95": 0.608676581308622
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.030657258243465133
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.04203934792801239
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4385096849830715,
          "upper_95": 0.5610273099536739
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.04907624025219835
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.061550387596899216
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.43151363188302116,
          "upper_95": 0.5739675978731722
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.05020404672303405
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.07114624505928854
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.9677906426956853,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.555943637737116,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.5656087770131596,
          "upper_95": 1.0
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.450961243872549,
          "upper_95": 0.6162260516396609
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.02084441489361701
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.05729662544717046
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.990966796875,
        "tpr_at_0_1pct_fpr": 0.703125,
        "tpr_at_1pct_fpr": 0.71875
      },
      "artifact_reconstruction": {
        "auroc": 0.755096435546875,
        "tpr_at_0_1pct_fpr": 0.13671875,
        "tpr_at_1pct_fpr": 0.1640625
      },
      "output_combination": {
        "auroc": 0.5324859619140625,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.0078125
      },
      "output_kl": {
        "auroc": 0.517486572265625,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0
      },
      "output_logit_mse": {
        "auroc": 0.5128631591796875,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "output_logprob": {
        "auroc": 0.4999542236328125,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "output_logprob_gap": {
        "auroc": 0.498992919921875,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.015625
      },
      "selected_artifact": {
        "auroc": 0.990966796875,
        "tpr_at_0_1pct_fpr": 0.703125,
        "tpr_at_1pct_fpr": 0.71875
      },
      "selected_output": {
        "auroc": 0.5329132080078125,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20260913,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          5,
          26,
          28,
          24,
          7,
          2,
          23,
          19,
          14,
          4,
          12,
          0,
          3,
          13,
          8,
          21
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.5413818359375,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
        "training_candidates": [
          1,
          6,
          9,
          10,
          11,
          15,
          16,
          17,
          18,
          20,
          22,
          25,
          27,
          29,
          30,
          31
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          10,
          1,
          20,
          29,
          18,
          11,
          9,
          15,
          27,
          6,
          16,
          30,
          25,
          31,
          17,
          22
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 0.001,
        "output_validation_auroc": 0.4517822265625,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_kl",
        "training_candidates": [
          0,
          2,
          3,
          4,
          5,
          7,
          8,
          12,
          13,
          14,
          19,
          21,
          23,
          24,
          26,
          28
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
      "lower_95": 0.37425287164337845,
      "upper_95": 0.5375780650374643
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
        "lower_95": 0.46242193496253575,
        "upper_95": 0.6257471283566215
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.015629631916996043
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.043833501336021374
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.3895431028506149,
        "upper_95": 0.5688927694559582
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.02874985818821255
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.3629247425477708,
        "upper_95": 0.5367097651373454
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.030657258243465133
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.03435443537773098
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.43223482272978275,
        "upper_95": 0.5886671181810478
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.05384615384615385
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06584362139917696
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.43223482272978275,
        "upper_95": 0.5886671181810478
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.05384615384615385
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06584362139917696
      }
    }
  },
  "empirical_test_fpr_resolution": 0.00390625,
  "experiment_sha256": "b8de09ab417092aee36ad69467de3d90ed273ba93c1c8ae3fe15109b49afd11a",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4479667663574219,
    "null_mean": 0.49955303344726565,
    "null_upper_95": 0.5504810333251953,
    "observed_auroc": 1.0,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 48,
    "maximum_seconds": 65.867783099995,
    "mean_seconds_per_artifact": 56.58245623541249,
    "minimum_seconds": 39.854585199966095,
    "total_seconds": 2715.9578992997995
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.10421671199661219,
      "model.decoder.layers.0.fc2": 0.19275124913766362,
      "model.decoder.layers.0.self_attn.k_proj": 0.08724707983375454,
      "model.decoder.layers.0.self_attn.out_proj": 0.1658429959630435,
      "model.decoder.layers.0.self_attn.q_proj": 0.0835071297507791,
      "model.decoder.layers.0.self_attn.v_proj": 0.057505290530884594,
      "model.decoder.layers.1.fc1": 0.11690773952328923,
      "model.decoder.layers.1.fc2": 0.18743646937913008,
      "model.decoder.layers.1.self_attn.k_proj": 0.10768218120821732,
      "model.decoder.layers.1.self_attn.out_proj": 0.18606257179627747,
      "model.decoder.layers.1.self_attn.q_proj": 0.12874584552823648,
      "model.decoder.layers.1.self_attn.v_proj": 0.11803355970053102,
      "model.decoder.layers.10.fc1": 0.17454616397976735,
      "model.decoder.layers.10.fc2": 0.1928147387052658,
      "model.decoder.layers.10.self_attn.k_proj": 0.137253831640619,
      "model.decoder.layers.10.self_attn.out_proj": 0.19663414005097204,
      "model.decoder.layers.10.self_attn.q_proj": 0.14451799968899126,
      "model.decoder.layers.10.self_attn.v_proj": 0.14735795028473128,
      "model.decoder.layers.11.fc1": 0.19578092497926045,
      "model.decoder.layers.11.fc2": 0.19411334415914996,
      "model.decoder.layers.11.self_attn.k_proj": 0.1536843219088255,
      "model.decoder.layers.11.self_attn.out_proj": 0.19635154486525944,
      "model.decoder.layers.11.self_attn.q_proj": 0.15544591766628552,
      "model.decoder.layers.11.self_attn.v_proj": 0.14958006695115772,
      "model.decoder.layers.2.fc1": 0.11700511572028859,
      "model.decoder.layers.2.fc2": 0.18350465914073413,
      "model.decoder.layers.2.self_attn.k_proj": 0.12286426315972485,
      "model.decoder.layers.2.self_attn.out_proj": 0.1926860574465721,
      "model.decoder.layers.2.self_attn.q_proj": 0.13178264748414412,
      "model.decoder.layers.2.self_attn.v_proj": 0.12515708609769347,
      "model.decoder.layers.3.fc1": 0.09271357470262445,
      "model.decoder.layers.3.fc2": 0.17486345252218122,
      "model.decoder.layers.3.self_attn.k_proj": 0.11691284866856888,
      "model.decoder.layers.3.self_attn.out_proj": 0.18975442095759348,
      "model.decoder.layers.3.self_attn.q_proj": 0.10989325491888141,
      "model.decoder.layers.3.self_attn.v_proj": 0.11256183474926726,
      "model.decoder.layers.4.fc1": 0.14043186657419365,
      "model.decoder.layers.4.fc2": 0.19364754863724265,
      "model.decoder.layers.4.self_attn.k_proj": 0.13157560908562352,
      "model.decoder.layers.4.self_attn.out_proj": 0.19249899995426448,
      "model.decoder.layers.4.self_attn.q_proj": 0.12538435341628418,
      "model.decoder.layers.4.self_attn.v_proj": 0.12256462118988637,
      "model.decoder.layers.5.fc1": 0.14660536903643656,
      "model.decoder.layers.5.fc2": 0.19600714402732827,
      "model.decoder.layers.5.self_attn.k_proj": 0.12891193498097853,
      "model.decoder.layers.5.self_attn.out_proj": 0.19167154682725193,
      "model.decoder.layers.5.self_attn.q_proj": 0.11691858419225622,
      "model.decoder.layers.5.self_attn.v_proj": 0.1356946668256993,
      "model.decoder.layers.6.fc1": 0.15527275252228157,
      "model.decoder.layers.6.fc2": 0.19669777892610207,
      "model.decoder.layers.6.self_attn.k_proj": 0.12529412922299674,
      "model.decoder.layers.6.self_attn.out_proj": 0.19220998372747505,
      "model.decoder.layers.6.self_attn.q_proj": 0.1310742212570397,
      "model.decoder.layers.6.self_attn.v_proj": 0.1267520212217908,
      "model.decoder.layers.7.fc1": 0.15210472473556724,
      "model.decoder.layers.7.fc2": 0.19987934946695385,
      "model.decoder.layers.7.self_attn.k_proj": 0.1090466340380862,
      "model.decoder.layers.7.self_attn.out_proj": 0.18745328756882768,
      "model.decoder.layers.7.self_attn.q_proj": 0.11805987363340209,
      "model.decoder.layers.7.self_attn.v_proj": 0.13589983071120332,
      "model.decoder.layers.8.fc1": 0.1621567160165189,
      "model.decoder.layers.8.fc2": 0.19739410485996944,
      "model.decoder.layers.8.self_attn.k_proj": 0.11815204297682885,
      "model.decoder.layers.8.self_attn.out_proj": 0.1935528372868991,
      "model.decoder.layers.8.self_attn.q_proj": 0.12386145173705759,
      "model.decoder.layers.8.self_attn.v_proj": 0.13890047395341676,
      "model.decoder.layers.9.fc1": 0.17368346144112592,
      "model.decoder.layers.9.fc2": 0.19608611881802376,
      "model.decoder.layers.9.self_attn.k_proj": 0.13347769901357598,
      "model.decoder.layers.9.self_attn.out_proj": 0.19889743410596947,
      "model.decoder.layers.9.self_attn.q_proj": 0.14675855785131325,
      "model.decoder.layers.9.self_attn.v_proj": 0.14193750860639623
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
      "layer": "model.decoder.layers.9.fc1",
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
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999755859375,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.984375
    },
    {
      "auroc": 0.9992218017578125,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 0.98828125
    },
    {
      "auroc": 0.9985198974609375,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.953125,
      "tpr_at_1pct_fpr": 0.96875
    },
    {
      "auroc": 0.9960479736328125,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.921875,
      "tpr_at_1pct_fpr": 0.921875
    },
    {
      "auroc": 0.9932098388671875,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.75,
      "tpr_at_1pct_fpr": 0.83203125
    },
    {
      "auroc": 0.9926910400390625,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.8359375,
      "tpr_at_1pct_fpr": 0.87890625
    },
    {
      "auroc": 0.9889678955078125,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.44921875,
      "tpr_at_1pct_fpr": 0.703125
    },
    {
      "auroc": 0.9865570068359375,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.61328125,
      "tpr_at_1pct_fpr": 0.73828125
    },
    {
      "auroc": 0.9862823486328125,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.671875,
      "tpr_at_1pct_fpr": 0.796875
    },
    {
      "auroc": 0.9844512939453125,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.515625,
      "tpr_at_1pct_fpr": 0.7265625
    },
    {
      "auroc": 0.983795166015625,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.52734375,
      "tpr_at_1pct_fpr": 0.68359375
    },
    {
      "auroc": 0.983062744140625,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.49609375,
      "tpr_at_1pct_fpr": 0.734375
    },
    {
      "auroc": 0.9828948974609375,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.78125,
      "tpr_at_1pct_fpr": 0.80859375
    },
    {
      "auroc": 0.9827728271484375,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.70703125,
      "tpr_at_1pct_fpr": 0.78515625
    },
    {
      "auroc": 0.9824066162109375,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.5546875,
      "tpr_at_1pct_fpr": 0.75
    },
    {
      "auroc": 0.9823760986328125,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.5546875,
      "tpr_at_1pct_fpr": 0.734375
    },
    {
      "auroc": 0.981109619140625,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.50390625,
      "tpr_at_1pct_fpr": 0.74609375
    },
    {
      "auroc": 0.9801025390625,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.484375,
      "tpr_at_1pct_fpr": 0.703125
    },
    {
      "auroc": 0.9795989990234375,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.5546875,
      "tpr_at_1pct_fpr": 0.65625
    },
    {
      "auroc": 0.9792938232421875,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.359375,
      "tpr_at_1pct_fpr": 0.6796875
    },
    {
      "auroc": 0.97796630859375,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.40625,
      "tpr_at_1pct_fpr": 0.65625
    },
    {
      "auroc": 0.977508544921875,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.625,
      "tpr_at_1pct_fpr": 0.734375
    },
    {
      "auroc": 0.974761962890625,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.19140625,
      "tpr_at_1pct_fpr": 0.70703125
    },
    {
      "auroc": 0.973175048828125,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.3515625,
      "tpr_at_1pct_fpr": 0.52734375
    },
    {
      "auroc": 0.970703125,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.63671875,
      "tpr_at_1pct_fpr": 0.68359375
    },
    {
      "auroc": 0.9690704345703125,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.19921875,
      "tpr_at_1pct_fpr": 0.58984375
    },
    {
      "auroc": 0.968170166015625,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.58203125,
      "tpr_at_1pct_fpr": 0.58203125
    },
    {
      "auroc": 0.964874267578125,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.3046875,
      "tpr_at_1pct_fpr": 0.5078125
    },
    {
      "auroc": 0.9638671875,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.4375,
      "tpr_at_1pct_fpr": 0.53125
    },
    {
      "auroc": 0.963653564453125,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.37890625,
      "tpr_at_1pct_fpr": 0.5390625
    },
    {
      "auroc": 0.9635162353515625,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.1953125,
      "tpr_at_1pct_fpr": 0.640625
    },
    {
      "auroc": 0.95989990234375,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.359375,
      "tpr_at_1pct_fpr": 0.5078125
    },
    {
      "auroc": 0.958953857421875,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.3359375,
      "tpr_at_1pct_fpr": 0.43359375
    },
    {
      "auroc": 0.9562835693359375,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.50390625,
      "tpr_at_1pct_fpr": 0.53515625
    },
    {
      "auroc": 0.9547576904296875,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.46875,
      "tpr_at_1pct_fpr": 0.53125
    },
    {
      "auroc": 0.9543609619140625,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.39453125,
      "tpr_at_1pct_fpr": 0.484375
    },
    {
      "auroc": 0.9529876708984375,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.16796875,
      "tpr_at_1pct_fpr": 0.40625
    },
    {
      "auroc": 0.9516448974609375,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.390625,
      "tpr_at_1pct_fpr": 0.5625
    },
    {
      "auroc": 0.950042724609375,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.35546875,
      "tpr_at_1pct_fpr": 0.4609375
    },
    {
      "auroc": 0.935791015625,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.3203125,
      "tpr_at_1pct_fpr": 0.41796875
    },
    {
      "auroc": 0.9245147705078125,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.42578125,
      "tpr_at_1pct_fpr": 0.4765625
    },
    {
      "auroc": 0.914031982421875,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.34375,
      "tpr_at_1pct_fpr": 0.4375
    },
    {
      "auroc": 0.9139251708984375,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.15625,
      "tpr_at_1pct_fpr": 0.21484375
    },
    {
      "auroc": 0.9060211181640625,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.2734375,
      "tpr_at_1pct_fpr": 0.3203125
    },
    {
      "auroc": 0.8756866455078125,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.15234375,
      "tpr_at_1pct_fpr": 0.22265625
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
      "auroc": 0.5473785400390625,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_kl": {
      "auroc": 0.480255126953125,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    "output_logit_mse": {
      "auroc": 0.4473724365234375,
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    "output_logprob": {
      "auroc": 0.5044708251953125,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    "output_logprob_gap": {
      "auroc": 0.5044708251953125,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    }
  },
  "model": "facebook/opt-125m",
  "model_revision": null,
  "output_combination": {
    "coefficients": {
      "output_kl": 0.41709000997328544,
      "output_logit_mse": -0.13449185352143636,
      "output_logprob": -0.10981849080148769,
      "output_logprob_gap": -0.10981849080148769
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 1.0,
    "shadow_split_auroc": 0.5766448974609375
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
      "lower_quartile": 0.453125,
      "maximum": 0.8125,
      "median": 0.546875,
      "minimum": 0.265625,
      "targets_above_chance": 19,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.64453125
    },
    "output_kl": {
      "lower_quartile": 0.40234375,
      "maximum": 0.828125,
      "median": 0.484375,
      "minimum": 0.140625,
      "targets_above_chance": 13,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.56640625
    },
    "output_logit_mse": {
      "lower_quartile": 0.35546875,
      "maximum": 0.734375,
      "median": 0.484375,
      "minimum": 0.03125,
      "targets_above_chance": 12,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.58203125
    },
    "output_logprob": {
      "lower_quartile": 0.421875,
      "maximum": 0.78125,
      "median": 0.46875,
      "minimum": 0.1875,
      "targets_above_chance": 12,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.58203125
    },
    "output_logprob_gap": {
      "lower_quartile": 0.421875,
      "maximum": 0.78125,
      "median": 0.46875,
      "minimum": 0.1875,
      "targets_above_chance": 12,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.58203125
    }
  },
  "population_sha256": "421b3f7e23eeb2c29902b6b4a8164056c2dd6235c946391567b4b27813b88fbc",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "distribution": {
      "concentration": 50.0,
      "nonce_length": 0,
      "topic_size": 512,
      "vocabulary_size": 512
    },
    "pool_sha256": "9fb02163a89f00a6984cedf027a45a71cd45b09bfee8dda7087b5d9fc92a3307",
    "seed": 20260912,
    "source": "synthetic"
  },
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.010490781819621348,
    "base_mean_logprob": -11.230236232280731,
    "base_perplexity": 75375.3993567455,
    "mean_logprob_change": -0.100726418197155,
    "perplexity_ratio_quantized_over_base": 1.1059740260022948,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -11.330962650477886,
    "quantized_perplexity": 83363.23388811061,
    "reference_decisions": 768
  },
  "selected_artifact_feature": "artifact_reconstruction",
  "selected_output_baseline": "output_combination",
  "sequence_length": 512,
  "shadow_artifacts": 32,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 2,
        "test_fpr": 0.0078125,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -2.881886194559363
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.01171875,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -0.9249530547280951
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 6,
        "test_fpr": 0.0234375,
        "test_tpr": 0.0078125,
        "test_true_positives": 2,
        "threshold": 2.1239243321229293
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 9,
        "test_fpr": 0.03515625,
        "test_tpr": 0.0078125,
        "test_true_positives": 2,
        "threshold": 2.0523043615199006
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 9,
        "test_fpr": 0.03515625,
        "test_tpr": 0.015625,
        "test_true_positives": 4,
        "threshold": 2.1124518728027137
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.02734375,
        "test_tpr": 0.02734375,
        "test_true_positives": 7,
        "threshold": 2.0432059075202416
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.02734375,
        "test_tpr": 0.02734375,
        "test_true_positives": 7,
        "threshold": 2.0432059075202416
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
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.6064453125,
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    "output_kl": {
      "auroc": 0.601470947265625,
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.017578125
    },
    "output_logit_mse": {
      "auroc": 0.5985031127929688,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.015625
    },
    "output_logprob": {
      "auroc": 0.6000328063964844,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.02734375
    },
    "output_logprob_gap": {
      "auroc": 0.6000328063964844,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.02734375
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
