# CalibTrace named-library attack report

Library `auto-round` 0.14.2 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 32 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 64 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.5319 | 0.0195 | 0.0049 |
| artifact_layer_combination | 0.8168 | 0.1670 | 0.0713 |
| output_logit_mse | 1.0000 | 1.0000 | 1.0000 |
| output_kl | 1.0000 | 0.9990 | 0.9932 |
| output_logprob | 0.6088 | 0.0117 | 0.0029 |
| output_logprob_gap | 0.6088 | 0.0117 | 0.0029 |
| output_combination | 1.0000 | 1.0000 | 1.0000 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_logit_mse`: -0.1832 AUROC, crossed-bootstrap 95% interval [-0.2149, -0.1517]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 1024 calibration-excluded reference scores, mean token log probability changes by -0.013830; the corresponding perplexity ratio is 1.013926.

## Generation runtime

The 64 quantize-and-score jobs took 25.5 minutes in aggregate, with mean 23.9 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.9.fc2 | 0.6516 | 0.0283 |
| model.decoder.layers.8.fc2 | 0.6226 | 0.0303 |
| model.decoder.layers.10.fc2 | 0.5955 | 0.0303 |
| model.decoder.layers.6.fc2 | 0.5874 | 0.0400 |
| model.decoder.layers.5.fc2 | 0.5854 | 0.0303 |
| model.decoder.layers.7.fc2 | 0.5717 | 0.0156 |
| model.decoder.layers.4.fc2 | 0.5515 | 0.0215 |
| model.decoder.layers.9.fc1 | 0.5477 | 0.0205 |
| model.decoder.layers.9.self_attn.out_proj | 0.5430 | 0.0068 |
| model.decoder.layers.1.fc2 | 0.5385 | 0.0215 |
| model.decoder.layers.11.self_attn.out_proj | 0.5363 | 0.0156 |
| model.decoder.layers.5.self_attn.v_proj | 0.5352 | 0.0059 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.5076 | 0.0088 |
| artifact_layer_combination | 0.5530 | 0.0215 |
| selected_artifact | 0.5530 | 0.0215 |
| selected_output | 0.9902 | 0.8643 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_logit_mse_auroc": -0.18318462371826172,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": -0.4371833801269531,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.521192921428343,
          "upper_95": 0.5913556091372357
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.03531900067206033
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.006896043628480455,
          "upper_95": 0.046189060879278696
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": -0.47136995217907396,
        "upper_95": -0.39577590433787774
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.4718299537847236,
          "upper_95": 0.5455672429994313
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.011860069603010878
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.02866511809052215
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.9816980658756288,
          "upper_95": 0.996710522374227
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.6352608615483901,
          "upper_95": 0.9056248446732666
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.7263096369826672,
          "upper_95": 0.9547062425141672
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.9792589904583316,
          "upper_95": 0.9962384972974624
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.6274270153055282,
          "upper_95": 0.8910903012266544
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.7710880779141286,
          "upper_95": 0.9391966389466389
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.9436723112651944,
          "upper_95": 0.9864311239243361
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.23421199582195082,
          "upper_95": 0.682695707070707
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.4160121972621973,
          "upper_95": 0.7739428087251322
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4746760291540248,
          "upper_95": 0.5381815916794018
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.008877504205536013
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.027860696517412936
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.5465141685445835,
          "upper_95": 0.6401498010156135
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.013687902552480901
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.028721090163227353
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.521192921428343,
          "upper_95": 0.5913556091372357
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.03531900067206033
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.006896043628480455,
          "upper_95": 0.046189060879278696
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.9816980658756288,
          "upper_95": 0.996710522374227
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.6352608615483901,
          "upper_95": 0.9056248446732666
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.7263096369826672,
          "upper_95": 0.9547062425141672
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.5530385971069336,
        "tpr_at_0_1pct_fpr": 0.01171875,
        "tpr_at_1pct_fpr": 0.021484375
      },
      "artifact_reconstruction": {
        "auroc": 0.5075979232788086,
        "tpr_at_0_1pct_fpr": 0.0009765625,
        "tpr_at_1pct_fpr": 0.0087890625
      },
      "output_combination": {
        "auroc": 0.9902219772338867,
        "tpr_at_0_1pct_fpr": 0.7236328125,
        "tpr_at_1pct_fpr": 0.8642578125
      },
      "output_kl": {
        "auroc": 0.9888982772827148,
        "tpr_at_0_1pct_fpr": 0.732421875,
        "tpr_at_1pct_fpr": 0.857421875
      },
      "output_logit_mse": {
        "auroc": 0.9657001495361328,
        "tpr_at_0_1pct_fpr": 0.3486328125,
        "tpr_at_1pct_fpr": 0.59375
      },
      "output_logprob": {
        "auroc": 0.5064687728881836,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0107421875
      },
      "output_logprob_gap": {
        "auroc": 0.5920162200927734,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "selected_artifact": {
        "auroc": 0.5530385971069336,
        "tpr_at_0_1pct_fpr": 0.01171875,
        "tpr_at_1pct_fpr": 0.021484375
      },
      "selected_output": {
        "auroc": 0.9902219772338867,
        "tpr_at_0_1pct_fpr": 0.7236328125,
        "tpr_at_1pct_fpr": 0.8642578125
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
        "layer_validation_auroc": 0.650911840175953,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.9824123289345064,
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
        "layer_validation_auroc": 0.553213587487781,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.9940738025415445,
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
        "lower_95": 0.7851423866448938,
        "upper_95": 0.8483318062352185
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.04385719886307948,
        "upper_95": 0.16772343736571352
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.09912158879148415,
        "upper_95": 0.24062094892403418
      }
    },
    "artifact_minus_output_logit_mse_auroc": {
      "lower_95": -0.2148576133551062,
      "upper_95": -0.1516681937647815
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.48898907631289584,
        "upper_95": 0.5725466075373791
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.02514873672564706
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0048921290209148725,
        "upper_95": 0.04631425578968112
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
        "lower_95": 0.999870236354379,
        "upper_95": 1.0
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.983790976081699,
        "upper_95": 1.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.9941953009443623,
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
        "lower_95": 0.5587880521096297,
        "upper_95": 0.6574027848523188
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.017326865973406925
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.000984251968503937,
        "upper_95": 0.045789656369316194
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.5587880521096297,
        "upper_95": 0.6574027848523188
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.017326865973406925
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.000984251968503937,
        "upper_95": 0.045789656369316194
      }
    }
  },
  "empirical_test_fpr_resolution": 0.0009765625,
  "experiment_sha256": "9e25d196a5c7c1487219df5f7369418e2ccde8248b930739cf38411c10ffdac9",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.47581732273101807,
    "null_mean": 0.5001270888328552,
    "null_upper_95": 0.5241736650466918,
    "observed_auroc": 0.8168153762817383,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 64,
    "maximum_seconds": 26.695355199975893,
    "mean_seconds_per_artifact": 23.862722434379975,
    "minimum_seconds": 18.832938900101,
    "total_seconds": 1527.2142358003184
  },
  "iters": 50,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.025367007766032262,
      "model.decoder.layers.0.fc2": 0.02173866634751292,
      "model.decoder.layers.0.self_attn.k_proj": 0.02605396726439533,
      "model.decoder.layers.0.self_attn.out_proj": 0.0033828071287302637,
      "model.decoder.layers.0.self_attn.q_proj": 0.051167963794217564,
      "model.decoder.layers.0.self_attn.v_proj": 0.011860234742709334,
      "model.decoder.layers.1.fc1": 0.017144812752410078,
      "model.decoder.layers.1.fc2": 0.05946838675731047,
      "model.decoder.layers.1.self_attn.k_proj": 0.017576642311390406,
      "model.decoder.layers.1.self_attn.out_proj": -0.0031360123729953704,
      "model.decoder.layers.1.self_attn.q_proj": -0.014750187526541768,
      "model.decoder.layers.1.self_attn.v_proj": -0.004633834862676023,
      "model.decoder.layers.10.fc1": 0.05184991478462263,
      "model.decoder.layers.10.fc2": 0.09457875253706881,
      "model.decoder.layers.10.self_attn.k_proj": 0.023051575737900187,
      "model.decoder.layers.10.self_attn.out_proj": 0.023369985644849184,
      "model.decoder.layers.10.self_attn.q_proj": 0.005281571439393833,
      "model.decoder.layers.10.self_attn.v_proj": 0.04208802830803049,
      "model.decoder.layers.11.fc1": 0.0723537015453845,
      "model.decoder.layers.11.fc2": 0.028010004662571662,
      "model.decoder.layers.11.self_attn.k_proj": -0.011096278007379142,
      "model.decoder.layers.11.self_attn.out_proj": 0.013387302349122839,
      "model.decoder.layers.11.self_attn.q_proj": -0.04471730242096922,
      "model.decoder.layers.11.self_attn.v_proj": 0.011848741466431187,
      "model.decoder.layers.2.fc1": 0.019918083779329035,
      "model.decoder.layers.2.fc2": 0.01788653316699293,
      "model.decoder.layers.2.self_attn.k_proj": 0.013235716547118321,
      "model.decoder.layers.2.self_attn.out_proj": -0.008521238245260425,
      "model.decoder.layers.2.self_attn.q_proj": -0.007093121080678187,
      "model.decoder.layers.2.self_attn.v_proj": 0.024052139242420324,
      "model.decoder.layers.3.fc1": -0.0009562535030729496,
      "model.decoder.layers.3.fc2": 0.038532819794597925,
      "model.decoder.layers.3.self_attn.k_proj": -0.0007780564741526982,
      "model.decoder.layers.3.self_attn.out_proj": -0.015460230991966977,
      "model.decoder.layers.3.self_attn.q_proj": 0.0033782336308564457,
      "model.decoder.layers.3.self_attn.v_proj": 0.05167904432395278,
      "model.decoder.layers.4.fc1": -0.011681588601822203,
      "model.decoder.layers.4.fc2": 0.1021302380818039,
      "model.decoder.layers.4.self_attn.k_proj": 0.008957478303980219,
      "model.decoder.layers.4.self_attn.out_proj": -0.006275167924720051,
      "model.decoder.layers.4.self_attn.q_proj": -0.013586519062758548,
      "model.decoder.layers.4.self_attn.v_proj": 0.02016165256060015,
      "model.decoder.layers.5.fc1": 0.02602867837053283,
      "model.decoder.layers.5.fc2": 0.1456157141246098,
      "model.decoder.layers.5.self_attn.k_proj": 0.008166821542802403,
      "model.decoder.layers.5.self_attn.out_proj": -0.006310427825249124,
      "model.decoder.layers.5.self_attn.q_proj": -0.0036554621854380845,
      "model.decoder.layers.5.self_attn.v_proj": 0.04795115931232205,
      "model.decoder.layers.6.fc1": 0.03452841485734968,
      "model.decoder.layers.6.fc2": 0.1280188676553431,
      "model.decoder.layers.6.self_attn.k_proj": 0.015102921102507745,
      "model.decoder.layers.6.self_attn.out_proj": -0.006016385530373793,
      "model.decoder.layers.6.self_attn.q_proj": -0.015967815604276434,
      "model.decoder.layers.6.self_attn.v_proj": 0.03259421608459932,
      "model.decoder.layers.7.fc1": 0.0183560830816742,
      "model.decoder.layers.7.fc2": 0.10250187418042711,
      "model.decoder.layers.7.self_attn.k_proj": -0.00874442658410539,
      "model.decoder.layers.7.self_attn.out_proj": 0.02385987729632886,
      "model.decoder.layers.7.self_attn.q_proj": -0.011978681468954465,
      "model.decoder.layers.7.self_attn.v_proj": 0.04173344721890048,
      "model.decoder.layers.8.fc1": 0.044470060662536934,
      "model.decoder.layers.8.fc2": 0.13814256870001917,
      "model.decoder.layers.8.self_attn.k_proj": 0.019358611648798714,
      "model.decoder.layers.8.self_attn.out_proj": -0.0024448556871049048,
      "model.decoder.layers.8.self_attn.q_proj": -0.006599969477714775,
      "model.decoder.layers.8.self_attn.v_proj": -0.008450141654055204,
      "model.decoder.layers.9.fc1": 0.059759317789532945,
      "model.decoder.layers.9.fc2": 0.1651269939651394,
      "model.decoder.layers.9.self_attn.k_proj": 0.008954090845711882,
      "model.decoder.layers.9.self_attn.out_proj": 0.07156000036734571,
      "model.decoder.layers.9.self_attn.q_proj": 0.0021422195262117637,
      "model.decoder.layers.9.self_attn.v_proj": 0.05385446633674691
    },
    "regularization": 0.001,
    "shadow_split_auroc": 0.8026409149169922
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 0.6516323089599609,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 0.0087890625,
      "tpr_at_1pct_fpr": 0.0283203125
    },
    {
      "auroc": 0.6225786209106445,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0302734375
    },
    {
      "auroc": 0.5955400466918945,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 0.0087890625,
      "tpr_at_1pct_fpr": 0.0302734375
    },
    {
      "auroc": 0.5874176025390625,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0400390625
    },
    {
      "auroc": 0.58544921875,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 0.0087890625,
      "tpr_at_1pct_fpr": 0.0302734375
    },
    {
      "auroc": 0.5717477798461914,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5515165328979492,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.021484375
    },
    {
      "auroc": 0.5476608276367188,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0205078125
    },
    {
      "auroc": 0.5429763793945312,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5384893417358398,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.021484375
    },
    {
      "auroc": 0.5362739562988281,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5352373123168945,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5339365005493164,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5323219299316406,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5312776565551758,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5312728881835938,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.5306787490844727,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5260696411132812,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.5260648727416992,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5222883224487305,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5216760635375977,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5210762023925781,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.5187110900878906,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5184812545776367,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5180606842041016,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5178098678588867,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5137538909912109,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.5132160186767578,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.017578125
    },
    {
      "auroc": 0.5131759643554688,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5110816955566406,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5106449127197266,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5103378295898438,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.005859375
    },
    {
      "auroc": 0.5102262496948242,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0205078125
    },
    {
      "auroc": 0.5101041793823242,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5099821090698242,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5087718963623047,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5081605911254883,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.5074014663696289,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.5065631866455078,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.505650520324707,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5053815841674805,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5048456192016602,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.5044889450073242,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5043907165527344,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5041160583496094,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0029296875
    },
    {
      "auroc": 0.5040016174316406,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5037527084350586,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.5032577514648438,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5029659271240234,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.5027761459350586,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.5016965866088867,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.5013589859008789,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.5013093948364258,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0048828125
    },
    {
      "auroc": 0.4995431900024414,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.4987163543701172,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4987001419067383,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.49816226959228516,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4976959228515625,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.013671875
    },
    {
      "auroc": 0.49738502502441406,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.49727439880371094,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.4958963394165039,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.49570560455322266,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0126953125
    },
    {
      "auroc": 0.4953632354736328,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.0146484375
    },
    {
      "auroc": 0.49459266662597656,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.0009765625,
      "tpr_at_1pct_fpr": 0.0029296875
    },
    {
      "auroc": 0.49227046966552734,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.0068359375,
      "tpr_at_1pct_fpr": 0.0185546875
    },
    {
      "auroc": 0.49094581604003906,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0107421875
    },
    {
      "auroc": 0.4883003234863281,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0068359375
    },
    {
      "auroc": 0.48493194580078125,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.0087890625
    },
    {
      "auroc": 0.48282909393310547,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4789466857910156,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0166015625
    },
    {
      "auroc": 0.4771261215209961,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.009765625
    },
    {
      "auroc": 0.47278308868408203,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.009765625
    }
  ],
  "library": "auto-round",
  "library_version": "0.14.2",
  "mean_changed_weight_fraction_vs_artifact0": null,
  "method": "AutoRound",
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 0.8168153762817383,
      "tpr_at_0_1pct_fpr": 0.0712890625,
      "tpr_at_1pct_fpr": 0.1669921875
    },
    "artifact_reconstruction": {
      "auroc": 0.531865119934082,
      "tpr_at_0_1pct_fpr": 0.0048828125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    "output_combination": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_kl": {
      "auroc": 0.9999732971191406,
      "tpr_at_0_1pct_fpr": 0.9931640625,
      "tpr_at_1pct_fpr": 0.9990234375
    },
    "output_logit_mse": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_logprob": {
      "auroc": 0.6088361740112305,
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    "output_logprob_gap": {
      "auroc": 0.6088361740112305,
      "tpr_at_0_1pct_fpr": 0.0029296875,
      "tpr_at_1pct_fpr": 0.01171875
    }
  },
  "model": "facebook/opt-125m",
  "model_dtype": "float16",
  "model_revision": "27dcfa74d334bc871f3234de431e71c6eeba5dd6",
  "output_combination": {
    "coefficients": {
      "output_kl": 3.8412646912699695,
      "output_logit_mse": 3.9411725565487963,
      "output_logprob": 0.033251105109127876,
      "output_logprob_gap": 0.033251105109127876
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
      "lower_quartile": 0.7802734375,
      "maximum": 0.96875,
      "median": 0.833984375,
      "minimum": 0.57421875,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 11,
      "upper_quartile": 0.88671875
    },
    "artifact_reconstruction": {
      "lower_quartile": 0.4677734375,
      "maximum": 0.74609375,
      "median": 0.5390625,
      "minimum": 0.3125,
      "targets_above_chance": 41,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.5986328125
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
      "minimum": 0.98046875,
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
      "lower_quartile": 0.50390625,
      "maximum": 0.92578125,
      "median": 0.62890625,
      "minimum": 0.296875,
      "targets_above_chance": 50,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.72265625
    },
    "output_logprob_gap": {
      "lower_quartile": 0.50390625,
      "maximum": 0.92578125,
      "median": 0.62890625,
      "minimum": 0.296875,
      "targets_above_chance": 50,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.72265625
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
    "artifact_logprob_change_std": 0.0021242261498098046,
    "base_mean_logprob": -3.8453422486782074,
    "base_perplexity": 46.774690187658,
    "mean_logprob_change": -0.013829946052283049,
    "perplexity_ratio_quantized_over_base": 1.0139260221543696,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -3.8591721947304904,
    "quantized_perplexity": 47.4260755594751,
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
        "test_false_positives": 22,
        "test_fpr": 0.021484375,
        "test_tpr": 0.2119140625,
        "test_true_positives": 217,
        "threshold": 1.5148918341272264
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 14,
        "test_fpr": 0.013671875,
        "test_tpr": 0.0234375,
        "test_true_positives": 24,
        "threshold": 2.0564962459509877
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.0068359375,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -0.866991233720364
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 11,
        "test_fpr": 0.0107421875,
        "test_tpr": 0.9990234375,
        "test_true_positives": 1023,
        "threshold": -0.38226864654881687
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 2,
        "test_fpr": 0.001953125,
        "test_tpr": 1.0,
        "test_true_positives": 1024,
        "threshold": -0.6399133831081333
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 38,
        "test_fpr": 0.037109375,
        "test_tpr": 0.044921875,
        "test_true_positives": 46,
        "threshold": 1.9079697847246875
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 10,
        "shadow_false_positives": 10,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 38,
        "test_fpr": 0.037109375,
        "test_tpr": 0.044921875,
        "test_true_positives": 46,
        "threshold": 1.9079697847246875
      }
    }
  },
  "shadow_metrics": {
    "artifact_layer_combination": {
      "auroc": 0.8343486785888672,
      "tpr_at_0_1pct_fpr": 0.14453125,
      "tpr_at_1pct_fpr": 0.20703125
    },
    "artifact_reconstruction": {
      "auroc": 0.5991487503051758,
      "tpr_at_0_1pct_fpr": 0.0107421875,
      "tpr_at_1pct_fpr": 0.0234375
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
      "auroc": 0.6517763137817383,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    "output_logprob_gap": {
      "auroc": 0.6517763137817383,
      "tpr_at_0_1pct_fpr": 0.0078125,
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
