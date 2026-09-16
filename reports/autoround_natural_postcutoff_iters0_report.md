# CalibTrace named-library attack report

Library `auto-round` 0.14.2 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 32 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 64 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.5318 | 0.0107 | 0.0020 |
| artifact_layer_combination | 0.7985 | 0.1074 | 0.0361 |
| output_logit_mse | 0.5022 | 0.0146 | 0.0020 |
| output_kl | 0.4707 | 0.0049 | 0.0000 |
| output_logprob | 0.5054 | 0.0059 | 0.0020 |
| output_logprob_gap | 0.5054 | 0.0059 | 0.0020 |
| output_combination | 0.4791 | 0.0127 | 0.0049 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_logprob`: 0.2931 AUROC, crossed-bootstrap 95% interval [0.2403, 0.3464]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 1024 calibration-excluded reference scores, mean token log probability changes by -0.066580; the corresponding perplexity ratio is 1.068847.

## Generation runtime

The 64 quantize-and-score jobs took 27.1 minutes in aggregate, with mean 25.4 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.1.fc2 | 0.7885 | 0.0654 |
| model.decoder.layers.5.fc2 | 0.6374 | 0.0459 |
| model.decoder.layers.9.fc2 | 0.6329 | 0.0400 |
| model.decoder.layers.7.fc2 | 0.6313 | 0.0156 |
| model.decoder.layers.8.fc2 | 0.6118 | 0.0352 |
| model.decoder.layers.10.fc2 | 0.5945 | 0.0186 |
| model.decoder.layers.4.fc2 | 0.5904 | 0.0215 |
| model.decoder.layers.6.fc2 | 0.5870 | 0.0273 |
| model.decoder.layers.9.fc1 | 0.5484 | 0.0146 |
| model.decoder.layers.0.fc2 | 0.5424 | 0.0146 |
| model.decoder.layers.1.self_attn.k_proj | 0.5421 | 0.0088 |
| model.decoder.layers.11.fc2 | 0.5293 | 0.0234 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.5014 | 0.0127 |
| artifact_layer_combination | 0.5175 | 0.0137 |
| selected_artifact | 0.5175 | 0.0137 |
| selected_output | 0.5018 | 0.0078 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_logprob_auroc": 0.29306983947753906,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.01573944091796875,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.4845124072151787,
          "upper_95": 0.5537675292750596
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0019780444665331597,
          "upper_95": 0.02501038611925708
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0057361376673040155,
          "upper_95": 0.03698425225754348
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": -0.024639295421916025,
        "upper_95": 0.06499103269871509
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.46417606660864696,
          "upper_95": 0.5387506078322868
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.019824682172359227
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.03581278721115925
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.46647190810936046,
          "upper_95": 0.5325966669751921
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.0080973710872927
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.022232055063913462
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.46485202029916967,
          "upper_95": 0.5326569337961262
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.008731310774977649
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.023233301064859633
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.4647309580247555,
          "upper_95": 0.5349656324800616
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.014925744782065766
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.02893100219417774
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.46641149947185334,
          "upper_95": 0.5303022789677065
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.011662091184444872
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0018974882415892516,
          "upper_95": 0.0277235457889215
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.46176630173061206,
          "upper_95": 0.5407963598245
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.011572962068518074
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.027334847042164098
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.4845124072151787,
          "upper_95": 0.5537675292750596
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0019780444665331597,
          "upper_95": 0.02501038611925708
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0057361376673040155,
          "upper_95": 0.03698425225754348
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.46607700479920255,
          "upper_95": 0.5350268638127617
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.009390556344665542
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.024096676000046474
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.5174970626831055,
        "tpr_at_0_1pct_fpr": 0.005859375,
        "tpr_at_1pct_fpr": 0.013671875
      },
      "artifact_reconstruction": {
        "auroc": 0.5014228820800781,
        "tpr_at_0_1pct_fpr": 0.0029296875,
        "tpr_at_1pct_fpr": 0.0126953125
      },
      "output_combination": {
        "auroc": 0.500152587890625,
        "tpr_at_0_1pct_fpr": 0.001953125,
        "tpr_at_1pct_fpr": 0.005859375
      },
      "output_kl": {
        "auroc": 0.5001125335693359,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0078125
      },
      "output_logit_mse": {
        "auroc": 0.5014247894287109,
        "tpr_at_0_1pct_fpr": 0.001953125,
        "tpr_at_1pct_fpr": 0.0048828125
      },
      "output_logprob": {
        "auroc": 0.49997425079345703,
        "tpr_at_0_1pct_fpr": 0.001953125,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "output_logprob_gap": {
        "auroc": 0.4996376037597656,
        "tpr_at_0_1pct_fpr": 0.001953125,
        "tpr_at_1pct_fpr": 0.009765625
      },
      "selected_artifact": {
        "auroc": 0.5174970626831055,
        "tpr_at_0_1pct_fpr": 0.005859375,
        "tpr_at_1pct_fpr": 0.013671875
      },
      "selected_output": {
        "auroc": 0.5017576217651367,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0078125
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
        "layer_validation_auroc": 0.5987903225806452,
        "output_regularization": 0.001,
        "output_validation_auroc": 0.47348484848484845,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_logit_mse",
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
        "layer_validation_auroc": 0.569770283479961,
        "output_regularization": 0.001,
        "output_validation_auroc": 0.4913856304985337,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_kl",
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
        "lower_95": 0.7619665426339095,
        "upper_95": 0.8308822542858889
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.016851716419564303,
        "upper_95": 0.11432094406032509
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.036784282915012324,
        "upper_95": 0.21578762033985913
      }
    },
    "artifact_minus_output_logprob_auroc": {
      "lower_95": 0.24033596035246194,
      "upper_95": 0.34638281456025094
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.48880439357869193,
        "upper_95": 0.5779857848388705
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.01177887464899581
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.030219613885875952
      }
    },
    "output_combination": {
      "auroc": {
        "lower_95": 0.4333024205725237,
        "upper_95": 0.5201113397362617
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.015720204633429942
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.001920727364372514,
        "upper_95": 0.027466702595545536
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.4244856205210534,
        "upper_95": 0.5156740693331753
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0028989024905023216
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.022118592843326883
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.462670515727158,
        "upper_95": 0.5424561282891199
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.01862790798360561
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.001911683072044583,
        "upper_95": 0.034017155249196455
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.45928867829707143,
        "upper_95": 0.5477005936079896
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.009731471370787895
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.02944352862122142
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.45928867829707143,
        "upper_95": 0.5477005936079896
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.009731471370787895
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.02944352862122142
      }
    }
  },
  "empirical_test_fpr_resolution": 0.0009765625,
  "experiment_sha256": "817581a967d63c96c3153b06056f09e311982a399d624a43c5159a5b1f2b065c",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4756726503372192,
    "null_mean": 0.499992089176178,
    "null_upper_95": 0.5246616125106811,
    "observed_auroc": 0.7984561920166016,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 64,
    "maximum_seconds": 31.59123819996603,
    "mean_seconds_per_artifact": 25.39255896405848,
    "minimum_seconds": 19.796709900023416,
    "total_seconds": 1625.1237736997427
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.010701002735901223,
      "model.decoder.layers.0.fc2": 0.052416694091862476,
      "model.decoder.layers.0.self_attn.k_proj": -0.007103143415325358,
      "model.decoder.layers.0.self_attn.out_proj": -0.0034925045739615025,
      "model.decoder.layers.0.self_attn.q_proj": 0.00969309512758189,
      "model.decoder.layers.0.self_attn.v_proj": 0.001573078314835344,
      "model.decoder.layers.1.fc1": -0.008149759796945771,
      "model.decoder.layers.1.fc2": 0.26186947106540254,
      "model.decoder.layers.1.self_attn.k_proj": -0.01204097465216962,
      "model.decoder.layers.1.self_attn.out_proj": 0.003931385155970121,
      "model.decoder.layers.1.self_attn.q_proj": -0.02564246473926779,
      "model.decoder.layers.1.self_attn.v_proj": 0.010685985903129459,
      "model.decoder.layers.10.fc1": 0.0021486504991024254,
      "model.decoder.layers.10.fc2": 0.07078971955318476,
      "model.decoder.layers.10.self_attn.k_proj": 0.00347871346339118,
      "model.decoder.layers.10.self_attn.out_proj": 0.008603177253051524,
      "model.decoder.layers.10.self_attn.q_proj": -0.006543479593859892,
      "model.decoder.layers.10.self_attn.v_proj": 0.016818210307612772,
      "model.decoder.layers.11.fc1": -0.007049327101510947,
      "model.decoder.layers.11.fc2": 0.017438270479210205,
      "model.decoder.layers.11.self_attn.k_proj": -0.0024424764871771843,
      "model.decoder.layers.11.self_attn.out_proj": 0.029735742397011065,
      "model.decoder.layers.11.self_attn.q_proj": 0.024314431150946173,
      "model.decoder.layers.11.self_attn.v_proj": -0.011125648703912458,
      "model.decoder.layers.2.fc1": -0.0004380720695456987,
      "model.decoder.layers.2.fc2": 0.006105202474791392,
      "model.decoder.layers.2.self_attn.k_proj": 0.015068044872021964,
      "model.decoder.layers.2.self_attn.out_proj": 0.016900593865313028,
      "model.decoder.layers.2.self_attn.q_proj": -0.0057850724109733305,
      "model.decoder.layers.2.self_attn.v_proj": -0.025553478667367804,
      "model.decoder.layers.3.fc1": 0.027224822729706295,
      "model.decoder.layers.3.fc2": 1.537829925578874e-07,
      "model.decoder.layers.3.self_attn.k_proj": 0.010673184242196791,
      "model.decoder.layers.3.self_attn.out_proj": 0.0007957635928082865,
      "model.decoder.layers.3.self_attn.q_proj": 0.03774832321080007,
      "model.decoder.layers.3.self_attn.v_proj": -0.0020485115899061116,
      "model.decoder.layers.4.fc1": 0.013876724625811033,
      "model.decoder.layers.4.fc2": 0.10235304177663127,
      "model.decoder.layers.4.self_attn.k_proj": 0.018144302918444176,
      "model.decoder.layers.4.self_attn.out_proj": 0.029273534525740927,
      "model.decoder.layers.4.self_attn.q_proj": 0.02442936716694634,
      "model.decoder.layers.4.self_attn.v_proj": -0.011232312718212454,
      "model.decoder.layers.5.fc1": 0.03229055583534479,
      "model.decoder.layers.5.fc2": 0.11234747351326396,
      "model.decoder.layers.5.self_attn.k_proj": 0.01854553172182553,
      "model.decoder.layers.5.self_attn.out_proj": 0.017745214566333274,
      "model.decoder.layers.5.self_attn.q_proj": 0.007071778379602298,
      "model.decoder.layers.5.self_attn.v_proj": -0.001389156069499439,
      "model.decoder.layers.6.fc1": 0.010870445431858075,
      "model.decoder.layers.6.fc2": 0.10159980598453994,
      "model.decoder.layers.6.self_attn.k_proj": -0.012656212482683888,
      "model.decoder.layers.6.self_attn.out_proj": 0.011344567364962923,
      "model.decoder.layers.6.self_attn.q_proj": 0.03376386751856337,
      "model.decoder.layers.6.self_attn.v_proj": 0.008346349501653206,
      "model.decoder.layers.7.fc1": 0.029083890482810924,
      "model.decoder.layers.7.fc2": 0.11881139215026491,
      "model.decoder.layers.7.self_attn.k_proj": 0.01828844491653104,
      "model.decoder.layers.7.self_attn.out_proj": -0.010016916256484916,
      "model.decoder.layers.7.self_attn.q_proj": -0.0024335433929329278,
      "model.decoder.layers.7.self_attn.v_proj": -0.010280998925072997,
      "model.decoder.layers.8.fc1": -0.007788976695435491,
      "model.decoder.layers.8.fc2": 0.12142691390315813,
      "model.decoder.layers.8.self_attn.k_proj": -0.008040115350990654,
      "model.decoder.layers.8.self_attn.out_proj": 0.015223107814489555,
      "model.decoder.layers.8.self_attn.q_proj": 0.006929160353738674,
      "model.decoder.layers.8.self_attn.v_proj": 0.014160655222999849,
      "model.decoder.layers.9.fc1": 0.030564756636412116,
      "model.decoder.layers.9.fc2": 0.1346239035031636,
      "model.decoder.layers.9.self_attn.k_proj": -0.004930208316087336,
      "model.decoder.layers.9.self_attn.out_proj": 0.04392325767769481,
      "model.decoder.layers.9.self_attn.q_proj": -0.009805902926854354,
      "model.decoder.layers.9.self_attn.v_proj": 0.0032911257108173718
    },
    "regularization": 0.001,
    "shadow_split_auroc": 0.80328369140625
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 0.7884712219238281,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.041015625,
      "tpr_at_1pct_fpr": 0.0654296875
    },
    {
      "auroc": 0.6373567581176758,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0458984375
    },
    {
      "auroc": 0.6329421997070312,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0400390625
    },
    {
      "auroc": 0.631291389465332,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.6118383407592773,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.5945301055908203,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0185546875
    },
    {
      "auroc": 0.5904417037963867,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.021484375
    },
    {
      "auroc": 0.5869960784912109,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.5484476089477539,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5423994064331055,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5420541763305664,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5292882919311523,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.5274982452392578,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.0087890625,
      "tpr_at_1pct_fpr": 0.0263671875
    },
    {
      "auroc": 0.5247592926025391,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5242490768432617,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5217056274414062,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5208864212036133,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5186595916748047,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.5162277221679688,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5147800445556641,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5144338607788086,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.5140142440795898,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5140047073364258,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.5136651992797852,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0224609375
    },
    {
      "auroc": 0.5133819580078125,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5127725601196289,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5116691589355469,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5110607147216797,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5105266571044922,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0029296875
    },
    {
      "auroc": 0.5101652145385742,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5097827911376953,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0185546875
    },
    {
      "auroc": 0.5097122192382812,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5095319747924805,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5089054107666016,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.5076694488525391,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.5076637268066406,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.507176399230957,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.5059776306152344,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5057172775268555,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5056447982788086,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.5054197311401367,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.5041027069091797,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5034866333007812,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.5033798217773438,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5030059814453125,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5017986297607422,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.501399040222168,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5009403228759766,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0029296875
    },
    {
      "auroc": 0.5007572174072266,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5007057189941406,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.49918174743652344,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4991035461425781,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.4988546371459961,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.49843311309814453,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.49829673767089844,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.4982633590698242,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.4981346130371094,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.4976787567138672,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4964466094970703,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.4961862564086914,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.4960346221923828,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.4958028793334961,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.49553871154785156,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.4952383041381836,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.4947805404663086,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.4938344955444336,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.4889249801635742,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.48726367950439453,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.48455333709716797,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.48452281951904297,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.4795961380004883,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    }
  ],
  "library": "auto-round",
  "library_version": "0.14.2",
  "mean_changed_weight_fraction_vs_artifact0": 0.065320964516459,
  "method": "AutoRound",
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 0.7984561920166016,
      "tpr_at_0_1pct_fpr": 0.0361328125,
      "tpr_at_1pct_fpr": 0.107421875
    },
    "artifact_reconstruction": {
      "auroc": 0.5318403244018555,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    "output_combination": {
      "auroc": 0.47907352447509766,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    "output_kl": {
      "auroc": 0.47072887420654297,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    "output_logit_mse": {
      "auroc": 0.5022096633911133,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    "output_logprob": {
      "auroc": 0.5053863525390625,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.005859375
    },
    "output_logprob_gap": {
      "auroc": 0.5053863525390625,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.005859375
    }
  },
  "model": "facebook/opt-125m",
  "model_dtype": "float16",
  "model_revision": "27dcfa74d334bc871f3234de431e71c6eeba5dd6",
  "output_combination": {
    "coefficients": {
      "output_kl": 0.03243305435893446,
      "output_logit_mse": 0.020768035535599225,
      "output_logprob": -0.0012130727159409976,
      "output_logprob_gap": -0.0012130727159409976
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 0.001,
    "shadow_split_auroc": 0.49456214904785156
  },
  "parameters": 125239296,
  "per_target_auroc": {
    "artifact_layer_combination": {
      "lower_quartile": 0.7490234375,
      "maximum": 0.99609375,
      "median": 0.796875,
      "minimum": 0.6171875,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 11,
      "upper_quartile": 0.8759765625
    },
    "artifact_reconstruction": {
      "lower_quartile": 0.44921875,
      "maximum": 0.8125,
      "median": 0.541015625,
      "minimum": 0.234375,
      "targets_above_chance": 38,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6103515625
    },
    "output_combination": {
      "lower_quartile": 0.4130859375,
      "maximum": 0.6875,
      "median": 0.46484375,
      "minimum": 0.2734375,
      "targets_above_chance": 25,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5517578125
    },
    "output_kl": {
      "lower_quartile": 0.3984375,
      "maximum": 0.703125,
      "median": 0.455078125,
      "minimum": 0.26953125,
      "targets_above_chance": 21,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5439453125
    },
    "output_logit_mse": {
      "lower_quartile": 0.44140625,
      "maximum": 0.7421875,
      "median": 0.505859375,
      "minimum": 0.30078125,
      "targets_above_chance": 33,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5703125
    },
    "output_logprob": {
      "lower_quartile": 0.4365234375,
      "maximum": 0.76953125,
      "median": 0.51171875,
      "minimum": 0.21484375,
      "targets_above_chance": 33,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5673828125
    },
    "output_logprob_gap": {
      "lower_quartile": 0.4365234375,
      "maximum": 0.76953125,
      "median": 0.51171875,
      "minimum": 0.21484375,
      "targets_above_chance": 33,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5673828125
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
    "artifact_logprob_change_std": 0.0007742143861842974,
    "base_mean_logprob": -3.8453422486782074,
    "base_perplexity": 46.774690187658,
    "mean_logprob_change": -0.06658026622608304,
    "perplexity_ratio_quantized_over_base": 1.0688467529272723,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -3.9119225149042904,
    "quantized_perplexity": 49.994975726257394,
    "reference_decisions": 1024
  },
  "selected_artifact_feature": "artifact_layer_combination",
  "selected_output_baseline": "output_logprob",
  "sequence_length": 512,
  "shadow_artifacts": 32,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 31,
        "test_fpr": 0.0302734375,
        "test_tpr": 0.224609375,
        "test_true_positives": 230,
        "threshold": 1.3975570917759297
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 30,
        "test_fpr": 0.029296875,
        "test_tpr": 0.0361328125,
        "test_true_positives": 37,
        "threshold": 2.0314904537256817
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 38,
        "test_fpr": 0.037109375,
        "test_tpr": 0.0361328125,
        "test_true_positives": 37,
        "threshold": 2.0025217489577143
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 33,
        "test_fpr": 0.0322265625,
        "test_tpr": 0.025390625,
        "test_true_positives": 26,
        "threshold": 2.048659780313111
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 25,
        "test_fpr": 0.0244140625,
        "test_tpr": 0.0234375,
        "test_true_positives": 24,
        "threshold": 2.187289726768172
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 33,
        "test_fpr": 0.0322265625,
        "test_tpr": 0.0283203125,
        "test_true_positives": 29,
        "threshold": 1.9739445518934553
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 33,
        "test_fpr": 0.0322265625,
        "test_tpr": 0.0283203125,
        "test_true_positives": 29,
        "threshold": 1.9739445518934553
      }
    }
  },
  "shadow_metrics": {
    "artifact_layer_combination": {
      "auroc": 0.8319673538208008,
      "tpr_at_0_1pct_fpr": 0.140625,
      "tpr_at_1pct_fpr": 0.228515625
    },
    "artifact_reconstruction": {
      "auroc": 0.5866069793701172,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.02734375
    },
    "output_combination": {
      "auroc": 0.5900249481201172,
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.0439453125
    },
    "output_kl": {
      "auroc": 0.5819883346557617,
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0244140625
    },
    "output_logit_mse": {
      "auroc": 0.592529296875,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    "output_logprob": {
      "auroc": 0.5937099456787109,
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.03515625
    },
    "output_logprob_gap": {
      "auroc": 0.5937099456787109,
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.03515625
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
