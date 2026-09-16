# CalibTrace named-library attack report

Library `auto-round` 0.14.2 quantizes `facebook/opt-125m` to W4A16 from 32 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 32 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.5443 | 0.0273 | 0.0156 |
| artifact_layer_combination | 0.9299 | 0.2852 | 0.2578 |
| output_logit_mse | 1.0000 | 1.0000 | 1.0000 |
| output_kl | 1.0000 | 1.0000 | 1.0000 |
| output_logprob | 0.6958 | 0.0078 | 0.0000 |
| output_logprob_gap | 0.6958 | 0.0078 | 0.0000 |
| output_combination | 1.0000 | 1.0000 | 1.0000 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_logit_mse`: -0.0701 AUROC, crossed-bootstrap 95% interval [-0.1047, -0.0388]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 768 calibration-excluded reference scores, mean token log probability changes by 0.006728; the corresponding perplexity ratio is 0.993294.

## Generation runtime

The 48 quantize-and-score jobs took 37.3 minutes in aggregate, with mean 46.7 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.0.fc2 | 0.7206 | 0.0742 |
| model.decoder.layers.0.fc1 | 0.6783 | 0.0234 |
| model.decoder.layers.0.self_attn.k_proj | 0.6534 | 0.0352 |
| model.decoder.layers.0.self_attn.v_proj | 0.6530 | 0.1133 |
| model.decoder.layers.5.fc2 | 0.6383 | 0.0234 |
| model.decoder.layers.11.self_attn.out_proj | 0.6159 | 0.0469 |
| model.decoder.layers.7.fc1 | 0.5974 | 0.0312 |
| model.decoder.layers.6.fc2 | 0.5886 | 0.0508 |
| model.decoder.layers.1.self_attn.v_proj | 0.5878 | 0.0391 |
| model.decoder.layers.10.fc2 | 0.5855 | 0.0469 |
| model.decoder.layers.10.fc1 | 0.5841 | 0.0117 |
| model.decoder.layers.9.self_attn.out_proj | 0.5795 | 0.0156 |

## Unseen-candidate generalization

Candidate-fold cross-fitting excludes each evaluated candidate from every learned score direction, scale, feature combination, and feature-selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.5100 | 0.0117 |
| artifact_layer_combination | 0.6306 | 0.0312 |
| selected_artifact | 0.6306 | 0.0312 |
| selected_output | 1.0000 | 1.0000 |

Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_logit_mse_auroc": -0.0700836181640625,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": -0.369354248046875,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.5678541827897353,
          "upper_95": 0.7060843433707741
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.008545197740112996,
          "upper_95": 0.1641490118577074
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.015623480058365759,
          "upper_95": 0.2348353993090835
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": -0.4321458172102647,
        "upper_95": -0.29391412549358265
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.4343480359556899,
          "upper_95": 0.5877725366472834
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.055560718711276325
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.05618090338883624
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.9998778383495961,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9877551020408163,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9922442320066183,
          "upper_95": 1.0
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.9971806225092372,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.8875388651379713,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9048969110148259,
          "upper_95": 1.0
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.9989309077801077,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9072715572715573,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9382179521714406,
          "upper_95": 1.0
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.440514730519759,
          "upper_95": 0.5872813201698777
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.040498274374460734
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.061308576480990265
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.45718747818042177,
          "upper_95": 0.6486651236309391
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
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.5678541827897353,
          "upper_95": 0.7060843433707741
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.008545197740112996,
          "upper_95": 0.1641490118577074
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.015623480058365759,
          "upper_95": 0.2348353993090835
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.9997558444729292,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9765625,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9884077589256872,
          "upper_95": 1.0
        }
      }
    },
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.630615234375,
        "tpr_at_0_1pct_fpr": 0.0234375,
        "tpr_at_1pct_fpr": 0.03125
      },
      "artifact_reconstruction": {
        "auroc": 0.5099945068359375,
        "tpr_at_0_1pct_fpr": 0.0078125,
        "tpr_at_1pct_fpr": 0.01171875
      },
      "output_combination": {
        "auroc": 0.9999847412109375,
        "tpr_at_0_1pct_fpr": 0.99609375,
        "tpr_at_1pct_fpr": 1.0
      },
      "output_kl": {
        "auroc": 0.999359130859375,
        "tpr_at_0_1pct_fpr": 0.9453125,
        "tpr_at_1pct_fpr": 0.97265625
      },
      "output_logit_mse": {
        "auroc": 0.9998321533203125,
        "tpr_at_0_1pct_fpr": 0.95703125,
        "tpr_at_1pct_fpr": 1.0
      },
      "output_logprob": {
        "auroc": 0.5082244873046875,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0
      },
      "output_logprob_gap": {
        "auroc": 0.5522918701171875,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.0
      },
      "selected_artifact": {
        "auroc": 0.630615234375,
        "tpr_at_0_1pct_fpr": 0.0234375,
        "tpr_at_1pct_fpr": 0.03125
      },
      "selected_output": {
        "auroc": 0.999969482421875,
        "tpr_at_0_1pct_fpr": 0.9921875,
        "tpr_at_1pct_fpr": 1.0
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
        "layer_validation_auroc": 0.8113086510263929,
        "output_regularization": 1.0,
        "output_validation_auroc": 1.0,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_logit_mse",
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
        "layer_validation_auroc": 0.833730449657869,
        "output_regularization": 1.0,
        "output_validation_auroc": 0.9999389051808407,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_combination",
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
        "lower_95": 0.8953168330397338,
        "upper_95": 0.9611845418068767
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.17004709576138147,
        "upper_95": 0.5592624521072797
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.18646062271062272,
        "upper_95": 0.7096500416204217
      }
    },
    "artifact_minus_output_logit_mse_auroc": {
      "lower_95": -0.10468316696026629,
      "upper_95": -0.03881545819312323
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.45374834451199175,
        "upper_95": 0.6294225377860322
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.05683215350223546
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.07384647585971654
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
        "lower_95": 0.6154017141319884,
        "upper_95": 0.7754092963686385
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.07442085337852607
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.1094656408828239
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.6154017141319884,
        "upper_95": 0.7754092963686385
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.07442085337852607
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.1094656408828239
      }
    }
  },
  "empirical_test_fpr_resolution": 0.00390625,
  "experiment_sha256": "5883b09c763266d876d79319ba45fe8ffc649b4ded3e0b9a57ee7cee53620581",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.4500118255615234,
    "null_mean": 0.49987115783691405,
    "null_upper_95": 0.5502479553222657,
    "observed_auroc": 0.9299163818359375,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 48,
    "maximum_seconds": 52.82641899998998,
    "mean_seconds_per_artifact": 46.68435744166951,
    "minimum_seconds": 34.886896800016984,
    "total_seconds": 2240.8491572001367
  },
  "iters": 200,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": 0.11646252250495756,
      "model.decoder.layers.0.fc2": 0.13263644836097657,
      "model.decoder.layers.0.self_attn.k_proj": 0.10889592695904039,
      "model.decoder.layers.0.self_attn.out_proj": 0.004531795962852798,
      "model.decoder.layers.0.self_attn.q_proj": 0.05777705253936148,
      "model.decoder.layers.0.self_attn.v_proj": 0.10009416004804154,
      "model.decoder.layers.1.fc1": 0.02363553420385183,
      "model.decoder.layers.1.fc2": 0.03280448376507874,
      "model.decoder.layers.1.self_attn.k_proj": 0.0044866253796137685,
      "model.decoder.layers.1.self_attn.out_proj": -0.002702879177167772,
      "model.decoder.layers.1.self_attn.q_proj": -0.007707470728366696,
      "model.decoder.layers.1.self_attn.v_proj": 0.0724688081072826,
      "model.decoder.layers.10.fc1": 0.06591752438115779,
      "model.decoder.layers.10.fc2": 0.04653624298740111,
      "model.decoder.layers.10.self_attn.k_proj": -0.017720514842916854,
      "model.decoder.layers.10.self_attn.out_proj": 0.04917252533280664,
      "model.decoder.layers.10.self_attn.q_proj": -0.007234751644733885,
      "model.decoder.layers.10.self_attn.v_proj": 0.031621200475627956,
      "model.decoder.layers.11.fc1": 0.07156532124503448,
      "model.decoder.layers.11.fc2": 0.02669255838422557,
      "model.decoder.layers.11.self_attn.k_proj": -0.01802811262642039,
      "model.decoder.layers.11.self_attn.out_proj": 0.06973748217028317,
      "model.decoder.layers.11.self_attn.q_proj": -0.025934006492914753,
      "model.decoder.layers.11.self_attn.v_proj": 0.05130621873880088,
      "model.decoder.layers.2.fc1": 0.005064572772532229,
      "model.decoder.layers.2.fc2": 0.02474201350616098,
      "model.decoder.layers.2.self_attn.k_proj": 0.010633681920648636,
      "model.decoder.layers.2.self_attn.out_proj": 0.02159366568915396,
      "model.decoder.layers.2.self_attn.q_proj": 0.0018232959260794678,
      "model.decoder.layers.2.self_attn.v_proj": 0.05595943091073233,
      "model.decoder.layers.3.fc1": -0.0018118039192759213,
      "model.decoder.layers.3.fc2": 0.0216196005707568,
      "model.decoder.layers.3.self_attn.k_proj": -0.0206122157109079,
      "model.decoder.layers.3.self_attn.out_proj": 0.012429498808313129,
      "model.decoder.layers.3.self_attn.q_proj": 0.013852144494050823,
      "model.decoder.layers.3.self_attn.v_proj": 0.039541442601180324,
      "model.decoder.layers.4.fc1": 0.024886658008604932,
      "model.decoder.layers.4.fc2": 0.04871604486289858,
      "model.decoder.layers.4.self_attn.k_proj": -0.010343909867439428,
      "model.decoder.layers.4.self_attn.out_proj": 0.01771748338994431,
      "model.decoder.layers.4.self_attn.q_proj": 0.00439725992265155,
      "model.decoder.layers.4.self_attn.v_proj": 0.03877349783540675,
      "model.decoder.layers.5.fc1": 0.04710020808316441,
      "model.decoder.layers.5.fc2": 0.07126710851395111,
      "model.decoder.layers.5.self_attn.k_proj": 0.00844368949536092,
      "model.decoder.layers.5.self_attn.out_proj": 0.004898374839014141,
      "model.decoder.layers.5.self_attn.q_proj": 0.012923160712413305,
      "model.decoder.layers.5.self_attn.v_proj": 0.0027087318653608258,
      "model.decoder.layers.6.fc1": 0.03391662713462578,
      "model.decoder.layers.6.fc2": 0.07008955299427844,
      "model.decoder.layers.6.self_attn.k_proj": -0.002408274703824193,
      "model.decoder.layers.6.self_attn.out_proj": 0.02217284219030404,
      "model.decoder.layers.6.self_attn.q_proj": -0.011555285272078837,
      "model.decoder.layers.6.self_attn.v_proj": 0.009928118141248285,
      "model.decoder.layers.7.fc1": 0.049276775887079155,
      "model.decoder.layers.7.fc2": 0.04560276285556225,
      "model.decoder.layers.7.self_attn.k_proj": -0.008055426062547544,
      "model.decoder.layers.7.self_attn.out_proj": 0.008452110859996217,
      "model.decoder.layers.7.self_attn.q_proj": 0.0033787598464790005,
      "model.decoder.layers.7.self_attn.v_proj": 0.013947080062513112,
      "model.decoder.layers.8.fc1": 0.02851071496947918,
      "model.decoder.layers.8.fc2": 0.025726117618193677,
      "model.decoder.layers.8.self_attn.k_proj": -0.001713012523033871,
      "model.decoder.layers.8.self_attn.out_proj": 0.02994340037424134,
      "model.decoder.layers.8.self_attn.q_proj": 0.00016827123782683348,
      "model.decoder.layers.8.self_attn.v_proj": 0.019746520293245643,
      "model.decoder.layers.9.fc1": 0.04408088695928037,
      "model.decoder.layers.9.fc2": 0.024265578969966332,
      "model.decoder.layers.9.self_attn.k_proj": -0.011835419003820218,
      "model.decoder.layers.9.self_attn.out_proj": 0.05537253408194766,
      "model.decoder.layers.9.self_attn.q_proj": -0.00567815893105305,
      "model.decoder.layers.9.self_attn.v_proj": 0.04193197483940282
    },
    "regularization": 0.001,
    "shadow_split_auroc": 0.9091415405273438
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 0.7205810546875,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 0.01953125,
      "tpr_at_1pct_fpr": 0.07421875
    },
    {
      "auroc": 0.678314208984375,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.01953125,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.653411865234375,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.01953125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.6529693603515625,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.11328125
    },
    {
      "auroc": 0.6383209228515625,
      "layer": "model.decoder.layers.5.fc2",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.6158599853515625,
      "layer": "model.decoder.layers.11.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.046875
    },
    {
      "auroc": 0.5973663330078125,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.03125
    },
    {
      "auroc": 0.5886077880859375,
      "layer": "model.decoder.layers.6.fc2",
      "tpr_at_0_1pct_fpr": 0.04296875,
      "tpr_at_1pct_fpr": 0.05078125
    },
    {
      "auroc": 0.5877532958984375,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.03125,
      "tpr_at_1pct_fpr": 0.0390625
    },
    {
      "auroc": 0.5855255126953125,
      "layer": "model.decoder.layers.10.fc2",
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.046875
    },
    {
      "auroc": 0.5841064453125,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5794830322265625,
      "layer": "model.decoder.layers.9.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5757904052734375,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.570098876953125,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.5676727294921875,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.56451416015625,
      "layer": "model.decoder.layers.4.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0234375
    },
    {
      "auroc": 0.561065673828125,
      "layer": "model.decoder.layers.7.fc2",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.555908203125,
      "layer": "model.decoder.layers.11.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.5533599853515625,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5492706298828125,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.54779052734375,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0390625
    },
    {
      "auroc": 0.5459747314453125,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5433807373046875,
      "layer": "model.decoder.layers.7.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.543365478515625,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.54058837890625,
      "layer": "model.decoder.layers.8.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.537384033203125,
      "layer": "model.decoder.layers.1.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5364532470703125,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.534881591796875,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5335540771484375,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.03125
    },
    {
      "auroc": 0.5330810546875,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5283660888671875,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.046875
    },
    {
      "auroc": 0.52801513671875,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0234375,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.525909423828125,
      "layer": "model.decoder.layers.8.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.525146484375,
      "layer": "model.decoder.layers.6.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5244293212890625,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.523590087890625,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5234527587890625,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.52288818359375,
      "layer": "model.decoder.layers.4.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5222015380859375,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.521148681640625,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5183868408203125,
      "layer": "model.decoder.layers.3.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5183563232421875,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.518280029296875,
      "layer": "model.decoder.layers.1.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5154876708984375,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5136260986328125,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5120697021484375,
      "layer": "model.decoder.layers.10.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.511383056640625,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.01171875,
      "tpr_at_1pct_fpr": 0.015625
    },
    {
      "auroc": 0.5112762451171875,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.5067291259765625,
      "layer": "model.decoder.layers.2.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.5041046142578125,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.504058837890625,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.5030975341796875,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.50250244140625,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.01953125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5013885498046875,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.5009613037109375,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.5009002685546875,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.499420166015625,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.4983062744140625,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.03515625
    },
    {
      "auroc": 0.4981231689453125,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.497589111328125,
      "layer": "model.decoder.layers.3.fc2",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.4973602294921875,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.49420166015625,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.4937744140625,
      "layer": "model.decoder.layers.9.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.0078125
    },
    {
      "auroc": 0.4926605224609375,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.488677978515625,
      "layer": "model.decoder.layers.11.fc2",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.4860687255859375,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0
    },
    {
      "auroc": 0.4860382080078125,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.02734375
    },
    {
      "auroc": 0.478515625,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4769134521484375,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.0078125,
      "tpr_at_1pct_fpr": 0.01953125
    },
    {
      "auroc": 0.4729156494140625,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.00390625,
      "tpr_at_1pct_fpr": 0.01171875
    },
    {
      "auroc": 0.4676361083984375,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.4672088623046875,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.00390625
    }
  ],
  "library": "auto-round",
  "library_version": "0.14.2",
  "mean_changed_weight_fraction_vs_artifact0": null,
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 0.9299163818359375,
      "tpr_at_0_1pct_fpr": 0.2578125,
      "tpr_at_1pct_fpr": 0.28515625
    },
    "artifact_reconstruction": {
      "auroc": 0.544342041015625,
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.02734375
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
      "auroc": 0.6958465576171875,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    },
    "output_logprob_gap": {
      "auroc": 0.6958465576171875,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.0078125
    }
  },
  "model": "facebook/opt-125m",
  "model_revision": null,
  "output_combination": {
    "coefficients": {
      "output_kl": 3.406238026851052,
      "output_logit_mse": 3.239797156904072,
      "output_logprob": 0.08043033751039007,
      "output_logprob_gap": 0.08043033751039007
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
      "lower_quartile": 0.890625,
      "maximum": 1.0,
      "median": 0.953125,
      "minimum": 0.796875,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 23,
      "upper_quartile": 0.97265625
    },
    "artifact_reconstruction": {
      "lower_quartile": 0.46484375,
      "maximum": 0.859375,
      "median": 0.5390625,
      "minimum": 0.21875,
      "targets_above_chance": 23,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6328125
    },
    "output_combination": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 32,
      "upper_quartile": 1.0
    },
    "output_kl": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 32,
      "upper_quartile": 1.0
    },
    "output_logit_mse": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 32,
      "upper_quartile": 1.0
    },
    "output_logprob": {
      "lower_quartile": 0.57421875,
      "maximum": 1.0,
      "median": 0.6953125,
      "minimum": 0.296875,
      "targets_above_chance": 27,
      "targets_at_least_0_9": 3,
      "upper_quartile": 0.8203125
    },
    "output_logprob_gap": {
      "lower_quartile": 0.57421875,
      "maximum": 1.0,
      "median": 0.6953125,
      "minimum": 0.296875,
      "targets_above_chance": 27,
      "targets_at_least_0_9": 3,
      "upper_quartile": 0.8203125
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
    "artifact_logprob_change_std": 0.009825772456026668,
    "base_mean_logprob": -9.6803018450737,
    "base_perplexity": 15999.325515845434,
    "mean_logprob_change": 0.006728488951921463,
    "perplexity_ratio_quantized_over_base": 0.993294096645828,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -9.673573356121778,
    "quantized_perplexity": 15892.035585204236,
    "reference_decisions": 768
  },
  "selected_artifact_feature": "artifact_layer_combination",
  "selected_output_baseline": "output_logit_mse",
  "sequence_length": 512,
  "shadow_artifacts": 32,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.02734375,
        "test_tpr": 0.578125,
        "test_true_positives": 148,
        "threshold": 0.9583286899346569
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 5,
        "test_fpr": 0.01953125,
        "test_tpr": 0.02734375,
        "test_true_positives": 7,
        "threshold": 1.9977284394862114
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 2,
        "test_fpr": 0.0078125,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -0.739867669240653
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 2,
        "test_fpr": 0.0078125,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -0.5864190007821125
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 2,
        "test_fpr": 0.0078125,
        "test_tpr": 1.0,
        "test_true_positives": 256,
        "threshold": -0.4101715450262219
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 6,
        "test_fpr": 0.0234375,
        "test_tpr": 0.0390625,
        "test_true_positives": 10,
        "threshold": 2.1765490885351304
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 6,
        "test_fpr": 0.0234375,
        "test_tpr": 0.0390625,
        "test_true_positives": 10,
        "threshold": 2.1765490885351304
      }
    }
  },
  "shadow_metrics": {
    "artifact_layer_combination": {
      "auroc": 0.9382553100585938,
      "tpr_at_0_1pct_fpr": 0.34375,
      "tpr_at_1pct_fpr": 0.5703125
    },
    "artifact_reconstruction": {
      "auroc": 0.5989570617675781,
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.02734375
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
      "auroc": 0.7152824401855469,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01953125
    },
    "output_logprob_gap": {
      "auroc": 0.7152824401855469,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.01953125
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
