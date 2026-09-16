# CalibTrace named-library attack report

Library `llm-compressor` 0.13.0 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 32 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 1.0000 | 1.0000 | 1.0000 |
| artifact_layer_combination | 1.0000 | 1.0000 | 1.0000 |
| output_logit_mse | 0.7149 | 0.0312 | 0.0195 |
| output_kl | 0.8109 | 0.1719 | 0.0898 |
| output_logprob | 0.5672 | 0.0078 | 0.0078 |
| output_logprob_gap | 0.5672 | 0.0078 | 0.0078 |
| output_combination | 0.8112 | 0.1680 | 0.0898 |

Selected artifact feature `artifact_reconstruction` minus selected output baseline `output_combination`: 0.1888 AUROC, crossed-bootstrap 95% interval [0.1319, 0.2489]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 768 calibration-excluded reference scores, mean token log probability changes by -0.045085; the corresponding perplexity ratio is 1.046117.

## Generation runtime

The 48 quantize-and-score jobs took 49.5 minutes in aggregate, with mean 61.9 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.0.fc1 | 1.0000 | 1.0000 |
| model.decoder.layers.0.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.0.self_attn.k_proj | 1.0000 | 1.0000 |
| model.decoder.layers.0.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.0.self_attn.q_proj | 1.0000 | 1.0000 |
| model.decoder.layers.0.self_attn.v_proj | 1.0000 | 1.0000 |
| model.decoder.layers.1.fc1 | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.k_proj | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.q_proj | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.v_proj | 1.0000 | 1.0000 |
| model.decoder.layers.10.fc1 | 1.0000 | 1.0000 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.9957 | 0.9023 |
| artifact_layer_combination | 1.0000 | 1.0000 |
| selected_artifact | 1.0000 | 1.0000 |
| selected_output | 0.6948 | 0.0469 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": 0.188751220703125,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.30523681640625,
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
      "artifact_minus_selected_output_auroc": {
        "lower_95": 0.22583879043214117,
        "upper_95": 0.3872817090214216
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.9866846774476199,
          "upper_95": 0.9998783093003738
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.7728883343730506,
          "upper_95": 0.9907973746683424
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.7992083445571817,
          "upper_95": 1.0
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.5861920495243597,
          "upper_95": 0.747131278972301
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.09719747202652297
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.004162901606425703,
          "upper_95": 0.13516584766584763
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.6127182909785783,
          "upper_95": 0.7741612095678588
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0037174721189591076,
          "upper_95": 0.1221491035652657
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.011524725274725277,
          "upper_95": 0.14059675232438007
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.5432300135548471,
          "upper_95": 0.7077203520505981
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.12110988451086956
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.17329216904527553
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4413439236801786,
          "upper_95": 0.5837435000143053
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.05225397403227762
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.07259539732494098
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.4579599177235869,
          "upper_95": 0.5900312371236284
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.033460370082672136
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.046511627906976744
        }
      },
      "selected_artifact": {
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
      "selected_output": {
        "auroc": {
          "lower_95": 0.6127182909785783,
          "upper_95": 0.7741612095678588
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0037174721189591076,
          "upper_95": 0.1221491035652657
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.011524725274725277,
          "upper_95": 0.14059675232438007
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 1.0,
        "tpr_at_0_1pct_fpr": 1.0,
        "tpr_at_1pct_fpr": 1.0
      },
      "artifact_reconstruction": {
        "auroc": 0.9957275390625,
        "tpr_at_0_1pct_fpr": 0.8671875,
        "tpr_at_1pct_fpr": 0.90234375
      },
      "output_combination": {
        "auroc": 0.668609619140625,
        "tpr_at_0_1pct_fpr": 0.01953125,
        "tpr_at_1pct_fpr": 0.0390625
      },
      "output_kl": {
        "auroc": 0.69476318359375,
        "tpr_at_0_1pct_fpr": 0.0234375,
        "tpr_at_1pct_fpr": 0.046875
      },
      "output_logit_mse": {
        "auroc": 0.62835693359375,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0078125
      },
      "output_logprob": {
        "auroc": 0.5081634521484375,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.02734375
      },
      "output_logprob_gap": {
        "auroc": 0.52398681640625,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "selected_artifact": {
        "auroc": 1.0,
        "tpr_at_0_1pct_fpr": 1.0,
        "tpr_at_1pct_fpr": 1.0
      },
      "selected_output": {
        "auroc": 0.69476318359375,
        "tpr_at_0_1pct_fpr": 0.0234375,
        "tpr_at_1pct_fpr": 0.046875
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20260903,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          22,
          29,
          9,
          5,
          20,
          12,
          8,
          26,
          31,
          23,
          3,
          27,
          25,
          6,
          4,
          10
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.7203690127077224,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_kl",
        "training_candidates": [
          0,
          1,
          2,
          7,
          11,
          13,
          14,
          15,
          16,
          17,
          18,
          19,
          21,
          24,
          28,
          30
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          16,
          2,
          18,
          30,
          1,
          24,
          11,
          7,
          13,
          0,
          21,
          19,
          17,
          15,
          28,
          14
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.6993829423264908,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_kl",
        "training_candidates": [
          3,
          4,
          5,
          6,
          8,
          9,
          10,
          12,
          20,
          22,
          23,
          25,
          26,
          27,
          29,
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
      "lower_95": 0.13194129483168412,
      "upper_95": 0.24890762617446058
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
        "lower_95": 0.7510923738255393,
        "upper_95": 0.8680587051683158
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.04147169811320755,
        "upper_95": 0.3347281078570805
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.06719367588932806,
        "upper_95": 0.4252052270061987
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.7479588991747758,
        "upper_95": 0.8682331820504363
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.04181720352966497,
        "upper_95": 0.31667045196456955
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.06591836734693877,
        "upper_95": 0.4038541666666667
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.6428237135566273,
        "upper_95": 0.7844694195202344
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.16034517818107874
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.003858818387120274,
        "upper_95": 0.1993440726357522
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.48014564884219113,
        "upper_95": 0.648588277584988
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.037196660166527375
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.04049409237379162
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.48014564884219113,
        "upper_95": 0.648588277584988
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.037196660166527375
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.04049409237379162
      }
    }
  },
  "empirical_test_fpr_resolution": 0.00390625,
  "experiment_sha256": "25cb73ae091fbd95d7658d2fc63e21c49df72234178305346df0781c8d418404",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4485622406005859,
    "null_mean": 0.4998328338623047,
    "null_upper_95": 0.5516971588134766,
    "observed_auroc": 1.0,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 48,
    "maximum_seconds": 111.55417080002371,
    "mean_seconds_per_artifact": 61.89358047500112,
    "minimum_seconds": 39.273923599976115,
    "total_seconds": 2970.891862800054
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.12196913114478221,
      "model.decoder.layers.0.fc2": 0.1452298558583691,
      "model.decoder.layers.0.self_attn.k_proj": 0.1272616826914563,
      "model.decoder.layers.0.self_attn.out_proj": 0.15310063656696296,
      "model.decoder.layers.0.self_attn.q_proj": 0.1246094446484182,
      "model.decoder.layers.0.self_attn.v_proj": 0.12413126900467251,
      "model.decoder.layers.1.fc1": 0.1278633630315062,
      "model.decoder.layers.1.fc2": 0.13636942698699472,
      "model.decoder.layers.1.self_attn.k_proj": 0.12048963200202199,
      "model.decoder.layers.1.self_attn.out_proj": 0.15203715710105614,
      "model.decoder.layers.1.self_attn.q_proj": 0.12313812036338835,
      "model.decoder.layers.1.self_attn.v_proj": 0.12918393475624018,
      "model.decoder.layers.10.fc1": 0.15654209112695586,
      "model.decoder.layers.10.fc2": 0.1716606457008571,
      "model.decoder.layers.10.self_attn.k_proj": 0.1569706580862321,
      "model.decoder.layers.10.self_attn.out_proj": 0.16573678165628392,
      "model.decoder.layers.10.self_attn.q_proj": 0.15866339922165099,
      "model.decoder.layers.10.self_attn.v_proj": 0.15103671003588787,
      "model.decoder.layers.11.fc1": 0.16967411730530205,
      "model.decoder.layers.11.fc2": 0.17502790751741978,
      "model.decoder.layers.11.self_attn.k_proj": 0.1532775549636292,
      "model.decoder.layers.11.self_attn.out_proj": 0.16889416254146924,
      "model.decoder.layers.11.self_attn.q_proj": 0.15190511779944582,
      "model.decoder.layers.11.self_attn.v_proj": 0.15874742692820537,
      "model.decoder.layers.2.fc1": 0.12601556626182603,
      "model.decoder.layers.2.fc2": 0.14575883615082333,
      "model.decoder.layers.2.self_attn.k_proj": 0.12679739789263758,
      "model.decoder.layers.2.self_attn.out_proj": 0.16615511280720865,
      "model.decoder.layers.2.self_attn.q_proj": 0.12698062240924507,
      "model.decoder.layers.2.self_attn.v_proj": 0.1276965801964283,
      "model.decoder.layers.3.fc1": 0.133194967083503,
      "model.decoder.layers.3.fc2": 0.1383492004326021,
      "model.decoder.layers.3.self_attn.k_proj": 0.12216760597646042,
      "model.decoder.layers.3.self_attn.out_proj": 0.16784854812843575,
      "model.decoder.layers.3.self_attn.q_proj": 0.11983809386775508,
      "model.decoder.layers.3.self_attn.v_proj": 0.12691626468789138,
      "model.decoder.layers.4.fc1": 0.1320588602934025,
      "model.decoder.layers.4.fc2": 0.1520407025876744,
      "model.decoder.layers.4.self_attn.k_proj": 0.12649312102594637,
      "model.decoder.layers.4.self_attn.out_proj": 0.16853856490543295,
      "model.decoder.layers.4.self_attn.q_proj": 0.1304114043023273,
      "model.decoder.layers.4.self_attn.v_proj": 0.13194519474827257,
      "model.decoder.layers.5.fc1": 0.13521790587184068,
      "model.decoder.layers.5.fc2": 0.14665584079800026,
      "model.decoder.layers.5.self_attn.k_proj": 0.13144043941377226,
      "model.decoder.layers.5.self_attn.out_proj": 0.16822603215345383,
      "model.decoder.layers.5.self_attn.q_proj": 0.130662386546953,
      "model.decoder.layers.5.self_attn.v_proj": 0.13152370549002887,
      "model.decoder.layers.6.fc1": 0.13191660331217173,
      "model.decoder.layers.6.fc2": 0.14840588201293553,
      "model.decoder.layers.6.self_attn.k_proj": 0.13468056369647025,
      "model.decoder.layers.6.self_attn.out_proj": 0.15723520502791766,
      "model.decoder.layers.6.self_attn.q_proj": 0.12899426288625393,
      "model.decoder.layers.6.self_attn.v_proj": 0.1296230124641929,
      "model.decoder.layers.7.fc1": 0.13644842607398078,
      "model.decoder.layers.7.fc2": 0.15801144414305363,
      "model.decoder.layers.7.self_attn.k_proj": 0.12498199933445421,
      "model.decoder.layers.7.self_attn.out_proj": 0.16632069909067618,
      "model.decoder.layers.7.self_attn.q_proj": 0.13449108290303374,
      "model.decoder.layers.7.self_attn.v_proj": 0.13160607925508663,
      "model.decoder.layers.8.fc1": 0.14396887807248096,
      "model.decoder.layers.8.fc2": 0.1602001159759229,
      "model.decoder.layers.8.self_attn.k_proj": 0.13995419723266078,
      "model.decoder.layers.8.self_attn.out_proj": 0.17108044743833073,
      "model.decoder.layers.8.self_attn.q_proj": 0.1360706875155416,
      "model.decoder.layers.8.self_attn.v_proj": 0.13087694622476706,
      "model.decoder.layers.9.fc1": 0.15490283409276298,
      "model.decoder.layers.9.fc2": 0.16664590860746703,
      "model.decoder.layers.9.self_attn.k_proj": 0.141681476460094,
      "model.decoder.layers.9.self_attn.out_proj": 0.1712201748402494,
      "model.decoder.layers.9.self_attn.q_proj": 0.1456611320611267,
      "model.decoder.layers.9.self_attn.v_proj": 0.14020447269631983
    },
    "regularization": 1.0,
    "shadow_split_auroc": 1.0
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
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
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
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
      "layer": "model.decoder.layers.10.self_attn.k_proj",
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
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
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
      "layer": "model.decoder.layers.11.self_attn.k_proj",
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
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.2.fc1",
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
      "layer": "model.decoder.layers.2.self_attn.k_proj",
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
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.3.fc1",
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
      "layer": "model.decoder.layers.3.self_attn.k_proj",
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
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.4.fc1",
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
      "layer": "model.decoder.layers.4.self_attn.k_proj",
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
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.5.fc1",
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
      "layer": "model.decoder.layers.5.self_attn.k_proj",
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
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.6.fc1",
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
      "layer": "model.decoder.layers.6.self_attn.k_proj",
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
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
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
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
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
      "layer": "model.decoder.layers.8.self_attn.k_proj",
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
      "layer": "model.decoder.layers.8.self_attn.q_proj",
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
      "layer": "model.decoder.layers.9.self_attn.k_proj",
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
      "auroc": 1.0,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999847412109375,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999847412109375,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999969482421875,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999542236328125,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.9996795654296875,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.91796875,
      "tpr_at_1pct_fpr": 1.0
    }
  ],
  "library": "llm-compressor",
  "library_version": "0.13.0",
  "mean_changed_weight_fraction_vs_artifact0": 0.20866176228464386,
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
      "auroc": 0.811248779296875,
      "tpr_at_0_1pct_fpr": 0.08984375,
      "tpr_at_1pct_fpr": 0.16796875
    },
    "output_kl": {
      "auroc": 0.8109283447265625,
      "tpr_at_0_1pct_fpr": 0.08984375,
      "tpr_at_1pct_fpr": 0.171875
    },
    "output_logit_mse": {
      "auroc": 0.7148590087890625,
      "tpr_at_0_1pct_fpr": 0.01953125,
      "tpr_at_1pct_fpr": 0.03125
    },
    "output_logprob": {
      "auroc": 0.5671844482421875,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    "output_logprob_gap": {
      "auroc": 0.5671844482421875,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0078125
    }
  },
  "model": "facebook/opt-125m",
  "model_revision": null,
  "output_combination": {
    "coefficients": {
      "output_kl": 1.735528450476696,
      "output_logit_mse": 0.21971801363819526,
      "output_logprob": 0.03570862475824262,
      "output_logprob_gap": 0.03570862475824262
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 1.0,
    "shadow_split_auroc": 0.8565826416015625
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
      "lower_quartile": 0.71875,
      "maximum": 0.984375,
      "median": 0.7890625,
      "minimum": 0.65625,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 8,
      "upper_quartile": 0.8828125
    },
    "output_kl": {
      "lower_quartile": 0.7109375,
      "maximum": 1.0,
      "median": 0.796875,
      "minimum": 0.59375,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 8,
      "upper_quartile": 0.87109375
    },
    "output_logit_mse": {
      "lower_quartile": 0.62890625,
      "maximum": 0.984375,
      "median": 0.703125,
      "minimum": 0.453125,
      "targets_above_chance": 30,
      "targets_at_least_0_9": 3,
      "upper_quartile": 0.84375
    },
    "output_logprob": {
      "lower_quartile": 0.484375,
      "maximum": 0.796875,
      "median": 0.6171875,
      "minimum": 0.265625,
      "targets_above_chance": 21,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6875
    },
    "output_logprob_gap": {
      "lower_quartile": 0.484375,
      "maximum": 0.796875,
      "median": 0.6171875,
      "minimum": 0.265625,
      "targets_above_chance": 21,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6875
    }
  },
  "population_sha256": "2b1907a1c6b1835128f2212f33cd00c8103e0301d17b25f69362f39b4fe4c119",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "distribution": {
      "concentration": 0.4,
      "nonce_length": 0,
      "topic_size": 96,
      "vocabulary_size": 4096
    },
    "pool_sha256": "c4ba7bb1dac6fb8e94ee76859da90ab144b065db6a60de5ae5849cd310d81f99",
    "seed": 20260902,
    "source": "synthetic"
  },
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.015943006945557545,
    "base_mean_logprob": -9.6803018450737,
    "base_perplexity": 15999.325515845434,
    "mean_logprob_change": -0.045084841549396515,
    "perplexity_ratio_quantized_over_base": 1.0461166102978705,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -9.725386686623096,
    "quantized_perplexity": 16737.160175688456,
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
        "test_false_positives": 1,
        "test_fpr": 0.00390625,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -2.8210246628379996
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
        "threshold": -2.0752297182094237
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 5,
        "test_fpr": 0.01953125,
        "test_tpr": 0.2578125,
        "test_true_positives": 66,
        "threshold": 1.4886759633153572
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.02734375,
        "test_tpr": 0.2734375,
        "test_true_positives": 70,
        "threshold": 1.45349199428791
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 4,
        "test_fpr": 0.015625,
        "test_tpr": 0.08203125,
        "test_true_positives": 21,
        "threshold": 1.5940311339899256
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 4,
        "test_fpr": 0.015625,
        "test_tpr": 0.0078125,
        "test_true_positives": 2,
        "threshold": 2.235951787271849
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 4,
        "test_fpr": 0.015625,
        "test_tpr": 0.0078125,
        "test_true_positives": 2,
        "threshold": 2.235951787271849
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
      "auroc": 0.8622817993164062,
      "tpr_at_0_1pct_fpr": 0.14453125,
      "tpr_at_1pct_fpr": 0.208984375
    },
    "output_kl": {
      "auroc": 0.8615264892578125,
      "tpr_at_0_1pct_fpr": 0.154296875,
      "tpr_at_1pct_fpr": 0.22265625
    },
    "output_logit_mse": {
      "auroc": 0.744140625,
      "tpr_at_0_1pct_fpr": 0.021484375,
      "tpr_at_1pct_fpr": 0.07421875
    },
    "output_logprob": {
      "auroc": 0.6022758483886719,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    "output_logprob_gap": {
      "auroc": 0.6022758483886719,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
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
