# CalibTrace named-library attack report

Library `auto-round` 0.14.2 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 32 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.6000 | 0.0156 | 0.0078 |
| artifact_layer_combination | 0.6030 | 0.0469 | 0.0039 |
| output_logit_mse | 0.5957 | 0.0391 | 0.0117 |
| output_kl | 0.6936 | 0.0469 | 0.0078 |
| output_logprob | 0.5399 | 0.0156 | 0.0078 |
| output_logprob_gap | 0.5399 | 0.0156 | 0.0078 |
| output_combination | 0.6951 | 0.0391 | 0.0078 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_combination`: -0.0921 AUROC, crossed-bootstrap 95% interval [-0.1886, 0.0059]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 768 calibration-excluded reference scores, mean token log probability changes by -0.022102; the corresponding perplexity ratio is 1.022348.

## Generation runtime

The 48 quantize-and-score jobs took 7.9 minutes in aggregate, with mean 9.9 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.11.fc1 | 0.5728 | 0.0195 |
| model.decoder.layers.3.self_attn.k_proj | 0.5697 | 0.0195 |
| model.decoder.layers.1.self_attn.q_proj | 0.5687 | 0.0273 |
| model.decoder.layers.6.self_attn.q_proj | 0.5645 | 0.0312 |
| model.decoder.layers.1.self_attn.k_proj | 0.5600 | 0.0234 |
| model.decoder.layers.2.fc1 | 0.5575 | 0.0039 |
| model.decoder.layers.5.self_attn.v_proj | 0.5548 | 0.0234 |
| model.decoder.layers.8.self_attn.k_proj | 0.5504 | 0.0117 |
| model.decoder.layers.5.fc1 | 0.5502 | 0.0391 |
| model.decoder.layers.11.self_attn.q_proj | 0.5498 | 0.0430 |
| model.decoder.layers.1.self_attn.v_proj | 0.5496 | 0.0430 |
| model.decoder.layers.4.self_attn.out_proj | 0.5482 | 0.0078 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.5159 | 0.0078 |
| artifact_layer_combination | 0.5171 | 0.0078 |
| selected_artifact | 0.5159 | 0.0078 |
| selected_output | 0.6131 | 0.0234 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": -0.09210205078125,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": -0.09716796875,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.4320524235366848,
          "upper_95": 0.5998008942579695
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.038030097752137865
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.06085879923015536
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": -0.18188158509348282,
        "upper_95": -0.014696713261959548
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.4351328168479981,
          "upper_95": 0.5929429413293225
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.06023391812865489
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.0760305019305019
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.5254617773638389,
          "upper_95": 0.6739576518467874
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.13177097413715413
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.15832090207090205
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.5346434315514812,
          "upper_95": 0.6879452236415147
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.09449223939600142
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.1285998206814106
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.49193302077743156,
          "upper_95": 0.6736695715462908
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.08787829140831105
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.003936621892851629,
          "upper_95": 0.09270969507189974
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.416552271313339,
          "upper_95": 0.5678875262609081
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.02390677290836653
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.03297767168209872
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.4067235597203419,
          "upper_95": 0.5678638785901863
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.049642454035108544
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.06148292613456547
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.4351328168479981,
          "upper_95": 0.5929429413293225
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.06023391812865489
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.0760305019305019
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.5346434315514812,
          "upper_95": 0.6879452236415147
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.09449223939600142
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.1285998206814106
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.51708984375,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0078125
      },
      "artifact_reconstruction": {
        "auroc": 0.515899658203125,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0078125
      },
      "output_combination": {
        "auroc": 0.6026458740234375,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.06640625
      },
      "output_kl": {
        "auroc": 0.613067626953125,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0234375
      },
      "output_logit_mse": {
        "auroc": 0.583221435546875,
        "tpr_at_0_1pct_fpr": 0.03125,
        "tpr_at_1pct_fpr": 0.0390625
      },
      "output_logprob": {
        "auroc": 0.4936370849609375,
        "tpr_at_0_1pct_fpr": 0.00390625,
        "tpr_at_1pct_fpr": 0.00390625
      },
      "output_logprob_gap": {
        "auroc": 0.4879608154296875,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.00390625
      },
      "selected_artifact": {
        "auroc": 0.515899658203125,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0078125
      },
      "selected_output": {
        "auroc": 0.613067626953125,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0234375
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20260830,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          18,
          15,
          0,
          16,
          25,
          3,
          7,
          4,
          10,
          23,
          17,
          13,
          28,
          31,
          12,
          1
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 0.5363791735335408,
        "output_regularization": 0.001,
        "output_validation_auroc": 0.5845388512482452,
        "selected_artifact_feature": "artifact_reconstruction",
        "selected_output_feature": "output_kl",
        "training_candidates": [
          2,
          5,
          6,
          8,
          9,
          11,
          14,
          19,
          20,
          21,
          22,
          24,
          26,
          27,
          29,
          30
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          6,
          21,
          11,
          27,
          2,
          20,
          19,
          26,
          14,
          24,
          9,
          5,
          30,
          29,
          22,
          8
        ],
        "layer_regularization": 1.0,
        "layer_validation_auroc": 0.4852896294939877,
        "output_regularization": 0.1,
        "output_validation_auroc": 0.5990966245498383,
        "selected_artifact_feature": "artifact_reconstruction",
        "selected_output_feature": "output_kl",
        "training_candidates": [
          0,
          1,
          3,
          4,
          7,
          10,
          12,
          13,
          15,
          16,
          17,
          18,
          23,
          25,
          28,
          31
        ]
      }
    ]
  },
  "cluster_bootstrap": {
    "artifact_layer_combination": {
      "auroc": {
        "lower_95": 0.5194594491493094,
        "upper_95": 0.6824774135577713
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0956217276487918
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.12205728748192189
      }
    },
    "artifact_minus_output_combination_auroc": {
      "lower_95": -0.18863136342654302,
      "upper_95": 0.005868012618551341
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.5174308319983228,
        "upper_95": 0.6762595654335634
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.055768029739776945
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.07516011938372182
      }
    },
    "output_combination": {
      "auroc": {
        "lower_95": 0.6151890814879235,
        "upper_95": 0.7700774835193641
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.10448739448823298
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.14888816654083825
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.6169635368199616,
        "upper_95": 0.7671765726585075
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.10975944786920397
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.15103867227824982
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.5099321294421622,
        "upper_95": 0.684691565107587
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.11470604775217706
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.1429131652661064
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.4615163168828804,
        "upper_95": 0.6164300170336258
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.04706261045190608
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.054056493316421116
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.4615163168828804,
        "upper_95": 0.6164300170336258
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.04706261045190608
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.054056493316421116
      }
    }
  },
  "empirical_test_fpr_resolution": 0.00390625,
  "experiment_sha256": null,
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4495845794677734,
    "null_mean": 0.4996193298339844,
    "null_upper_95": 0.5491641998291016,
    "observed_auroc": 0.6030120849609375,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 48,
    "maximum_seconds": 10.673475399962626,
    "mean_seconds_per_artifact": 9.920102922914035,
    "minimum_seconds": 7.949658899975475,
    "total_seconds": 476.1649402998737
  },
  "iters": 10,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": -0.011922382328317058,
      "model.decoder.layers.0.fc2": -0.0035379906526713757,
      "model.decoder.layers.0.self_attn.k_proj": -0.020186850342899146,
      "model.decoder.layers.0.self_attn.out_proj": 0.00861001933647348,
      "model.decoder.layers.0.self_attn.q_proj": -0.0010577413464698748,
      "model.decoder.layers.0.self_attn.v_proj": 0.002587669630270638,
      "model.decoder.layers.1.fc1": -0.017174166045663592,
      "model.decoder.layers.1.fc2": -0.018267731904352397,
      "model.decoder.layers.1.self_attn.k_proj": -0.06942113196329992,
      "model.decoder.layers.1.self_attn.out_proj": -0.014395193842705262,
      "model.decoder.layers.1.self_attn.q_proj": -0.034839660626072605,
      "model.decoder.layers.1.self_attn.v_proj": -0.05085418271081047,
      "model.decoder.layers.10.fc1": -0.016604083673147033,
      "model.decoder.layers.10.fc2": -0.0017514901531755084,
      "model.decoder.layers.10.self_attn.k_proj": -0.01777687504363162,
      "model.decoder.layers.10.self_attn.out_proj": 0.002776112513418538,
      "model.decoder.layers.10.self_attn.q_proj": -0.02488142228353541,
      "model.decoder.layers.10.self_attn.v_proj": -0.021235761526953195,
      "model.decoder.layers.11.fc1": -0.007643338924778841,
      "model.decoder.layers.11.fc2": -0.014999280419177323,
      "model.decoder.layers.11.self_attn.k_proj": -0.001047465016111124,
      "model.decoder.layers.11.self_attn.out_proj": 0.006367712956787143,
      "model.decoder.layers.11.self_attn.q_proj": 0.014767610959644292,
      "model.decoder.layers.11.self_attn.v_proj": 0.010390604460684629,
      "model.decoder.layers.2.fc1": 0.00672929144319637,
      "model.decoder.layers.2.fc2": -0.004693084906218124,
      "model.decoder.layers.2.self_attn.k_proj": -0.018434672341867908,
      "model.decoder.layers.2.self_attn.out_proj": 0.00817915621494505,
      "model.decoder.layers.2.self_attn.q_proj": -0.03566929117630899,
      "model.decoder.layers.2.self_attn.v_proj": -0.014859992490981334,
      "model.decoder.layers.3.fc1": 0.001872552415653725,
      "model.decoder.layers.3.fc2": -0.014404830144635613,
      "model.decoder.layers.3.self_attn.k_proj": -0.01925199714753698,
      "model.decoder.layers.3.self_attn.out_proj": -0.02207457106670415,
      "model.decoder.layers.3.self_attn.q_proj": -0.03281323444887665,
      "model.decoder.layers.3.self_attn.v_proj": -0.031310134519807145,
      "model.decoder.layers.4.fc1": -0.0023732424510883726,
      "model.decoder.layers.4.fc2": -0.007799193793388802,
      "model.decoder.layers.4.self_attn.k_proj": -0.03266656853067678,
      "model.decoder.layers.4.self_attn.out_proj": -0.012126059781700246,
      "model.decoder.layers.4.self_attn.q_proj": -0.018105692469213615,
      "model.decoder.layers.4.self_attn.v_proj": -0.01242908273273969,
      "model.decoder.layers.5.fc1": -0.028247411646648693,
      "model.decoder.layers.5.fc2": -0.013380631340559411,
      "model.decoder.layers.5.self_attn.k_proj": -0.028980884959432292,
      "model.decoder.layers.5.self_attn.out_proj": -0.003184349355068579,
      "model.decoder.layers.5.self_attn.q_proj": -0.025714879730345166,
      "model.decoder.layers.5.self_attn.v_proj": 0.0007883125707588091,
      "model.decoder.layers.6.fc1": -0.02293605622179016,
      "model.decoder.layers.6.fc2": 0.007493378750834168,
      "model.decoder.layers.6.self_attn.k_proj": -0.03189653730795537,
      "model.decoder.layers.6.self_attn.out_proj": -0.025080175668846592,
      "model.decoder.layers.6.self_attn.q_proj": -0.034754306826512676,
      "model.decoder.layers.6.self_attn.v_proj": -0.016703448330894103,
      "model.decoder.layers.7.fc1": -0.010009193516441313,
      "model.decoder.layers.7.fc2": -0.043486343883309304,
      "model.decoder.layers.7.self_attn.k_proj": -0.009670990419415286,
      "model.decoder.layers.7.self_attn.out_proj": -0.015131962206405789,
      "model.decoder.layers.7.self_attn.q_proj": -0.016303849829271886,
      "model.decoder.layers.7.self_attn.v_proj": 0.0067176183516682265,
      "model.decoder.layers.8.fc1": -0.011717980230185675,
      "model.decoder.layers.8.fc2": -0.021268854640474847,
      "model.decoder.layers.8.self_attn.k_proj": -0.01798309279468399,
      "model.decoder.layers.8.self_attn.out_proj": -0.005787410466991494,
      "model.decoder.layers.8.self_attn.q_proj": -0.004328126361564713,
      "model.decoder.layers.8.self_attn.v_proj": -0.002923685596005441,
      "model.decoder.layers.9.fc1": -0.025593733423321066,
      "model.decoder.layers.9.fc2": 0.0044214364405079105,
      "model.decoder.layers.9.self_attn.k_proj": 0.003757961630097178,
      "model.decoder.layers.9.self_attn.out_proj": -0.015588611441721245,
      "model.decoder.layers.9.self_attn.q_proj": -0.012774698787809442,
      "model.decoder.layers.9.self_attn.v_proj": -0.005669666441399092
    },
    "regularization": 0.001,
    "shadow_split_auroc": 0.6411666870117188
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 0.57275390625,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5696868896484375,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5686798095703125,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.5645294189453125,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.03125
    },
    {
      "auroc": 0.559967041015625,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.557525634765625,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5548095703125,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.5504150390625,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.55023193359375,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0390625
    },
    {
      "auroc": 0.549835205078125,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.04296875
    },
    {
      "auroc": 0.5496368408203125,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.04296875
    },
    {
      "auroc": 0.5482330322265625,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5442047119140625,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.5405120849609375,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.53997802734375,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.53887939453125,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.538543701171875,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.537841796875,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.536651611328125,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5364837646484375,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5347747802734375,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.534637451171875,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.53460693359375,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.53125,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.04296875
    },
    {
      "auroc": 0.5301361083984375,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5272369384765625,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5269622802734375,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.52655029296875,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.524322509765625,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.524078369140625,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.52227783203125,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.522186279296875,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.01953125,
      "tpr_at_1pct_fpr": 0.03125
    },
    {
      "auroc": 0.5215911865234375,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5215606689453125,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.521026611328125,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5196990966796875,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.0234375,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.5183868408203125,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.518096923828125,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.517669677734375,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.515838623046875,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.511962890625,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5098419189453125,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5081024169921875,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5074615478515625,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5045318603515625,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0234375,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.502716064453125,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5021209716796875,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0234375
    },
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
      "auroc": 0.4962921142578125,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.4954833984375,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.4931640625,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.4930572509765625,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.4922637939453125,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.4913330078125,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.4885406494140625,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.488067626953125,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.488006591796875,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 0.0234375,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.48760986328125,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.485748291015625,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.4835968017578125,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.48321533203125,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4799957275390625,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.4756927490234375,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.469970703125,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.458465576171875,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.456207275390625,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.452484130859375,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    }
  ],
  "library": "auto-round",
  "library_version": "0.14.2",
  "mean_changed_weight_fraction_vs_artifact0": 0.6579944617108845,
  "method": "AutoRound",
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 0.6030120849609375,
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.046875
    },
    "artifact_reconstruction": {
      "auroc": 0.5999755859375,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.015625
    },
    "output_combination": {
      "auroc": 0.6951141357421875,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0390625
    },
    "output_kl": {
      "auroc": 0.6935577392578125,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.046875
    },
    "output_logit_mse": {
      "auroc": 0.5957489013671875,
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.0390625
    },
    "output_logprob": {
      "auroc": 0.53985595703125,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.015625
    },
    "output_logprob_gap": {
      "auroc": 0.53985595703125,
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.015625
    }
  },
  "model": "facebook/opt-125m",
  "model_dtype": "float16",
  "model_revision": null,
  "output_combination": {
    "coefficients": {
      "output_kl": 0.6414578618047959,
      "output_logit_mse": -0.012260045379278592,
      "output_logprob": -0.07699130259793165,
      "output_logprob_gap": -0.07699130259793165
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 1.0,
    "shadow_split_auroc": 0.6626663208007812
  },
  "parameters": 125239296,
  "per_target_auroc": {
    "artifact_layer_combination": {
      "lower_quartile": 0.51171875,
      "maximum": 0.84375,
      "median": 0.609375,
      "minimum": 0.328125,
      "targets_above_chance": 24,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.671875
    },
    "artifact_reconstruction": {
      "lower_quartile": 0.4765625,
      "maximum": 0.859375,
      "median": 0.6015625,
      "minimum": 0.3125,
      "targets_above_chance": 23,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.71875
    },
    "output_combination": {
      "lower_quartile": 0.640625,
      "maximum": 0.9375,
      "median": 0.703125,
      "minimum": 0.40625,
      "targets_above_chance": 28,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.78515625
    },
    "output_kl": {
      "lower_quartile": 0.6328125,
      "maximum": 0.90625,
      "median": 0.703125,
      "minimum": 0.421875,
      "targets_above_chance": 29,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.76953125
    },
    "output_logit_mse": {
      "lower_quartile": 0.54296875,
      "maximum": 0.90625,
      "median": 0.609375,
      "minimum": 0.125,
      "targets_above_chance": 26,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.68359375
    },
    "output_logprob": {
      "lower_quartile": 0.4453125,
      "maximum": 0.75,
      "median": 0.5390625,
      "minimum": 0.1875,
      "targets_above_chance": 23,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.65625
    },
    "output_logprob_gap": {
      "lower_quartile": 0.4453125,
      "maximum": 0.75,
      "median": 0.5390625,
      "minimum": 0.1875,
      "targets_above_chance": 23,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.65625
    }
  },
  "population_sha256": null,
  "quantizer_seed": "fixed",
  "record_metadata": null,
  "reference_records": 16,
  "reference_utility": {
    "artifact_logprob_change_std": 0.07813176427539122,
    "base_mean_logprob": -9.663284122943878,
    "base_perplexity": 15729.357079143332,
    "mean_logprob_change": -0.022101691613594692,
    "perplexity_ratio_quantized_over_base": 1.022347743376153,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -9.685385814557472,
    "quantized_perplexity": 16080.872714619893,
    "reference_decisions": 768
  },
  "selected_artifact_feature": "artifact_layer_combination",
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
        "test_tpr": 0.0390625,
        "test_true_positives": 10,
        "threshold": 2.0806867349635008
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.02734375,
        "test_tpr": 0.03125,
        "test_true_positives": 8,
        "threshold": 2.024288713454215
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 15,
        "test_fpr": 0.05859375,
        "test_tpr": 0.140625,
        "test_true_positives": 36,
        "threshold": 1.4753275032690145
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 16,
        "test_fpr": 0.0625,
        "test_tpr": 0.16796875,
        "test_true_positives": 43,
        "threshold": 1.4424778652203027
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.01171875,
        "test_tpr": 0.0390625,
        "test_true_positives": 10,
        "threshold": 1.9658464083173952
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
        "threshold": 1.9026178375525686
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
        "threshold": 1.9026178375525686
      }
    }
  },
  "shadow_metrics": {
    "artifact_layer_combination": {
      "auroc": 0.7235603332519531,
      "tpr_at_0_1pct_fpr": 0.025390625,
      "tpr_at_1pct_fpr": 0.0546875
    },
    "artifact_reconstruction": {
      "auroc": 0.6246681213378906,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    "output_combination": {
      "auroc": 0.6685256958007812,
      "tpr_at_0_1pct_fpr": 0.009765625,
      "tpr_at_1pct_fpr": 0.11328125
    },
    "output_kl": {
      "auroc": 0.6650772094726562,
      "tpr_at_0_1pct_fpr": 0.005859375,
      "tpr_at_1pct_fpr": 0.134765625
    },
    "output_logit_mse": {
      "auroc": 0.5918350219726562,
      "tpr_at_0_1pct_fpr": 0.001953125,
      "tpr_at_1pct_fpr": 0.02734375
    },
    "output_logprob": {
      "auroc": 0.5791702270507812,
      "tpr_at_0_1pct_fpr": 0.017578125,
      "tpr_at_1pct_fpr": 0.021484375
    },
    "output_logprob_gap": {
      "auroc": 0.5791702270507812,
      "tpr_at_0_1pct_fpr": 0.017578125,
      "tpr_at_1pct_fpr": 0.021484375
    }
  },
  "targets": 32,
  "test_artifacts": 16,
  "test_decisions": 512,
  "test_members": 256,
  "test_nonmembers": 256,
  "threat_model": "public base, released auto-round W4 artifact, one held-out artifact"
}
```
