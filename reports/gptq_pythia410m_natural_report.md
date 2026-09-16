# CalibTrace named-library attack report

Library `llm-compressor` 0.13.0 quantizes `EleutherAI/pythia-410m` to W4A16 from 24 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 32 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 1.0000 | 1.0000 | 1.0000 |
| artifact_layer_combination | 1.0000 | 1.0000 | 1.0000 |
| output_logit_mse | 0.7442 | 0.1562 | 0.0742 |
| output_kl | 0.6317 | 0.0391 | 0.0117 |
| output_logprob | 0.5545 | 0.0117 | 0.0078 |
| output_logprob_gap | 0.5545 | 0.0117 | 0.0078 |
| output_combination | 0.7402 | 0.1289 | 0.0703 |

Selected artifact feature `artifact_reconstruction` minus selected output baseline `output_combination`: 0.2598 AUROC, crossed-bootstrap 95% interval [0.1861, 0.3326]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 640 calibration-excluded reference scores, mean token log probability changes by -0.071740; the corresponding perplexity ratio is 1.074376.

## Generation runtime

The 40 quantize-and-score jobs took 58.0 minutes in aggregate, with mean 87.0 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| gpt_neox.layers.0.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.0.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.1.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.10.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.10.attention.query_key_value | 1.0000 | 1.0000 |
| gpt_neox.layers.10.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.10.mlp.dense_h_to_4h | 1.0000 | 1.0000 |
| gpt_neox.layers.11.attention.dense | 1.0000 | 1.0000 |
| gpt_neox.layers.11.attention.query_key_value | 1.0000 | 1.0000 |
| gpt_neox.layers.11.mlp.dense_4h_to_h | 1.0000 | 1.0000 |
| gpt_neox.layers.11.mlp.dense_h_to_4h | 1.0000 | 1.0000 |
| gpt_neox.layers.12.attention.dense | 1.0000 | 1.0000 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.6096 | 0.0312 |
| artifact_layer_combination | 1.0000 | 1.0000 |
| selected_artifact | 1.0000 | 1.0000 |
| selected_output | 0.5977 | 0.0273 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": 0.2598419189453125,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.402252197265625,
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
        "lower_95": 0.32612438316118464,
        "upper_95": 0.4718558389143739
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.543354872122589,
          "upper_95": 0.690663316890111
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.016653225806451614,
          "upper_95": 0.1314818246394268
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.016653225806451614,
          "upper_95": 0.1326519819736962
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.5275864932189022,
          "upper_95": 0.6757165993048296
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0041472691697871334,
          "upper_95": 0.09230923694779117
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.011144364070699072,
          "upper_95": 0.11852912383749388
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.4762279297434837,
          "upper_95": 0.6404732104651873
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.09162066940692894
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.10678575839920942
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.5294867158608125,
          "upper_95": 0.675023561529786
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.11062078071985729
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0038450570342205325,
          "upper_95": 0.14903905691831387
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4526269212919928,
          "upper_95": 0.5757890971870229
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.04334120832448501
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.05716656787196204
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.4876959796597771,
          "upper_95": 0.6181957764603321
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.07425571152888442
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.09958585714058599
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
          "lower_95": 0.5281441610856261,
          "upper_95": 0.6738756168388154
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.004114804695405789,
          "upper_95": 0.10117719479571984
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.01185538246919321,
          "upper_95": 0.13136660754171595
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
        "auroc": 0.609588623046875,
        "tpr_at_0_1pct_fpr": 0.03125,
        "tpr_at_1pct_fpr": 0.03125
      },
      "output_combination": {
        "auroc": 0.5973663330078125,
        "tpr_at_0_1pct_fpr": 0.01953125,
        "tpr_at_1pct_fpr": 0.03125
      },
      "output_kl": {
        "auroc": 0.557373046875,
        "tpr_at_0_1pct_fpr": 0.0078125,
        "tpr_at_1pct_fpr": 0.03515625
      },
      "output_logit_mse": {
        "auroc": 0.596435546875,
        "tpr_at_0_1pct_fpr": 0.01171875,
        "tpr_at_1pct_fpr": 0.0234375
      },
      "output_logprob": {
        "auroc": 0.5111236572265625,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "output_logprob_gap": {
        "auroc": 0.5529022216796875,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0234375
      },
      "selected_artifact": {
        "auroc": 1.0,
        "tpr_at_0_1pct_fpr": 1.0,
        "tpr_at_1pct_fpr": 1.0
      },
      "selected_output": {
        "auroc": 0.597747802734375,
        "tpr_at_0_1pct_fpr": 0.015625,
        "tpr_at_1pct_fpr": 0.02734375
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20261003,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          7,
          18,
          27,
          13,
          0,
          19,
          30,
          16,
          20,
          2,
          3,
          15,
          29,
          23,
          17,
          22
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.6114369501466276,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
        "training_candidates": [
          1,
          4,
          5,
          6,
          8,
          9,
          10,
          11,
          12,
          14,
          21,
          24,
          25,
          26,
          28,
          31
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          24,
          31,
          25,
          10,
          12,
          5,
          9,
          6,
          28,
          1,
          21,
          14,
          4,
          11,
          8,
          26
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.58547844031715,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_logit_mse",
        "training_candidates": [
          0,
          2,
          3,
          7,
          13,
          15,
          16,
          17,
          18,
          19,
          20,
          22,
          23,
          27,
          29,
          30
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
      "lower_95": 0.18612800294397489,
      "upper_95": 0.3326250795051061
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
        "lower_95": 0.6673749204948939,
        "upper_95": 0.8138719970560251
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.026412611717974183,
        "upper_95": 0.21285221391604361
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.03785774410774411,
        "upper_95": 0.2720181818181818
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.5340960265903083,
        "upper_95": 0.7197139779411859
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.09958585714058599
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.15526600435417642
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.6746649417596692,
        "upper_95": 0.8087855138374623
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.03006798912174052,
        "upper_95": 0.23323692611736088
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.04503098751061755,
        "upper_95": 0.2833409090909091
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.47063447678315035,
        "upper_95": 0.6300112108629471
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.048157131011608616
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06296369203849518
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.47063447678315035,
        "upper_95": 0.6300112108629471
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.048157131011608616
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06296369203849518
      }
    }
  },
  "empirical_test_fpr_resolution": 0.00390625,
  "experiment_sha256": "8ecb849913866d3aafc3c6737178a60bdf012f9d81becd682392635946680add",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4480278015136719,
    "null_mean": 0.4996476638793945,
    "null_upper_95": 0.5512393951416016,
    "observed_auroc": 1.0,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 40,
    "maximum_seconds": 92.35321100003785,
    "mean_seconds_per_artifact": 87.01907749499951,
    "minimum_seconds": 84.39878210000461,
    "total_seconds": 3480.7630997999804
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "gpt_neox.layers.0.attention.dense": 0.12199869858080103,
      "gpt_neox.layers.0.attention.query_key_value": 0.09767338814062511,
      "gpt_neox.layers.0.mlp.dense_4h_to_h": 0.11684753277175715,
      "gpt_neox.layers.0.mlp.dense_h_to_4h": 0.09730789110012833,
      "gpt_neox.layers.1.attention.dense": 0.1157890765228592,
      "gpt_neox.layers.1.attention.query_key_value": 0.09671362623421949,
      "gpt_neox.layers.1.mlp.dense_4h_to_h": 0.12461168297091768,
      "gpt_neox.layers.1.mlp.dense_h_to_4h": 0.09668279027774256,
      "gpt_neox.layers.10.attention.dense": 0.12903658679355076,
      "gpt_neox.layers.10.attention.query_key_value": 0.1021231058977796,
      "gpt_neox.layers.10.mlp.dense_4h_to_h": 0.12846572267389636,
      "gpt_neox.layers.10.mlp.dense_h_to_4h": 0.10164337078812836,
      "gpt_neox.layers.11.attention.dense": 0.1298068171750531,
      "gpt_neox.layers.11.attention.query_key_value": 0.10280813116616065,
      "gpt_neox.layers.11.mlp.dense_4h_to_h": 0.12819486955397094,
      "gpt_neox.layers.11.mlp.dense_h_to_4h": 0.10232519481712772,
      "gpt_neox.layers.12.attention.dense": 0.1306503115498452,
      "gpt_neox.layers.12.attention.query_key_value": 0.10085366630424082,
      "gpt_neox.layers.12.mlp.dense_4h_to_h": 0.1280873346758117,
      "gpt_neox.layers.12.mlp.dense_h_to_4h": 0.10299399719301891,
      "gpt_neox.layers.13.attention.dense": 0.12679254676651505,
      "gpt_neox.layers.13.attention.query_key_value": 0.10238403917952427,
      "gpt_neox.layers.13.mlp.dense_4h_to_h": 0.12690538171143856,
      "gpt_neox.layers.13.mlp.dense_h_to_4h": 0.10201104438024998,
      "gpt_neox.layers.14.attention.dense": 0.1244401356683332,
      "gpt_neox.layers.14.attention.query_key_value": 0.09569404966148576,
      "gpt_neox.layers.14.mlp.dense_4h_to_h": 0.12810113665303915,
      "gpt_neox.layers.14.mlp.dense_h_to_4h": 0.10399568223165993,
      "gpt_neox.layers.15.attention.dense": 0.12518345436846298,
      "gpt_neox.layers.15.attention.query_key_value": 0.0960369790425305,
      "gpt_neox.layers.15.mlp.dense_4h_to_h": 0.12613264514420566,
      "gpt_neox.layers.15.mlp.dense_h_to_4h": 0.09929085595951576,
      "gpt_neox.layers.16.attention.dense": 0.12970675184472655,
      "gpt_neox.layers.16.attention.query_key_value": 0.09903419223975041,
      "gpt_neox.layers.16.mlp.dense_4h_to_h": 0.12683002958449263,
      "gpt_neox.layers.16.mlp.dense_h_to_4h": 0.09679399125714166,
      "gpt_neox.layers.17.attention.dense": 0.12708672357486564,
      "gpt_neox.layers.17.attention.query_key_value": 0.09440860287974977,
      "gpt_neox.layers.17.mlp.dense_4h_to_h": 0.12493125580412591,
      "gpt_neox.layers.17.mlp.dense_h_to_4h": 0.09840482839974525,
      "gpt_neox.layers.18.attention.dense": 0.12793975958764273,
      "gpt_neox.layers.18.attention.query_key_value": 0.10354930276238705,
      "gpt_neox.layers.18.mlp.dense_4h_to_h": 0.12502374993709714,
      "gpt_neox.layers.18.mlp.dense_h_to_4h": 0.09720589020848984,
      "gpt_neox.layers.19.attention.dense": 0.11996107369571415,
      "gpt_neox.layers.19.attention.query_key_value": 0.09330386022138806,
      "gpt_neox.layers.19.mlp.dense_4h_to_h": 0.12545245537910818,
      "gpt_neox.layers.19.mlp.dense_h_to_4h": 0.0974668995174779,
      "gpt_neox.layers.2.attention.dense": 0.11866468773666979,
      "gpt_neox.layers.2.attention.query_key_value": 0.09621938556176912,
      "gpt_neox.layers.2.mlp.dense_4h_to_h": 0.1278531478941487,
      "gpt_neox.layers.2.mlp.dense_h_to_4h": 0.09771402393127275,
      "gpt_neox.layers.20.attention.dense": 0.12394471605582384,
      "gpt_neox.layers.20.attention.query_key_value": 0.09464828883987664,
      "gpt_neox.layers.20.mlp.dense_4h_to_h": 0.12402425772633457,
      "gpt_neox.layers.20.mlp.dense_h_to_4h": 0.09615299243293485,
      "gpt_neox.layers.21.attention.dense": 0.12891669173344036,
      "gpt_neox.layers.21.attention.query_key_value": 0.1006626897376479,
      "gpt_neox.layers.21.mlp.dense_4h_to_h": 0.12324330373671054,
      "gpt_neox.layers.21.mlp.dense_h_to_4h": 0.0980802446158418,
      "gpt_neox.layers.22.attention.dense": 0.13058575714683884,
      "gpt_neox.layers.22.attention.query_key_value": 0.10392416944197137,
      "gpt_neox.layers.22.mlp.dense_4h_to_h": 0.12502945308030883,
      "gpt_neox.layers.22.mlp.dense_h_to_4h": 0.09995683346700687,
      "gpt_neox.layers.23.attention.dense": 0.12931024674551755,
      "gpt_neox.layers.23.attention.query_key_value": 0.10555411447382052,
      "gpt_neox.layers.23.mlp.dense_4h_to_h": 0.12439975603830583,
      "gpt_neox.layers.23.mlp.dense_h_to_4h": 0.10323724578282367,
      "gpt_neox.layers.3.attention.dense": 0.11963290297706194,
      "gpt_neox.layers.3.attention.query_key_value": 0.10008120632946552,
      "gpt_neox.layers.3.mlp.dense_4h_to_h": 0.12628176329517374,
      "gpt_neox.layers.3.mlp.dense_h_to_4h": 0.09987727339045636,
      "gpt_neox.layers.4.attention.dense": 0.12427657158365638,
      "gpt_neox.layers.4.attention.query_key_value": 0.09773829599548227,
      "gpt_neox.layers.4.mlp.dense_4h_to_h": 0.12665760835580034,
      "gpt_neox.layers.4.mlp.dense_h_to_4h": 0.09894060437028543,
      "gpt_neox.layers.5.attention.dense": 0.12216344365527226,
      "gpt_neox.layers.5.attention.query_key_value": 0.09655105553595607,
      "gpt_neox.layers.5.mlp.dense_4h_to_h": 0.12374336550498474,
      "gpt_neox.layers.5.mlp.dense_h_to_4h": 0.10000644033351423,
      "gpt_neox.layers.6.attention.dense": 0.12686227934882555,
      "gpt_neox.layers.6.attention.query_key_value": 0.09705431735768949,
      "gpt_neox.layers.6.mlp.dense_4h_to_h": 0.12625245909731753,
      "gpt_neox.layers.6.mlp.dense_h_to_4h": 0.0926287051540893,
      "gpt_neox.layers.7.attention.dense": 0.1286523300682893,
      "gpt_neox.layers.7.attention.query_key_value": 0.09760777811039542,
      "gpt_neox.layers.7.mlp.dense_4h_to_h": 0.12719729454390327,
      "gpt_neox.layers.7.mlp.dense_h_to_4h": 0.09790682466959104,
      "gpt_neox.layers.8.attention.dense": 0.13156375291760883,
      "gpt_neox.layers.8.attention.query_key_value": 0.09944913122082391,
      "gpt_neox.layers.8.mlp.dense_4h_to_h": 0.12822965846118073,
      "gpt_neox.layers.8.mlp.dense_h_to_4h": 0.10184966505718723,
      "gpt_neox.layers.9.attention.dense": 0.1291069185740698,
      "gpt_neox.layers.9.attention.query_key_value": 0.09884491081055809,
      "gpt_neox.layers.9.mlp.dense_4h_to_h": 0.12935163421974505,
      "gpt_neox.layers.9.mlp.dense_h_to_4h": 0.1007271877865778
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
      "layer": "gpt_neox.layers.0.mlp.dense_4h_to_h",
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
      "layer": "gpt_neox.layers.10.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.10.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.10.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.10.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.11.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.11.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.11.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.11.mlp.dense_h_to_4h",
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
      "layer": "gpt_neox.layers.12.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.12.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.12.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.13.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.13.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.13.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.14.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.14.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.14.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.15.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.15.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.15.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.16.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.16.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.16.mlp.dense_h_to_4h",
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
      "layer": "gpt_neox.layers.17.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.17.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.18.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.18.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.18.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.19.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.19.mlp.dense_h_to_4h",
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
      "layer": "gpt_neox.layers.2.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.20.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.20.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.21.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.21.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.22.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.22.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.23.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.23.mlp.dense_4h_to_h",
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
      "layer": "gpt_neox.layers.3.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.4.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.4.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.5.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.5.mlp.dense_4h_to_h",
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
      "auroc": 1.0,
      "layer": "gpt_neox.layers.6.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.7.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.7.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.7.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.8.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.8.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.8.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.9.attention.dense",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.9.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.9.mlp.dense_4h_to_h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "gpt_neox.layers.9.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999847412109375,
      "layer": "gpt_neox.layers.13.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999847412109375,
      "layer": "gpt_neox.layers.19.attention.dense",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999847412109375,
      "layer": "gpt_neox.layers.23.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999969482421875,
      "layer": "gpt_neox.layers.16.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999969482421875,
      "layer": "gpt_neox.layers.22.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9921875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999542236328125,
      "layer": "gpt_neox.layers.20.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.9999542236328125,
      "layer": "gpt_neox.layers.21.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999542236328125,
      "layer": "gpt_neox.layers.7.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999542236328125,
      "layer": "gpt_neox.layers.8.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.99993896484375,
      "layer": "gpt_neox.layers.1.attention.dense",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998931884765625,
      "layer": "gpt_neox.layers.21.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.9998016357421875,
      "layer": "gpt_neox.layers.22.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.9998016357421875,
      "layer": "gpt_neox.layers.6.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9765625,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.999786376953125,
      "layer": "gpt_neox.layers.23.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.9996490478515625,
      "layer": "gpt_neox.layers.3.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.9453125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9996185302734375,
      "layer": "gpt_neox.layers.3.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.95703125,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.9996185302734375,
      "layer": "gpt_neox.layers.6.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.98046875,
      "tpr_at_1pct_fpr": 0.984375
    },
    {
      "auroc": 0.9995880126953125,
      "layer": "gpt_neox.layers.4.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9375,
      "tpr_at_1pct_fpr": 0.98828125
    },
    {
      "auroc": 0.99957275390625,
      "layer": "gpt_neox.layers.5.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.9375,
      "tpr_at_1pct_fpr": 0.98046875
    },
    {
      "auroc": 0.999542236328125,
      "layer": "gpt_neox.layers.20.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.9994354248046875,
      "layer": "gpt_neox.layers.15.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.96484375,
      "tpr_at_1pct_fpr": 0.97265625
    },
    {
      "auroc": 0.9993896484375,
      "layer": "gpt_neox.layers.5.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.86328125,
      "tpr_at_1pct_fpr": 0.99609375
    },
    {
      "auroc": 0.9993743896484375,
      "layer": "gpt_neox.layers.4.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.91015625,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.999114990234375,
      "layer": "gpt_neox.layers.19.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.94921875,
      "tpr_at_1pct_fpr": 0.97265625
    },
    {
      "auroc": 0.998931884765625,
      "layer": "gpt_neox.layers.0.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.7890625,
      "tpr_at_1pct_fpr": 0.98046875
    },
    {
      "auroc": 0.998748779296875,
      "layer": "gpt_neox.layers.2.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.8203125,
      "tpr_at_1pct_fpr": 0.9765625
    },
    {
      "auroc": 0.9986419677734375,
      "layer": "gpt_neox.layers.1.mlp.dense_h_to_4h",
      "tpr_at_0_1pct_fpr": 0.88671875,
      "tpr_at_1pct_fpr": 0.9375
    },
    {
      "auroc": 0.998626708984375,
      "layer": "gpt_neox.layers.1.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8984375,
      "tpr_at_1pct_fpr": 0.95703125
    },
    {
      "auroc": 0.9985809326171875,
      "layer": "gpt_neox.layers.0.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.81640625,
      "tpr_at_1pct_fpr": 0.96875
    },
    {
      "auroc": 0.998565673828125,
      "layer": "gpt_neox.layers.2.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.8359375,
      "tpr_at_1pct_fpr": 0.90625
    },
    {
      "auroc": 0.9983978271484375,
      "layer": "gpt_neox.layers.18.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.83984375,
      "tpr_at_1pct_fpr": 0.97265625
    },
    {
      "auroc": 0.99444580078125,
      "layer": "gpt_neox.layers.17.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.671875,
      "tpr_at_1pct_fpr": 0.91796875
    },
    {
      "auroc": 0.988983154296875,
      "layer": "gpt_neox.layers.14.attention.query_key_value",
      "tpr_at_0_1pct_fpr": 0.61328125,
      "tpr_at_1pct_fpr": 0.71875
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
      "auroc": 0.7401580810546875,
      "tpr_at_0_1pct_fpr": 0.0703125,
      "tpr_at_1pct_fpr": 0.12890625
    },
    "output_kl": {
      "auroc": 0.631683349609375,
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.0390625
    },
    "output_logit_mse": {
      "auroc": 0.7442474365234375,
      "tpr_at_0_1pct_fpr": 0.07421875,
      "tpr_at_1pct_fpr": 0.15625
    },
    "output_logprob": {
      "auroc": 0.554473876953125,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    "output_logprob_gap": {
      "auroc": 0.554473876953125,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01171875
    }
  },
  "model": "EleutherAI/pythia-410m",
  "model_dtype": "bfloat16",
  "model_revision": "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f",
  "output_combination": {
    "coefficients": {
      "output_kl": 0.11726078922327156,
      "output_logit_mse": 0.998803415275317,
      "output_logprob": 0.051552715389095304,
      "output_logprob_gap": 0.051552715389095366
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 0.1,
    "shadow_split_auroc": 0.7645941840277778
  },
  "parameters": 405334016,
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
      "lower_quartile": 0.71484375,
      "maximum": 0.921875,
      "median": 0.7734375,
      "minimum": 0.28125,
      "targets_above_chance": 30,
      "targets_at_least_0_9": 2,
      "upper_quartile": 0.84765625
    },
    "output_kl": {
      "lower_quartile": 0.5,
      "maximum": 0.9375,
      "median": 0.6171875,
      "minimum": 0.40625,
      "targets_above_chance": 23,
      "targets_at_least_0_9": 3,
      "upper_quartile": 0.72265625
    },
    "output_logit_mse": {
      "lower_quartile": 0.6875,
      "maximum": 0.921875,
      "median": 0.7890625,
      "minimum": 0.328125,
      "targets_above_chance": 30,
      "targets_at_least_0_9": 4,
      "upper_quartile": 0.828125
    },
    "output_logprob": {
      "lower_quartile": 0.453125,
      "maximum": 0.796875,
      "median": 0.5625,
      "minimum": 0.21875,
      "targets_above_chance": 21,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.67578125
    },
    "output_logprob_gap": {
      "lower_quartile": 0.453125,
      "maximum": 0.796875,
      "median": 0.5625,
      "minimum": 0.21875,
      "targets_above_chance": 21,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.67578125
    }
  },
  "population_sha256": "1385df045ff8aee13c1006e946be56b27a8df72aa7449f2b16bf79d9ee68bf10",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "document_count": 4000,
    "earliest_published": "2024-01-01T00:54:02Z",
    "identifier_sha256": "6cf2151daecdb3ec893ce81d946bcdfa1c21bbd06d03b7b05064f1782132e412",
    "latest_published": "2024-02-10T00:49:46Z",
    "path": "data\\arxiv_cs_lg_2024.jsonl",
    "pool_sha256": "a8c57b62f3076a3b43e4d279c3ef198d8a043f54c0867eee3e4d2e6f71340dd2",
    "queries": [
      "cat:cs.LG AND submittedDate:[202401010000 TO 202412312359]"
    ],
    "required_published_after": "2023-12-31T23:59:59Z",
    "seed": 20261002,
    "sha256": "bdb4a18acfeb49e89ecc29bb54c3dcdd9f0ce67a1a9936a92db7d95cdc79e454",
    "source": "text_jsonl",
    "sources": [
      "arXiv API"
    ],
    "text_field": "text"
  },
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.005133943208348152,
    "base_mean_logprob": -3.173473075032234,
    "base_perplexity": 23.890313288216166,
    "mean_logprob_change": -0.07174002900719642,
    "perplexity_ratio_quantized_over_base": 1.0743760011591952,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -3.2452131040394305,
    "quantized_perplexity": 25.667179257034064,
    "reference_decisions": 640
  },
  "selected_artifact_feature": "artifact_reconstruction",
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
        "test_false_positives": 3,
        "test_fpr": 0.01171875,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -1.71683183291052
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.01171875,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -0.6259411840816397
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.06640625,
        "test_true_positives": 17,
        "threshold": 1.88967971853895
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 5,
        "test_fpr": 0.01953125,
        "test_tpr": 0.04296875,
        "test_true_positives": 11,
        "threshold": 1.7416948154251506
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 0,
        "test_fpr": 0.0,
        "test_tpr": 0.03515625,
        "test_true_positives": 9,
        "threshold": 2.0636442237466834
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 13,
        "test_fpr": 0.05078125,
        "test_tpr": 0.05859375,
        "test_true_positives": 15,
        "threshold": 1.8177142442715037
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 3,
        "shadow_false_positives": 3,
        "shadow_fpr": 0.0078125,
        "target_fpr": 0.01,
        "test_false_positives": 13,
        "test_fpr": 0.05078125,
        "test_tpr": 0.05859375,
        "test_true_positives": 15,
        "threshold": 1.817714244271504
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
      "auroc": 0.7730509440104167,
      "tpr_at_0_1pct_fpr": 0.018229166666666668,
      "tpr_at_1pct_fpr": 0.0546875
    },
    "output_kl": {
      "auroc": 0.6632283528645834,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.06510416666666667
    },
    "output_logit_mse": {
      "auroc": 0.7709486219618056,
      "tpr_at_0_1pct_fpr": 0.005208333333333333,
      "tpr_at_1pct_fpr": 0.033854166666666664
    },
    "output_logprob": {
      "auroc": 0.6180352105034721,
      "tpr_at_0_1pct_fpr": 0.03125,
      "tpr_at_1pct_fpr": 0.049479166666666664
    },
    "output_logprob_gap": {
      "auroc": 0.6180352105034721,
      "tpr_at_0_1pct_fpr": 0.03125,
      "tpr_at_1pct_fpr": 0.049479166666666664
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
