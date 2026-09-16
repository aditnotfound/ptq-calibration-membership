# CalibTrace named-library attack report

Library `llm-compressor` 0.13.0 quantizes `EleutherAI/pythia-1.4b` to W4A16 from 32 shadow and 32 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 64 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.9995 | 1.0000 | 0.8633 |
| artifact_layer_combination | 0.9999 | 1.0000 | 0.9805 |
| output_logit_mse | 0.8422 | 0.1963 | 0.0986 |
| output_kl | 0.7831 | 0.1055 | 0.0107 |
| output_logprob | 0.5409 | 0.0107 | 0.0020 |
| output_logprob_gap | 0.5409 | 0.0107 | 0.0020 |
| output_combination | 0.8616 | 0.2559 | 0.1797 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_combination`: 0.1383 AUROC, crossed-bootstrap 95% interval [0.1089, 0.1691]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 1024 calibration-excluded reference scores, mean token log probability changes by -0.027084; the corresponding perplexity ratio is 1.027454.

## Generation runtime

The 64 quantize-and-score jobs took 255.9 minutes in aggregate, with mean 239.9 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| gpt_neox.layers.0.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.1.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.12.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.17.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.2.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.3.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.6.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.8.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.9.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.10.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.11.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.8.mlp.dense_4h_to_h | 1.0000 | 1.0000 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.7104 | 0.1484 |
| artifact_layer_combination | 1.0000 | 1.0000 |
| selected_artifact | 1.0000 | 1.0000 |
| selected_output | 0.6260 | 0.0322 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": 0.13832569122314453,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.3739585876464844,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.9998111161569865,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9687745123113767,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9920632950300279,
          "upper_95": 1.0
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": 0.3273947017164163,
        "upper_95": 0.41608315735749474
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.6692999943031018,
          "upper_95": 0.7663419857952594
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.029576436222005842,
          "upper_95": 0.3020040326995364
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0662032461269157,
          "upper_95": 0.32914813511262686
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.5839161750698472,
          "upper_95": 0.6725869875774081
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.001891792254631542,
          "upper_95": 0.03400737141444785
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.010421500499132576,
          "upper_95": 0.06633980956279359
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.5593115536514183,
          "upper_95": 0.6406928978709427
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.02992660033271721
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.008019356797129881,
          "upper_95": 0.054028168640152925
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.5425263789985747,
          "upper_95": 0.6267388414038695
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0029001807249980217,
          "upper_95": 0.05460396332196291
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.018302674935928017,
          "upper_95": 0.09992249099838639
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4688099682098093,
          "upper_95": 0.5421270487822688
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.012352688474471442
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.001966471843238064,
          "upper_95": 0.028137087632781346
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.5044007666788616,
          "upper_95": 0.5870681827473202
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.017070274184824947
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0019776592381167855,
          "upper_95": 0.041502071665115145
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.9998111161569865,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9687745123113767,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9920632950300279,
          "upper_95": 1.0
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.5839161750698472,
          "upper_95": 0.6725869875774081
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.001891792254631542,
          "upper_95": 0.03400737141444785
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.010421500499132576,
          "upper_95": 0.06633980956279359
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.9999732971191406,
        "tpr_at_0_1pct_fpr": 0.9931640625,
        "tpr_at_1pct_fpr": 1.0
      },
      "artifact_reconstruction": {
        "auroc": 0.7104101181030273,
        "tpr_at_0_1pct_fpr": 0.0693359375,
        "tpr_at_1pct_fpr": 0.1484375
      },
      "output_combination": {
        "auroc": 0.6260147094726562,
        "tpr_at_0_1pct_fpr": 0.0087890625,
        "tpr_at_1pct_fpr": 0.0322265625
      },
      "output_kl": {
        "auroc": 0.5979824066162109,
        "tpr_at_0_1pct_fpr": 0.0107421875,
        "tpr_at_1pct_fpr": 0.01953125
      },
      "output_logit_mse": {
        "auroc": 0.5811805725097656,
        "tpr_at_0_1pct_fpr": 0.01953125,
        "tpr_at_1pct_fpr": 0.0439453125
      },
      "output_logprob": {
        "auroc": 0.5034694671630859,
        "tpr_at_0_1pct_fpr": 0.0029296875,
        "tpr_at_1pct_fpr": 0.0107421875
      },
      "output_logprob_gap": {
        "auroc": 0.5429153442382812,
        "tpr_at_0_1pct_fpr": 0.0048828125,
        "tpr_at_1pct_fpr": 0.0146484375
      },
      "selected_artifact": {
        "auroc": 0.9999732971191406,
        "tpr_at_0_1pct_fpr": 0.9931640625,
        "tpr_at_1pct_fpr": 1.0
      },
      "selected_output": {
        "auroc": 0.6260147094726562,
        "tpr_at_0_1pct_fpr": 0.0087890625,
        "tpr_at_1pct_fpr": 0.0322265625
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20261103,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          10,
          8,
          36,
          7,
          5,
          13,
          52,
          58,
          30,
          54,
          2,
          32,
          29,
          23,
          55,
          47,
          48,
          60,
          50,
          37,
          40,
          38,
          59,
          43,
          56,
          4,
          14,
          15,
          21,
          0,
          26,
          9
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 0.1,
        "output_validation_auroc": 0.6162597156687586,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
        "training_candidates": [
          1,
          3,
          6,
          11,
          12,
          16,
          17,
          18,
          19,
          20,
          22,
          24,
          25,
          27,
          28,
          31,
          33,
          34,
          35,
          39,
          41,
          42,
          44,
          45,
          46,
          49,
          51,
          53,
          57,
          61,
          62,
          63
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          11,
          46,
          18,
          16,
          28,
          39,
          31,
          51,
          61,
          27,
          44,
          53,
          63,
          17,
          6,
          41,
          24,
          62,
          25,
          22,
          1,
          42,
          20,
          35,
          3,
          49,
          33,
          45,
          57,
          12,
          34,
          19
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.6252538671797456,
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
          13,
          14,
          15,
          21,
          23,
          26,
          29,
          30,
          32,
          36,
          37,
          38,
          40,
          43,
          47,
          48,
          50,
          52,
          54,
          55,
          56,
          58,
          59,
          60
        ]
      }
    ]
  },
  "cluster_bootstrap": {
    "artifact_layer_combination": {
      "auroc": {
        "lower_95": 0.9996730189139487,
        "upper_95": 1.0
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.9385879833321694,
        "upper_95": 1.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.9922004221599363,
        "upper_95": 1.0
      }
    },
    "artifact_minus_output_combination_auroc": {
      "lower_95": 0.10888669027029371,
      "upper_95": 0.1691437612388963
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.9977971068079903,
        "upper_95": 1.0
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.6825358632384619,
        "upper_95": 1.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.9158121330724069,
        "upper_95": 1.0
      }
    },
    "output_combination": {
      "auroc": {
        "lower_95": 0.8308562387611037,
        "upper_95": 0.8910974137695613
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.02728321124250678,
        "upper_95": 0.2693147000816782
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.15512807626533176,
        "upper_95": 0.3437549008625518
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.7500644293963471,
        "upper_95": 0.8155125704917852
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.09267714966612761
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.010988463181882924,
        "upper_95": 0.20709782283364178
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.8072814392096931,
        "upper_95": 0.8763236778163954
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.06347618689903846,
        "upper_95": 0.2097612185594512
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.10200618987451478,
        "upper_95": 0.34163752627107274
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.4963043171785084,
        "upper_95": 0.5830646768650416
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.014509241768196788
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0009642737481240307,
        "upper_95": 0.03779529732116573
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.4963043171785084,
        "upper_95": 0.5830646768650416
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.014509241768196788
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0009642737481240307,
        "upper_95": 0.03779529732116573
      }
    }
  },
  "empirical_test_fpr_resolution": 0.0009765625,
  "experiment_sha256": "047187fa82d3aad2bb322ac6341ddb1419ec02aa555a94d0821539b2daf72758",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4745925426483154,
    "null_mean": 0.49987481393814087,
    "null_upper_95": 0.5254814624786377,
    "observed_auroc": 0.9999427795410156,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 64,
    "maximum_seconds": 556.1722156000324,
    "mean_seconds_per_artifact": 239.9103596234363,
    "minimum_seconds": 183.12786580005195,
    "total_seconds": 15354.263015899924
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "gpt_neox.layers.0.attention.dense": 0.1840443312917393,
      "gpt_neox.layers.0.attention.query_key_value": 0.1312406214870478,
      "gpt_neox.layers.0.mlp.dense_4h_to_h": 0.1842465302988411,
      "gpt_neox.layers.0.mlp.dense_h_to_4h": 0.13067300376093896,
      "gpt_neox.layers.1.attention.dense": 0.11779971181739157,
      "gpt_neox.layers.1.attention.query_key_value": 0.08325953813773913,
      "gpt_neox.layers.1.mlp.dense_4h_to_h": 0.21924497725652609,
      "gpt_neox.layers.1.mlp.dense_h_to_4h": 0.09101923176911747,
      "gpt_neox.layers.10.attention.dense": 0.22138216402614666,
      "gpt_neox.layers.10.attention.query_key_value": 0.03418529482162386,
      "gpt_neox.layers.10.mlp.dense_4h_to_h": 0.218203835411304,
      "gpt_neox.layers.10.mlp.dense_h_to_4h": 0.03397132545918606,
      "gpt_neox.layers.11.attention.dense": 0.20498944875267103,
      "gpt_neox.layers.11.attention.query_key_value": 0.05079133583268764,
      "gpt_neox.layers.11.mlp.dense_4h_to_h": 0.2277629403484184,
      "gpt_neox.layers.11.mlp.dense_h_to_4h": 0.04936627462854232,
      "gpt_neox.layers.12.attention.dense": 0.22531837710282318,
      "gpt_neox.layers.12.attention.query_key_value": 0.058293536894777336,
      "gpt_neox.layers.12.mlp.dense_4h_to_h": 0.2216280136418919,
      "gpt_neox.layers.12.mlp.dense_h_to_4h": 0.06576722729442114,
      "gpt_neox.layers.13.attention.dense": 0.24373353437625547,
      "gpt_neox.layers.13.attention.query_key_value": 0.06304057449491153,
      "gpt_neox.layers.13.mlp.dense_4h_to_h": 0.22164370456200044,
      "gpt_neox.layers.13.mlp.dense_h_to_4h": 0.06828484143296053,
      "gpt_neox.layers.14.attention.dense": 0.20150894374927705,
      "gpt_neox.layers.14.attention.query_key_value": 0.07059388715406824,
      "gpt_neox.layers.14.mlp.dense_4h_to_h": 0.21992464188962393,
      "gpt_neox.layers.14.mlp.dense_h_to_4h": 0.05991287179291575,
      "gpt_neox.layers.15.attention.dense": 0.1929962103859801,
      "gpt_neox.layers.15.attention.query_key_value": 0.053270168797254464,
      "gpt_neox.layers.15.mlp.dense_4h_to_h": 0.20813356623966855,
      "gpt_neox.layers.15.mlp.dense_h_to_4h": 0.05383218347676817,
      "gpt_neox.layers.16.attention.dense": 0.17206597367790732,
      "gpt_neox.layers.16.attention.query_key_value": 0.05139227982142044,
      "gpt_neox.layers.16.mlp.dense_4h_to_h": 0.19939378188781684,
      "gpt_neox.layers.16.mlp.dense_h_to_4h": 0.043465563918278174,
      "gpt_neox.layers.17.attention.dense": 0.22128641407377814,
      "gpt_neox.layers.17.attention.query_key_value": 0.04309991657627575,
      "gpt_neox.layers.17.mlp.dense_4h_to_h": 0.19667988638918277,
      "gpt_neox.layers.17.mlp.dense_h_to_4h": 0.04323178886005159,
      "gpt_neox.layers.18.attention.dense": 0.16619671702213754,
      "gpt_neox.layers.18.attention.query_key_value": 0.037075410814753844,
      "gpt_neox.layers.18.mlp.dense_4h_to_h": 0.19498518468266532,
      "gpt_neox.layers.18.mlp.dense_h_to_4h": 0.03796306176721484,
      "gpt_neox.layers.19.attention.dense": 0.15127803963072867,
      "gpt_neox.layers.19.attention.query_key_value": 0.03487296843636885,
      "gpt_neox.layers.19.mlp.dense_4h_to_h": 0.196175230658407,
      "gpt_neox.layers.19.mlp.dense_h_to_4h": 0.04127751242012554,
      "gpt_neox.layers.2.attention.dense": 0.12453930259094104,
      "gpt_neox.layers.2.attention.query_key_value": 0.05966883609754895,
      "gpt_neox.layers.2.mlp.dense_4h_to_h": 0.2382452144960794,
      "gpt_neox.layers.2.mlp.dense_h_to_4h": 0.059044661791850965,
      "gpt_neox.layers.20.attention.dense": 0.18479688165747102,
      "gpt_neox.layers.20.attention.query_key_value": 0.036081450459901306,
      "gpt_neox.layers.20.mlp.dense_4h_to_h": 0.1988895917434676,
      "gpt_neox.layers.20.mlp.dense_h_to_4h": 0.03835574977956503,
      "gpt_neox.layers.21.attention.dense": 0.1880885482618332,
      "gpt_neox.layers.21.attention.query_key_value": 0.024923793195789357,
      "gpt_neox.layers.21.mlp.dense_4h_to_h": 0.20187247973178213,
      "gpt_neox.layers.21.mlp.dense_h_to_4h": 0.04193811662046991,
      "gpt_neox.layers.22.attention.dense": 0.20961553125085863,
      "gpt_neox.layers.22.attention.query_key_value": 0.04342016451549489,
      "gpt_neox.layers.22.mlp.dense_4h_to_h": 0.19780374910395906,
      "gpt_neox.layers.22.mlp.dense_h_to_4h": 0.046630085038332866,
      "gpt_neox.layers.23.attention.dense": 0.14384017112988207,
      "gpt_neox.layers.23.attention.query_key_value": 0.04939756972722472,
      "gpt_neox.layers.23.mlp.dense_4h_to_h": 0.18593723455362668,
      "gpt_neox.layers.23.mlp.dense_h_to_4h": 0.04656839816828699,
      "gpt_neox.layers.3.attention.dense": 0.16053079518655267,
      "gpt_neox.layers.3.attention.query_key_value": 0.03687232007388213,
      "gpt_neox.layers.3.mlp.dense_4h_to_h": 0.23278691416208186,
      "gpt_neox.layers.3.mlp.dense_h_to_4h": 0.04026957825085072,
      "gpt_neox.layers.4.attention.dense": 0.16751909639237317,
      "gpt_neox.layers.4.attention.query_key_value": 0.031127160017129993,
      "gpt_neox.layers.4.mlp.dense_4h_to_h": 0.23504689939858037,
      "gpt_neox.layers.4.mlp.dense_h_to_4h": 0.02766824786420259,
      "gpt_neox.layers.5.attention.dense": 0.14991087722760196,
      "gpt_neox.layers.5.attention.query_key_value": 0.018735926009788597,
      "gpt_neox.layers.5.mlp.dense_4h_to_h": 0.22249393712601592,
      "gpt_neox.layers.5.mlp.dense_h_to_4h": 0.021216039775860274,
      "gpt_neox.layers.6.attention.dense": 0.15551536736411736,
      "gpt_neox.layers.6.attention.query_key_value": 0.01482161560411499,
      "gpt_neox.layers.6.mlp.dense_4h_to_h": 0.21684278142994723,
      "gpt_neox.layers.6.mlp.dense_h_to_4h": 0.011095806728283628,
      "gpt_neox.layers.7.attention.dense": 0.16225058106986215,
      "gpt_neox.layers.7.attention.query_key_value": 0.004216375850595318,
      "gpt_neox.layers.7.mlp.dense_4h_to_h": 0.21952804691110148,
      "gpt_neox.layers.7.mlp.dense_h_to_4h": 0.004498257780148753,
      "gpt_neox.layers.8.attention.dense": 0.1610657718308719,
      "gpt_neox.layers.8.attention.query_key_value": 0.011702123265329881,
      "gpt_neox.layers.8.mlp.dense_4h_to_h": 0.21107436957108383,
      "gpt_neox.layers.8.mlp.dense_h_to_4h": 0.010351195260777726,
      "gpt_neox.layers.9.attention.dense": 0.20504707952386528,
      "gpt_neox.layers.9.attention.query_key_value": 0.023314983175466396,
      "gpt_neox.layers.9.mlp.dense_4h_to_h": 0.22430144086407597,
      "gpt_neox.layers.9.mlp.dense_h_to_4h": 0.02383073831934797
    },
    "regularization": 1.0,
    "shadow_split_auroc": 1.0
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.0.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.1.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.12.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.17.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.2.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.3.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.6.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999990463256836,
      "layer": "gpt_neox.layers.8.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999990463256836,
      "layer": "gpt_neox.layers.9.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999995231628418,
      "layer": "gpt_neox.layers.10.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999914169311523,
      "layer": "gpt_neox.layers.11.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9970703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999895095825195,
      "layer": "gpt_neox.layers.8.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9990234375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999866485595703,
      "layer": "gpt_neox.layers.11.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9990234375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999866485595703,
      "layer": "gpt_neox.layers.13.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999856948852539,
      "layer": "gpt_neox.layers.7.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999818801879883,
      "layer": "gpt_neox.layers.6.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9990234375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999809265136719,
      "layer": "gpt_neox.layers.12.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9970703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999809265136719,
      "layer": "gpt_neox.layers.5.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9951171875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999771118164062,
      "layer": "gpt_neox.layers.10.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9912109375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999761581420898,
      "layer": "gpt_neox.layers.14.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999752044677734,
      "layer": "gpt_neox.layers.15.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9912109375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999713897705078,
      "layer": "gpt_neox.layers.1.attention.dense",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999656677246094,
      "layer": "gpt_neox.layers.4.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.990234375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999628067016602,
      "layer": "gpt_neox.layers.15.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9814453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999570846557617,
      "layer": "gpt_neox.layers.5.attention.dense",
      "tpr_at_0_1pct_fpr": 0.98046875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999427795410156,
      "layer": "gpt_neox.layers.2.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9775390625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999275207519531,
      "layer": "gpt_neox.layers.4.attention.dense",
      "tpr_at_0_1pct_fpr": 0.978515625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999170303344727,
      "layer": "gpt_neox.layers.16.attention.dense",
      "tpr_at_0_1pct_fpr": 0.98046875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999122619628906,
      "layer": "gpt_neox.layers.7.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9794921875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999103546142578,
      "layer": "gpt_neox.layers.16.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.96484375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999055862426758,
      "layer": "gpt_neox.layers.21.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9736328125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998970031738281,
      "layer": "gpt_neox.layers.18.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9521484375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998922348022461,
      "layer": "gpt_neox.layers.9.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9716796875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998836517333984,
      "layer": "gpt_neox.layers.20.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9658203125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998798370361328,
      "layer": "gpt_neox.layers.17.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.951171875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998741149902344,
      "layer": "gpt_neox.layers.3.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9541015625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998531341552734,
      "layer": "gpt_neox.layers.22.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9609375,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9998493194580078,
      "layer": "gpt_neox.layers.22.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9443359375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998483657836914,
      "layer": "gpt_neox.layers.18.attention.dense",
      "tpr_at_0_1pct_fpr": 0.9443359375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999842643737793,
      "layer": "gpt_neox.layers.21.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998254776000977,
      "layer": "gpt_neox.layers.0.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.95703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998178482055664,
      "layer": "gpt_neox.layers.19.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9521484375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998178482055664,
      "layer": "gpt_neox.layers.20.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9482421875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998149871826172,
      "layer": "gpt_neox.layers.13.attention.dense",
      "tpr_at_0_1pct_fpr": 0.955078125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998102188110352,
      "layer": "gpt_neox.layers.23.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9997434616088867,
      "layer": "gpt_neox.layers.23.attention.dense",
      "tpr_at_0_1pct_fpr": 0.97265625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9997138977050781,
      "layer": "gpt_neox.layers.14.attention.dense",
      "tpr_at_0_1pct_fpr": 0.912109375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996795654296875,
      "layer": "gpt_neox.layers.12.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9482421875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996786117553711,
      "layer": "gpt_neox.layers.10.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9365234375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999659538269043,
      "layer": "gpt_neox.layers.13.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9462890625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996585845947266,
      "layer": "gpt_neox.layers.13.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996347427368164,
      "layer": "gpt_neox.layers.14.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9638671875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996299743652344,
      "layer": "gpt_neox.layers.12.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996213912963867,
      "layer": "gpt_neox.layers.7.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9208984375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995994567871094,
      "layer": "gpt_neox.layers.19.attention.dense",
      "tpr_at_0_1pct_fpr": 0.8896484375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995918273925781,
      "layer": "gpt_neox.layers.11.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9072265625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995794296264648,
      "layer": "gpt_neox.layers.9.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8916015625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995746612548828,
      "layer": "gpt_neox.layers.4.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8916015625,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9995718002319336,
      "layer": "gpt_neox.layers.11.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.92578125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995632171630859,
      "layer": "gpt_neox.layers.10.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9169921875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995632171630859,
      "layer": "gpt_neox.layers.7.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.900390625,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9995565414428711,
      "layer": "gpt_neox.layers.15.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8291015625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995536804199219,
      "layer": "gpt_neox.layers.8.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.8955078125,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9995384216308594,
      "layer": "gpt_neox.layers.6.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.85546875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995336532592773,
      "layer": "gpt_neox.layers.14.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9072265625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995288848876953,
      "layer": "gpt_neox.layers.9.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.8720703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995269775390625,
      "layer": "gpt_neox.layers.3.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9111328125,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9995050430297852,
      "layer": "gpt_neox.layers.5.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.853515625,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9994926452636719,
      "layer": "gpt_neox.layers.0.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.89453125,
      "tpr_at_1pct_fpr": 0.998046875
    },
    {
      "auroc": 0.9994869232177734,
      "layer": "gpt_neox.layers.6.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.857421875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994707107543945,
      "layer": "gpt_neox.layers.0.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8916015625,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9994611740112305,
      "layer": "gpt_neox.layers.23.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.857421875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999455451965332,
      "layer": "gpt_neox.layers.23.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.77734375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994525909423828,
      "layer": "gpt_neox.layers.17.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.841796875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.99945068359375,
      "layer": "gpt_neox.layers.22.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.8095703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994497299194336,
      "layer": "gpt_neox.layers.20.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.794921875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994363784790039,
      "layer": "gpt_neox.layers.15.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.8583984375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994354248046875,
      "layer": "gpt_neox.layers.22.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8134765625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994335174560547,
      "layer": "gpt_neox.layers.19.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.7724609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994220733642578,
      "layer": "gpt_neox.layers.16.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8623046875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994211196899414,
      "layer": "gpt_neox.layers.21.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.7744140625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994163513183594,
      "layer": "gpt_neox.layers.18.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.814453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994163513183594,
      "layer": "gpt_neox.layers.20.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.79296875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994125366210938,
      "layer": "gpt_neox.layers.2.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8837890625,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9994087219238281,
      "layer": "gpt_neox.layers.16.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.806640625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9994068145751953,
      "layer": "gpt_neox.layers.8.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.7705078125,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9994029998779297,
      "layer": "gpt_neox.layers.5.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.814453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9993906021118164,
      "layer": "gpt_neox.layers.4.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.87109375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9993877410888672,
      "layer": "gpt_neox.layers.2.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.876953125,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    {
      "auroc": 0.9993619918823242,
      "layer": "gpt_neox.layers.18.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9993524551391602,
      "layer": "gpt_neox.layers.1.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8125,
      "tpr_at_1pct_fpr": 0.998046875
    },
    {
      "auroc": 0.9993524551391602,
      "layer": "gpt_neox.layers.1.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.84375,
      "tpr_at_1pct_fpr": 0.998046875
    },
    {
      "auroc": 0.9993371963500977,
      "layer": "gpt_neox.layers.19.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.78515625,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9993247985839844,
      "layer": "gpt_neox.layers.21.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.7421875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999302864074707,
      "layer": "gpt_neox.layers.17.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.771484375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9992542266845703,
      "layer": "gpt_neox.layers.3.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.87890625,
      "tpr_at_1pct_fpr": 1.0
    }
  ],
  "library": "llm-compressor",
  "library_version": "0.13.0",
  "mean_changed_weight_fraction_vs_artifact0": null,
  "method": "GPTQ",
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 0.9999427795410156,
      "tpr_at_0_1pct_fpr": 0.98046875,
      "tpr_at_1pct_fpr": 1.0
    },
    "artifact_reconstruction": {
      "auroc": 0.9995441436767578,
      "tpr_at_0_1pct_fpr": 0.86328125,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.8616170883178711,
      "tpr_at_0_1pct_fpr": 0.1796875,
      "tpr_at_1pct_fpr": 0.255859375
    },
    "output_kl": {
      "auroc": 0.7831020355224609,
      "tpr_at_0_1pct_fpr": 0.0107421875,
      "tpr_at_1pct_fpr": 0.10546875
    },
    "output_logit_mse": {
      "auroc": 0.8422470092773438,
      "tpr_at_0_1pct_fpr": 0.0986328125,
      "tpr_at_1pct_fpr": 0.1962890625
    },
    "output_logprob": {
      "auroc": 0.5408802032470703,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    "output_logprob_gap": {
      "auroc": 0.5408802032470703,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    }
  },
  "model": "EleutherAI/pythia-1.4b",
  "model_dtype": "bfloat16",
  "model_revision": "fedc38a16eea3bd36a96b906d78d11d2ce18ed79",
  "output_combination": {
    "coefficients": {
      "output_kl": 0.7479181178685346,
      "output_logit_mse": 1.3282169858446542,
      "output_logprob": 0.033321356115659194,
      "output_logprob_gap": 0.033321356115659194
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 0.1,
    "shadow_split_auroc": 0.8685436248779297
  },
  "parameters": 1414647808,
  "per_target_auroc": {
    "artifact_layer_combination": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 64,
      "upper_quartile": 1.0
    },
    "artifact_reconstruction": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 0.99609375,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 64,
      "upper_quartile": 1.0
    },
    "output_combination": {
      "lower_quartile": 0.8076171875,
      "maximum": 1.0,
      "median": 0.875,
      "minimum": 0.55859375,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 22,
      "upper_quartile": 0.9189453125
    },
    "output_kl": {
      "lower_quartile": 0.7216796875,
      "maximum": 0.96484375,
      "median": 0.787109375,
      "minimum": 0.6015625,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 5,
      "upper_quartile": 0.841796875
    },
    "output_logit_mse": {
      "lower_quartile": 0.7919921875,
      "maximum": 0.9921875,
      "median": 0.849609375,
      "minimum": 0.52734375,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 21,
      "upper_quartile": 0.921875
    },
    "output_logprob": {
      "lower_quartile": 0.4638671875,
      "maximum": 0.765625,
      "median": 0.548828125,
      "minimum": 0.3125,
      "targets_above_chance": 40,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6318359375
    },
    "output_logprob_gap": {
      "lower_quartile": 0.4638671875,
      "maximum": 0.765625,
      "median": 0.548828125,
      "minimum": 0.3125,
      "targets_above_chance": 40,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6318359375
    }
  },
  "population_sha256": "4130735375c7b856333d65b73b79077fdaa103187037221cab3f8c574c0b0870",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "document_count": 5156,
    "earliest_published": "2025-01-01T00:20:22Z",
    "identifier_sha256": "854331d12711037dc398b0f8b190ef30ba071622a9cf1040c95e07c4d7207941",
    "latest_published": "2025-12-31T15:29:01Z",
    "path": "data\\stackexchange_questions_2025.jsonl",
    "pool_sha256": "e04ffa5b1d6cd22ee38382ff0a32f8331b28570d0068e844f8745154149a8f8c",
    "queries": [
      "questions created from 2025-01-01T00:00:00Z through 2025-12-31T23:59:59Z"
    ],
    "required_published_after": "2024-12-31T23:59:59Z",
    "seed": 20261102,
    "sha256": "4171e629048848e01c68d3db6b1a836c8e3e28b12c317411e0f8a73dbdd7171f",
    "source": "text_jsonl",
    "sources": [
      "Stack Exchange API (ai)",
      "Stack Exchange API (datascience)",
      "Stack Exchange API (stackoverflow)",
      "Stack Exchange API (stats)"
    ],
    "text_field": "text"
  },
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.0033176871902180394,
    "base_mean_logprob": -2.9531740695238113,
    "base_perplexity": 19.166693699134207,
    "mean_logprob_change": -0.027083651162683964,
    "perplexity_ratio_quantized_over_base": 1.0274537468693068,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -2.9802577206864953,
    "quantized_perplexity": 19.692891256271775,
    "reference_decisions": 1024
  },
  "selected_artifact_feature": "artifact_layer_combination",
  "selected_output_baseline": "output_combination",
  "sequence_length": 512,
  "shadow_artifacts": 32,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 11,
        "test_fpr": 0.0107421875,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -1.8026894332636165
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 15,
        "test_fpr": 0.0146484375,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -0.447057888878646
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
        "test_tpr": 0.2578125,
        "test_true_positives": 264,
        "threshold": 1.3999767157603216
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 13,
        "test_fpr": 0.0126953125,
        "test_tpr": 0.1162109375,
        "test_true_positives": 119,
        "threshold": 1.7671268151872725
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 12,
        "test_fpr": 0.01171875,
        "test_tpr": 0.2294921875,
        "test_true_positives": 235,
        "threshold": 1.4066492568538123
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 36,
        "test_fpr": 0.03515625,
        "test_tpr": 0.033203125,
        "test_true_positives": 34,
        "threshold": 1.936004967124968
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 36,
        "test_fpr": 0.03515625,
        "test_tpr": 0.033203125,
        "test_true_positives": 34,
        "threshold": 1.936004967124968
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
      "auroc": 0.9999761581420898,
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.8771247863769531,
      "tpr_at_0_1pct_fpr": 0.12109375,
      "tpr_at_1pct_fpr": 0.28515625
    },
    "output_kl": {
      "auroc": 0.7990388870239258,
      "tpr_at_0_1pct_fpr": 0.044921875,
      "tpr_at_1pct_fpr": 0.1083984375
    },
    "output_logit_mse": {
      "auroc": 0.8614406585693359,
      "tpr_at_0_1pct_fpr": 0.1259765625,
      "tpr_at_1pct_fpr": 0.2626953125
    },
    "output_logprob": {
      "auroc": 0.5998458862304688,
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.0439453125
    },
    "output_logprob_gap": {
      "auroc": 0.5998458862304688,
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.0439453125
    }
  },
  "targets": 64,
  "test_artifacts": 32,
  "test_decisions": 2048,
  "test_members": 1024,
  "test_nonmembers": 1024,
  "threat_model": "public base, released llm-compressor W4 artifact, one held-out artifact"
}
```
