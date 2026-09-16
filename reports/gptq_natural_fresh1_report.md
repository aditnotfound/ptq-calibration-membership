# CalibTrace named-library attack report

Library `llm-compressor` 0.13.0 quantizes `facebook/opt-125m` to W4A16 from 16 shadow and 16 held-out calibration assignments of N=128 sequences of 512 tokens, tracking 64 candidate records.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.9999 | 1.0000 | 0.9844 |
| artifact_layer_combination | 1.0000 | 1.0000 | 1.0000 |
| output_logit_mse | 0.8646 | 0.3535 | 0.0625 |
| output_kl | 0.6962 | 0.0586 | 0.0000 |
| output_logprob | 0.4972 | 0.0156 | 0.0000 |
| output_logprob_gap | 0.4972 | 0.0156 | 0.0000 |
| output_combination | 0.8647 | 0.3691 | 0.0625 |

Selected artifact feature `artifact_layer_combination` minus selected output baseline `output_combination`: 0.1353 AUROC, crossed-bootstrap 95% interval [0.0964, 0.1806]. Both features were selected on shadow artifacts only. A negative value indicates that the selected output feature has higher AUROC in this configuration.

## Public-reference utility

Across 512 calibration-excluded reference scores, mean token log probability changes by -0.048117; the corresponding perplexity ratio is 1.049294.

## Generation runtime

The 32 quantize-and-score jobs took 30.3 minutes in aggregate, with mean 56.8 seconds per artifact.

## Layerwise localization

| Layer | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| model.decoder.layers.1.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.1.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.10.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.10.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.11.fc1 | 1.0000 | 1.0000 |
| model.decoder.layers.11.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.11.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.2.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.3.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.3.self_attn.out_proj | 1.0000 | 1.0000 |
| model.decoder.layers.4.fc2 | 1.0000 | 1.0000 |
| model.decoder.layers.4.self_attn.out_proj | 1.0000 | 1.0000 |

## Unseen-candidate generalization

Candidate-fold cross-fitting uses one global direction, midpoint, and scale pooled over the other candidates. The evaluated candidate contributes no shadow score, label, normalization statistic, feature weight, or selection decision.

| Feature | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| artifact_reconstruction | 0.6639 | 0.0684 |
| artifact_layer_combination | 0.9999 | 1.0000 |
| selected_artifact | 0.9999 | 1.0000 |
| selected_output | 0.6320 | 0.0293 |

## Fit-free fixed score

This ablation applies the predefined negative residual-energy score directly, with no learned direction, normalization, layer weighting, or feature selection.

| Variant | AUROC | ROC TPR @ FPR<=1% |
|---|---:|---:|
| raw_fixed_formula | 0.6684 | 0.0977 |
| reference_corrected_fixed_formula | 0.6687 | 0.0996 |

## Held-out artifact distribution

For artifact_layer_combination, per-artifact AUROC has minimum 1.0000, median 1.0000, and maximum 1.0000 across 16 test artifacts.


Fixed-degree randomization test for the selected artifact score: p=0.000100 (10000 random assignments).

Full metrics and metadata:

```json
{
  "artifact_minus_output_combination_auroc": 0.135345458984375,
  "bits": 4,
  "calibration_size": 128,
  "candidate_generalization": {
    "artifact_minus_output_auroc": 0.36795806884765625,
    "cluster_bootstrap": {
      "artifact_layer_combination": {
        "auroc": {
          "lower_95": 0.9996791197779882,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9653829479768786,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9844350391759772,
          "upper_95": 1.0
        }
      },
      "artifact_minus_selected_output_auroc": {
        "lower_95": 0.3103793859158317,
        "upper_95": 0.41650359316131524
      },
      "artifact_reconstruction": {
        "auroc": {
          "lower_95": 0.6028659402096171,
          "upper_95": 0.7282182401737334
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.017427952790261356,
          "upper_95": 0.14805020268276955
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.024332251521298174,
          "upper_95": 0.17229722010662601
        }
      },
      "output_combination": {
        "auroc": {
          "lower_95": 0.5707896176642062,
          "upper_95": 0.6830668406205668
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.003983472052384521,
          "upper_95": 0.07810364145658262
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.007811362257281553,
          "upper_95": 0.13320688425034843
        }
      },
      "output_kl": {
        "auroc": {
          "lower_95": 0.5564322982024485,
          "upper_95": 0.6648408672444577
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.00205761316872428,
          "upper_95": 0.06615431967412451
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.009231354890193557,
          "upper_95": 0.08478551555416976
        }
      },
      "output_logit_mse": {
        "auroc": {
          "lower_95": 0.5834517414852559,
          "upper_95": 0.6896165115648525
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.003898445855234714,
          "upper_95": 0.07755517932104909
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.00946880360205832,
          "upper_95": 0.12348409045427255
        }
      },
      "output_logprob": {
        "auroc": {
          "lower_95": 0.4615573935077005,
          "upper_95": 0.5466988557138853
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.02581549593005727
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.03854505715678412
        }
      },
      "output_logprob_gap": {
        "auroc": {
          "lower_95": 0.4824529645336699,
          "upper_95": 0.5894663528834694
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.03475921513030887
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.0,
          "upper_95": 0.08052278973889142
        }
      },
      "selected_artifact": {
        "auroc": {
          "lower_95": 0.9996791197779882,
          "upper_95": 1.0
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.9653829479768786,
          "upper_95": 1.0
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.9844350391759772,
          "upper_95": 1.0
        }
      },
      "selected_output": {
        "auroc": {
          "lower_95": 0.5834517414852559,
          "upper_95": 0.6896165115648525
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.003898445855234714,
          "upper_95": 0.07755517932104909
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.00946880360205832,
          "upper_95": 0.12348409045427255
        }
      }
    },
    "excluded_identity_shadow_scores_used": false,
    "excluded_identity_test_scores_used_for_fitting": false,
    "folds": 2,
    "metrics": {
      "artifact_layer_combination": {
        "auroc": 0.9999465942382812,
        "tpr_at_0_1pct_fpr": 0.98828125,
        "tpr_at_1pct_fpr": 1.0
      },
      "artifact_reconstruction": {
        "auroc": 0.6639328002929688,
        "tpr_at_0_1pct_fpr": 0.044921875,
        "tpr_at_1pct_fpr": 0.068359375
      },
      "output_combination": {
        "auroc": 0.623443603515625,
        "tpr_at_0_1pct_fpr": 0.01171875,
        "tpr_at_1pct_fpr": 0.017578125
      },
      "output_kl": {
        "auroc": 0.6095657348632812,
        "tpr_at_0_1pct_fpr": 0.01953125,
        "tpr_at_1pct_fpr": 0.0390625
      },
      "output_logit_mse": {
        "auroc": 0.631988525390625,
        "tpr_at_0_1pct_fpr": 0.009765625,
        "tpr_at_1pct_fpr": 0.029296875
      },
      "output_logprob": {
        "auroc": 0.5039901733398438,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.013671875
      },
      "output_logprob_gap": {
        "auroc": 0.5365791320800781,
        "tpr_at_0_1pct_fpr": 0.0,
        "tpr_at_1pct_fpr": 0.001953125
      },
      "selected_artifact": {
        "auroc": 0.9999465942382812,
        "tpr_at_0_1pct_fpr": 0.98828125,
        "tpr_at_1pct_fpr": 1.0
      },
      "selected_output": {
        "auroc": 0.631988525390625,
        "tpr_at_0_1pct_fpr": 0.009765625,
        "tpr_at_1pct_fpr": 0.029296875
      }
    },
    "normalization": "one fold-global direction, midpoint, and scale pooled over shadow scores from training-fold candidates only",
    "per_artifact_auroc": {
      "artifact_layer_combination": {
        "artifacts": 16,
        "artifacts_above_chance": 16,
        "artifacts_at_least_0_9": 16,
        "lower_quartile": 1.0,
        "maximum": 1.0,
        "median": 1.0,
        "minimum": 0.9990234375,
        "upper_quartile": 1.0,
        "values": [
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          0.9990234375,
          1.0
        ]
      },
      "artifact_reconstruction": {
        "artifacts": 16,
        "artifacts_above_chance": 15,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.62451171875,
        "maximum": 0.8837890625,
        "median": 0.6630859375,
        "minimum": 0.4931640625,
        "upper_quartile": 0.68408203125,
        "values": [
          0.6337890625,
          0.6337890625,
          0.587890625,
          0.7392578125,
          0.6748046875,
          0.4931640625,
          0.5966796875,
          0.6767578125,
          0.6591796875,
          0.5439453125,
          0.6474609375,
          0.6826171875,
          0.8837890625,
          0.6669921875,
          0.6884765625,
          0.7158203125
        ]
      },
      "output_combination": {
        "artifacts": 16,
        "artifacts_above_chance": 15,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.5830078125,
        "maximum": 0.76953125,
        "median": 0.5966796875,
        "minimum": 0.5,
        "upper_quartile": 0.6591796875,
        "values": [
          0.591796875,
          0.54296875,
          0.708984375,
          0.6796875,
          0.58984375,
          0.5185546875,
          0.6025390625,
          0.65234375,
          0.57421875,
          0.5,
          0.587890625,
          0.74609375,
          0.76953125,
          0.6015625,
          0.6455078125,
          0.5859375
        ]
      },
      "output_kl": {
        "artifacts": 16,
        "artifacts_above_chance": 15,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.546630859375,
        "maximum": 0.73828125,
        "median": 0.62158203125,
        "minimum": 0.482421875,
        "upper_quartile": 0.637451171875,
        "values": [
          0.482421875,
          0.5205078125,
          0.62890625,
          0.6484375,
          0.55078125,
          0.501953125,
          0.630859375,
          0.6337890625,
          0.6044921875,
          0.5341796875,
          0.6298828125,
          0.7177734375,
          0.73828125,
          0.603515625,
          0.6142578125,
          0.7001953125
        ]
      },
      "output_logit_mse": {
        "artifacts": 16,
        "artifacts_above_chance": 16,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.5869140625,
        "maximum": 0.7958984375,
        "median": 0.60791015625,
        "minimum": 0.5009765625,
        "upper_quartile": 0.67333984375,
        "values": [
          0.587890625,
          0.5498046875,
          0.693359375,
          0.68359375,
          0.587890625,
          0.5009765625,
          0.6103515625,
          0.66796875,
          0.583984375,
          0.541015625,
          0.59765625,
          0.7431640625,
          0.7958984375,
          0.6064453125,
          0.669921875,
          0.609375
        ]
      },
      "output_logprob": {
        "artifacts": 16,
        "artifacts_above_chance": 7,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.46484375,
        "maximum": 0.603515625,
        "median": 0.48974609375,
        "minimum": 0.4130859375,
        "upper_quartile": 0.5361328125,
        "values": [
          0.46875,
          0.447265625,
          0.5263671875,
          0.603515625,
          0.5810546875,
          0.494140625,
          0.48046875,
          0.453125,
          0.5126953125,
          0.5068359375,
          0.4130859375,
          0.5654296875,
          0.4423828125,
          0.5791015625,
          0.4853515625,
          0.482421875
        ]
      },
      "output_logprob_gap": {
        "artifacts": 16,
        "artifacts_above_chance": 11,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.491943359375,
        "maximum": 0.6396484375,
        "median": 0.5380859375,
        "minimum": 0.375,
        "upper_quartile": 0.60009765625,
        "values": [
          0.5458984375,
          0.5703125,
          0.5908203125,
          0.5986328125,
          0.375,
          0.630859375,
          0.6396484375,
          0.4970703125,
          0.517578125,
          0.4765625,
          0.5302734375,
          0.6142578125,
          0.6044921875,
          0.5166015625,
          0.44140625,
          0.453125
        ]
      },
      "selected_artifact": {
        "artifacts": 16,
        "artifacts_above_chance": 16,
        "artifacts_at_least_0_9": 16,
        "lower_quartile": 1.0,
        "maximum": 1.0,
        "median": 1.0,
        "minimum": 0.9990234375,
        "upper_quartile": 1.0,
        "values": [
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          0.9990234375,
          1.0
        ]
      },
      "selected_output": {
        "artifacts": 16,
        "artifacts_above_chance": 16,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.5869140625,
        "maximum": 0.7958984375,
        "median": 0.60791015625,
        "minimum": 0.5009765625,
        "upper_quartile": 0.67333984375,
        "values": [
          0.587890625,
          0.5498046875,
          0.693359375,
          0.68359375,
          0.587890625,
          0.5009765625,
          0.6103515625,
          0.66796875,
          0.583984375,
          0.541015625,
          0.59765625,
          0.7431640625,
          0.7958984375,
          0.6064453125,
          0.669921875,
          0.609375
        ]
      }
    },
    "protocol": "candidate-fold cross-fitting: all score directions, scales, feature combinations, and feature choices exclude the evaluated candidate",
    "seed": 20261003,
    "selections": [
      {
        "fold": 0,
        "held_out_candidates": [
          46,
          30,
          50,
          19,
          48,
          17,
          12,
          61,
          13,
          22,
          56,
          0,
          29,
          32,
          25,
          40,
          34,
          15,
          57,
          60,
          45,
          3,
          51,
          38,
          9,
          23,
          7,
          59,
          39,
          52,
          31,
          62
        ],
        "held_out_prediction_sha256": "4903b94ceb67c27acf38c3a95dbd9381512067025947e2c01ebadda028c8ff8c",
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 0.1,
        "output_validation_auroc": 0.6528998778998779,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_logit_mse",
        "training_candidates": [
          1,
          2,
          4,
          5,
          6,
          8,
          10,
          11,
          14,
          16,
          18,
          20,
          21,
          24,
          26,
          27,
          28,
          33,
          35,
          36,
          37,
          41,
          42,
          43,
          44,
          47,
          49,
          53,
          54,
          55,
          58,
          63
        ]
      },
      {
        "fold": 1,
        "held_out_candidates": [
          18,
          42,
          54,
          49,
          63,
          16,
          53,
          47,
          2,
          35,
          11,
          58,
          55,
          20,
          37,
          28,
          24,
          1,
          10,
          44,
          5,
          41,
          6,
          36,
          33,
          27,
          21,
          14,
          4,
          43,
          8,
          26
        ],
        "held_out_prediction_sha256": "fffe60b6bd83b8d4dc1d90bed0efc261cfb590f8fc50d98d4928c2aa6389e333",
        "layer_regularization": 1.0,
        "layer_validation_auroc": 1.0,
        "output_regularization": 0.01,
        "output_validation_auroc": 0.6326312576312576,
        "selected_artifact_feature": "artifact_layer_combination",
        "selected_output_feature": "output_logit_mse",
        "training_candidates": [
          0,
          3,
          7,
          9,
          12,
          13,
          15,
          17,
          19,
          22,
          23,
          25,
          29,
          30,
          31,
          32,
          34,
          38,
          39,
          40,
          45,
          46,
          48,
          50,
          51,
          52,
          56,
          57,
          59,
          60,
          61,
          62
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
      "lower_95": 0.0963887089984771,
      "upper_95": 0.18061026024586216
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.9994048593441212,
        "upper_95": 1.0
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.9626700686849311,
        "upper_95": 1.0
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.9705882352941176,
        "upper_95": 1.0
      }
    },
    "output_combination": {
      "auroc": {
        "lower_95": 0.8193897397541379,
        "upper_95": 0.9036112910015229
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.032747775211340265,
        "upper_95": 0.40274412684200134
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.05356877652050919,
        "upper_95": 0.4952054794520547
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.6349428363058739,
        "upper_95": 0.7549004425655517
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.1222879684418146
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.17728442473671707
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.8192344583670096,
        "upper_95": 0.9034724795467179
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.031738235569276824,
        "upper_95": 0.4035832663720369
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.05189950980392157,
        "upper_95": 0.4990216217865821
      }
    },
    "output_logprob": {
      "auroc": {
        "lower_95": 0.4345657049215878,
        "upper_95": 0.5636949335802082
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.02353289244691959
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.042345150657593394
      }
    },
    "output_logprob_gap": {
      "auroc": {
        "lower_95": 0.4345657049215878,
        "upper_95": 0.5636949335802082
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.02353289244691959
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.042345150657593394
      }
    }
  },
  "empirical_test_fpr_resolution": 0.001953125,
  "experiment_sha256": "08d1834cc8be36cba1afe2cfd602c8fe460245ce535eae52d66573afdb957e31",
  "feature_selection": "highest shadow-split AUROC, chosen without any held-out label",
  "fit_free_fixed_score": {
    "cluster_bootstrap": {
      "artifact_minus_raw_fixed_formula_auroc": {
        "lower_95": -0.0012897137518823765,
        "upper_95": 0.0017704071310850969
      },
      "raw_fixed_formula": {
        "auroc": {
          "lower_95": 0.6112481561023865,
          "upper_95": 0.7320245003427434
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.02451270390137563,
          "upper_95": 0.21805490680609338
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.037945293759621926,
          "upper_95": 0.2381952242684805
        }
      },
      "reference_corrected_fixed_formula": {
        "auroc": {
          "lower_95": 0.6121587530245635,
          "upper_95": 0.7325465052010732
        },
        "tpr_at_0_1pct_fpr": {
          "lower_95": 0.02143834764215503,
          "upper_95": 0.2103425426774483
        },
        "tpr_at_1pct_fpr": {
          "lower_95": 0.037926022046825505,
          "upper_95": 0.23153094180544806
        }
      }
    },
    "metrics": {
      "raw_fixed_formula": {
        "auroc": 0.6684455871582031,
        "tpr_at_0_1pct_fpr": 0.05078125,
        "tpr_at_1pct_fpr": 0.09765625
      },
      "reference_corrected_fixed_formula": {
        "auroc": 0.668701171875,
        "tpr_at_0_1pct_fpr": 0.05078125,
        "tpr_at_1pct_fpr": 0.099609375
      }
    },
    "per_artifact_auroc": {
      "raw_fixed_formula": {
        "artifacts": 16,
        "artifacts_above_chance": 16,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.623779296875,
        "maximum": 0.8837890625,
        "median": 0.66650390625,
        "minimum": 0.505859375,
        "upper_quartile": 0.686767578125,
        "values": [
          0.626953125,
          0.6640625,
          0.6142578125,
          0.744140625,
          0.67578125,
          0.505859375,
          0.5908203125,
          0.6845703125,
          0.6689453125,
          0.5419921875,
          0.6494140625,
          0.693359375,
          0.8837890625,
          0.66015625,
          0.6806640625,
          0.712890625
        ]
      },
      "reference_corrected_fixed_formula": {
        "artifacts": 16,
        "artifacts_above_chance": 16,
        "artifacts_at_least_0_9": 0,
        "lower_quartile": 0.623779296875,
        "maximum": 0.8837890625,
        "median": 0.66650390625,
        "minimum": 0.505859375,
        "upper_quartile": 0.686767578125,
        "values": [
          0.626953125,
          0.6640625,
          0.6142578125,
          0.744140625,
          0.67578125,
          0.505859375,
          0.5908203125,
          0.6845703125,
          0.6689453125,
          0.5419921875,
          0.6494140625,
          0.693359375,
          0.8837890625,
          0.66015625,
          0.6806640625,
          0.712890625
        ]
      }
    },
    "protocol": "predefined negative residual-energy score; no fitted direction, location, scale, layer combination, regularization, or feature selection"
  },
  "fixed_degree_randomization_test": {
    "null_lower_95": 0.46393117904663084,
    "null_mean": 0.4999391986846924,
    "null_upper_95": 0.5353434562683106,
    "observed_auroc": 1.0,
    "p_value_greater_equal": 9.999000099990002e-05,
    "replicates": 10000
  },
  "generation_runtime": {
    "artifacts": 32,
    "maximum_seconds": 84.3771772000473,
    "mean_seconds_per_artifact": 56.799706981248164,
    "minimum_seconds": 40.39136049989611,
    "total_seconds": 1817.5906233999413
  },
  "iters": 0,
  "layer_combination": {
    "coefficients": {
      "model.decoder.layers.0.fc1": -0.016825042911055132,
      "model.decoder.layers.0.fc2": 0.3192485016535892,
      "model.decoder.layers.0.self_attn.k_proj": -0.044647219383193784,
      "model.decoder.layers.0.self_attn.out_proj": 0.2746929897196598,
      "model.decoder.layers.0.self_attn.q_proj": -0.032782402441983334,
      "model.decoder.layers.0.self_attn.v_proj": -0.00695060688916673,
      "model.decoder.layers.1.fc1": -0.057235324608796656,
      "model.decoder.layers.1.fc2": 0.295435692138214,
      "model.decoder.layers.1.self_attn.k_proj": 0.04835233350008938,
      "model.decoder.layers.1.self_attn.out_proj": 0.2948464049191039,
      "model.decoder.layers.1.self_attn.q_proj": 0.004076043175725292,
      "model.decoder.layers.1.self_attn.v_proj": 0.011246034243778711,
      "model.decoder.layers.10.fc1": 0.10210647293609201,
      "model.decoder.layers.10.fc2": 0.3034666395712045,
      "model.decoder.layers.10.self_attn.k_proj": 0.06850906950914001,
      "model.decoder.layers.10.self_attn.out_proj": 0.3210103588979588,
      "model.decoder.layers.10.self_attn.q_proj": 0.10773890188564304,
      "model.decoder.layers.10.self_attn.v_proj": 0.03708894414219921,
      "model.decoder.layers.11.fc1": 0.20468234638683983,
      "model.decoder.layers.11.fc2": 0.30841873542278914,
      "model.decoder.layers.11.self_attn.k_proj": 0.11340309600869848,
      "model.decoder.layers.11.self_attn.out_proj": 0.3791614134039567,
      "model.decoder.layers.11.self_attn.q_proj": 0.09849230453962894,
      "model.decoder.layers.11.self_attn.v_proj": 0.013296380978263128,
      "model.decoder.layers.2.fc1": -0.002499770974328199,
      "model.decoder.layers.2.fc2": 0.2358879867154444,
      "model.decoder.layers.2.self_attn.k_proj": 0.05202922976651806,
      "model.decoder.layers.2.self_attn.out_proj": 0.26092204845232303,
      "model.decoder.layers.2.self_attn.q_proj": 0.07125130565354468,
      "model.decoder.layers.2.self_attn.v_proj": 0.044675470227363394,
      "model.decoder.layers.3.fc1": 0.01868455947660547,
      "model.decoder.layers.3.fc2": 0.27480819085788105,
      "model.decoder.layers.3.self_attn.k_proj": -0.026877196469644808,
      "model.decoder.layers.3.self_attn.out_proj": 0.204827114102465,
      "model.decoder.layers.3.self_attn.q_proj": -0.005505110432635303,
      "model.decoder.layers.3.self_attn.v_proj": 0.026020473854699952,
      "model.decoder.layers.4.fc1": 0.02374346512171651,
      "model.decoder.layers.4.fc2": 0.34552246450481255,
      "model.decoder.layers.4.self_attn.k_proj": 0.02999682868351486,
      "model.decoder.layers.4.self_attn.out_proj": 0.2564164931776108,
      "model.decoder.layers.4.self_attn.q_proj": -0.009700385936853897,
      "model.decoder.layers.4.self_attn.v_proj": 0.0414281827937357,
      "model.decoder.layers.5.fc1": -0.01853884899221225,
      "model.decoder.layers.5.fc2": 0.290077323214767,
      "model.decoder.layers.5.self_attn.k_proj": 0.06371348176296518,
      "model.decoder.layers.5.self_attn.out_proj": 0.1740240161958305,
      "model.decoder.layers.5.self_attn.q_proj": 0.04346710780589985,
      "model.decoder.layers.5.self_attn.v_proj": -0.007233849398715162,
      "model.decoder.layers.6.fc1": 0.022064736538962026,
      "model.decoder.layers.6.fc2": 0.371926753867616,
      "model.decoder.layers.6.self_attn.k_proj": 0.03294657409554713,
      "model.decoder.layers.6.self_attn.out_proj": 0.29316741162367843,
      "model.decoder.layers.6.self_attn.q_proj": 0.0006077513126504031,
      "model.decoder.layers.6.self_attn.v_proj": -0.040530745213012614,
      "model.decoder.layers.7.fc1": 0.08865947696846957,
      "model.decoder.layers.7.fc2": 0.3247838513976115,
      "model.decoder.layers.7.self_attn.k_proj": 0.09649509030855963,
      "model.decoder.layers.7.self_attn.out_proj": 0.28929003830591893,
      "model.decoder.layers.7.self_attn.q_proj": 0.1354493184535472,
      "model.decoder.layers.7.self_attn.v_proj": 0.06478982943932997,
      "model.decoder.layers.8.fc1": 0.07367155114741639,
      "model.decoder.layers.8.fc2": 0.35253122582471547,
      "model.decoder.layers.8.self_attn.k_proj": 0.08960283258449113,
      "model.decoder.layers.8.self_attn.out_proj": 0.2603912737009896,
      "model.decoder.layers.8.self_attn.q_proj": 0.11075646127378481,
      "model.decoder.layers.8.self_attn.v_proj": 0.10231940046165226,
      "model.decoder.layers.9.fc1": 0.06583157795777773,
      "model.decoder.layers.9.fc2": 0.3105529300857846,
      "model.decoder.layers.9.self_attn.k_proj": 0.13521185206054376,
      "model.decoder.layers.9.self_attn.out_proj": 0.2913228825548111,
      "model.decoder.layers.9.self_attn.q_proj": 0.12972993225071355,
      "model.decoder.layers.9.self_attn.v_proj": 0.05140973911522753
    },
    "regularization": 1.0,
    "shadow_split_auroc": 1.0
  },
  "layerwise_artifact_reconstruction": [
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
      "auroc": 0.9999923706054688,
      "layer": "model.decoder.layers.2.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.99609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999732971191406,
      "layer": "model.decoder.layers.5.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9999656677246094,
      "layer": "model.decoder.layers.10.fc1",
      "tpr_at_0_1pct_fpr": 0.98828125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.999908447265625,
      "layer": "model.decoder.layers.9.fc1",
      "tpr_at_0_1pct_fpr": 0.970703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998512268066406,
      "layer": "model.decoder.layers.6.fc1",
      "tpr_at_0_1pct_fpr": 0.9609375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998435974121094,
      "layer": "model.decoder.layers.7.fc1",
      "tpr_at_0_1pct_fpr": 0.95703125,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998207092285156,
      "layer": "model.decoder.layers.8.fc1",
      "tpr_at_0_1pct_fpr": 0.951171875,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.99969482421875,
      "layer": "model.decoder.layers.11.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.955078125,
      "tpr_at_1pct_fpr": 0.9921875
    },
    {
      "auroc": 0.9996261596679688,
      "layer": "model.decoder.layers.5.fc1",
      "tpr_at_0_1pct_fpr": 0.896484375,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9995803833007812,
      "layer": "model.decoder.layers.11.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.896484375,
      "tpr_at_1pct_fpr": 0.998046875
    },
    {
      "auroc": 0.9991836547851562,
      "layer": "model.decoder.layers.10.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.890625,
      "tpr_at_1pct_fpr": 0.990234375
    },
    {
      "auroc": 0.9991722106933594,
      "layer": "model.decoder.layers.10.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.849609375,
      "tpr_at_1pct_fpr": 0.984375
    },
    {
      "auroc": 0.9991416931152344,
      "layer": "model.decoder.layers.0.fc2",
      "tpr_at_0_1pct_fpr": 0.994140625,
      "tpr_at_1pct_fpr": 0.994140625
    },
    {
      "auroc": 0.9989967346191406,
      "layer": "model.decoder.layers.11.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.904296875,
      "tpr_at_1pct_fpr": 0.978515625
    },
    {
      "auroc": 0.9988365173339844,
      "layer": "model.decoder.layers.9.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.87890625,
      "tpr_at_1pct_fpr": 0.984375
    },
    {
      "auroc": 0.9986724853515625,
      "layer": "model.decoder.layers.10.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.87109375,
      "tpr_at_1pct_fpr": 0.97265625
    },
    {
      "auroc": 0.998565673828125,
      "layer": "model.decoder.layers.9.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.87109375,
      "tpr_at_1pct_fpr": 0.96875
    },
    {
      "auroc": 0.9984970092773438,
      "layer": "model.decoder.layers.7.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.701171875,
      "tpr_at_1pct_fpr": 0.966796875
    },
    {
      "auroc": 0.998321533203125,
      "layer": "model.decoder.layers.5.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.759765625,
      "tpr_at_1pct_fpr": 0.970703125
    },
    {
      "auroc": 0.998138427734375,
      "layer": "model.decoder.layers.8.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.796875,
      "tpr_at_1pct_fpr": 0.986328125
    },
    {
      "auroc": 0.9980087280273438,
      "layer": "model.decoder.layers.4.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.6640625,
      "tpr_at_1pct_fpr": 0.966796875
    },
    {
      "auroc": 0.9978446960449219,
      "layer": "model.decoder.layers.0.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.625,
      "tpr_at_1pct_fpr": 0.978515625
    },
    {
      "auroc": 0.997711181640625,
      "layer": "model.decoder.layers.5.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.701171875,
      "tpr_at_1pct_fpr": 0.9609375
    },
    {
      "auroc": 0.9976615905761719,
      "layer": "model.decoder.layers.6.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.849609375,
      "tpr_at_1pct_fpr": 0.953125
    },
    {
      "auroc": 0.99749755859375,
      "layer": "model.decoder.layers.6.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.607421875,
      "tpr_at_1pct_fpr": 0.974609375
    },
    {
      "auroc": 0.9973258972167969,
      "layer": "model.decoder.layers.8.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.662109375,
      "tpr_at_1pct_fpr": 0.9609375
    },
    {
      "auroc": 0.9972190856933594,
      "layer": "model.decoder.layers.2.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.751953125,
      "tpr_at_1pct_fpr": 0.931640625
    },
    {
      "auroc": 0.9971580505371094,
      "layer": "model.decoder.layers.6.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.6875,
      "tpr_at_1pct_fpr": 0.974609375
    },
    {
      "auroc": 0.9971351623535156,
      "layer": "model.decoder.layers.0.self_attn.out_proj",
      "tpr_at_0_1pct_fpr": 0.818359375,
      "tpr_at_1pct_fpr": 0.939453125
    },
    {
      "auroc": 0.9970893859863281,
      "layer": "model.decoder.layers.5.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.677734375,
      "tpr_at_1pct_fpr": 0.9453125
    },
    {
      "auroc": 0.9969329833984375,
      "layer": "model.decoder.layers.3.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.74609375,
      "tpr_at_1pct_fpr": 0.9375
    },
    {
      "auroc": 0.9967689514160156,
      "layer": "model.decoder.layers.4.fc1",
      "tpr_at_0_1pct_fpr": 0.703125,
      "tpr_at_1pct_fpr": 0.935546875
    },
    {
      "auroc": 0.9964942932128906,
      "layer": "model.decoder.layers.9.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.470703125,
      "tpr_at_1pct_fpr": 0.919921875
    },
    {
      "auroc": 0.9964714050292969,
      "layer": "model.decoder.layers.3.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.736328125,
      "tpr_at_1pct_fpr": 0.90625
    },
    {
      "auroc": 0.9964332580566406,
      "layer": "model.decoder.layers.4.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.736328125,
      "tpr_at_1pct_fpr": 0.943359375
    },
    {
      "auroc": 0.9963226318359375,
      "layer": "model.decoder.layers.3.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.775390625,
      "tpr_at_1pct_fpr": 0.90234375
    },
    {
      "auroc": 0.9963111877441406,
      "layer": "model.decoder.layers.8.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.69140625,
      "tpr_at_1pct_fpr": 0.8984375
    },
    {
      "auroc": 0.9962882995605469,
      "layer": "model.decoder.layers.1.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.66015625,
      "tpr_at_1pct_fpr": 0.943359375
    },
    {
      "auroc": 0.9961929321289062,
      "layer": "model.decoder.layers.4.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.646484375,
      "tpr_at_1pct_fpr": 0.8828125
    },
    {
      "auroc": 0.9961700439453125,
      "layer": "model.decoder.layers.0.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.662109375,
      "tpr_at_1pct_fpr": 0.92578125
    },
    {
      "auroc": 0.9959678649902344,
      "layer": "model.decoder.layers.1.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.5234375,
      "tpr_at_1pct_fpr": 0.931640625
    },
    {
      "auroc": 0.99578857421875,
      "layer": "model.decoder.layers.1.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.65234375,
      "tpr_at_1pct_fpr": 0.9296875
    },
    {
      "auroc": 0.9957084655761719,
      "layer": "model.decoder.layers.2.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.6953125,
      "tpr_at_1pct_fpr": 0.9375
    },
    {
      "auroc": 0.9955863952636719,
      "layer": "model.decoder.layers.7.self_attn.q_proj",
      "tpr_at_0_1pct_fpr": 0.720703125,
      "tpr_at_1pct_fpr": 0.93359375
    },
    {
      "auroc": 0.9955825805664062,
      "layer": "model.decoder.layers.2.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.6875,
      "tpr_at_1pct_fpr": 0.904296875
    },
    {
      "auroc": 0.9955596923828125,
      "layer": "model.decoder.layers.1.fc1",
      "tpr_at_0_1pct_fpr": 0.607421875,
      "tpr_at_1pct_fpr": 0.890625
    },
    {
      "auroc": 0.9954147338867188,
      "layer": "model.decoder.layers.0.fc1",
      "tpr_at_0_1pct_fpr": 0.67578125,
      "tpr_at_1pct_fpr": 0.935546875
    },
    {
      "auroc": 0.9952468872070312,
      "layer": "model.decoder.layers.0.self_attn.v_proj",
      "tpr_at_0_1pct_fpr": 0.572265625,
      "tpr_at_1pct_fpr": 0.919921875
    },
    {
      "auroc": 0.9949455261230469,
      "layer": "model.decoder.layers.7.self_attn.k_proj",
      "tpr_at_0_1pct_fpr": 0.76171875,
      "tpr_at_1pct_fpr": 0.892578125
    },
    {
      "auroc": 0.9898567199707031,
      "layer": "model.decoder.layers.2.fc1",
      "tpr_at_0_1pct_fpr": 0.4921875,
      "tpr_at_1pct_fpr": 0.830078125
    },
    {
      "auroc": 0.9838638305664062,
      "layer": "model.decoder.layers.3.fc1",
      "tpr_at_0_1pct_fpr": 0.57421875,
      "tpr_at_1pct_fpr": 0.8125
    }
  ],
  "library": "llm-compressor",
  "library_version": "0.13.0",
  "mean_changed_weight_fraction_vs_artifact0": null,
  "method": "GPTQ",
  "metrics": {
    "artifact_layer_combination": {
      "auroc": 1.0,
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    "artifact_reconstruction": {
      "auroc": 0.9999313354492188,
      "tpr_at_0_1pct_fpr": 0.984375,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.864654541015625,
      "tpr_at_0_1pct_fpr": 0.0625,
      "tpr_at_1pct_fpr": 0.369140625
    },
    "output_kl": {
      "auroc": 0.6961669921875,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.05859375
    },
    "output_logit_mse": {
      "auroc": 0.8646278381347656,
      "tpr_at_0_1pct_fpr": 0.0625,
      "tpr_at_1pct_fpr": 0.353515625
    },
    "output_logprob": {
      "auroc": 0.4972496032714844,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    },
    "output_logprob_gap": {
      "auroc": 0.4972496032714844,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.015625
    }
  },
  "model": "facebook/opt-125m",
  "model_dtype": "float16",
  "model_revision": "27dcfa74d334bc871f3234de431e71c6eeba5dd6",
  "output_combination": {
    "coefficients": {
      "output_kl": -0.010776678907897682,
      "output_logit_mse": 2.056086651321649,
      "output_logprob": -0.032817949171154805,
      "output_logprob_gap": -0.032817949171154805
    },
    "features": [
      "output_logit_mse",
      "output_kl",
      "output_logprob",
      "output_logprob_gap"
    ],
    "regularization": 1.0,
    "shadow_split_auroc": 0.8771209716796875
  },
  "parameters": 125239296,
  "per_artifact_auroc": {
    "artifact_layer_combination": {
      "artifacts": 16,
      "artifacts_above_chance": 16,
      "artifacts_at_least_0_9": 16,
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "upper_quartile": 1.0,
      "values": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ]
    },
    "artifact_reconstruction": {
      "artifacts": 16,
      "artifacts_above_chance": 16,
      "artifacts_at_least_0_9": 16,
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 0.998046875,
      "upper_quartile": 1.0,
      "values": [
        1.0,
        0.9990234375,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.998046875,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ]
    },
    "output_combination": {
      "artifacts": 16,
      "artifacts_above_chance": 16,
      "artifacts_at_least_0_9": 5,
      "lower_quartile": 0.829833984375,
      "maximum": 0.9384765625,
      "median": 0.865234375,
      "minimum": 0.771484375,
      "upper_quartile": 0.919189453125,
      "values": [
        0.8662109375,
        0.8662109375,
        0.8642578125,
        0.919921875,
        0.771484375,
        0.826171875,
        0.9208984375,
        0.8134765625,
        0.8310546875,
        0.9306640625,
        0.84375,
        0.9189453125,
        0.8076171875,
        0.9384765625,
        0.8837890625,
        0.8486328125
      ]
    },
    "output_kl": {
      "artifacts": 16,
      "artifacts_above_chance": 16,
      "artifacts_at_least_0_9": 0,
      "lower_quartile": 0.654296875,
      "maximum": 0.80078125,
      "median": 0.70068359375,
      "minimum": 0.5947265625,
      "upper_quartile": 0.754150390625,
      "values": [
        0.6298828125,
        0.73046875,
        0.7333984375,
        0.6552734375,
        0.6025390625,
        0.693359375,
        0.80078125,
        0.6513671875,
        0.5947265625,
        0.775390625,
        0.7724609375,
        0.748046875,
        0.7041015625,
        0.6904296875,
        0.697265625,
        0.7958984375
      ]
    },
    "output_logit_mse": {
      "artifacts": 16,
      "artifacts_above_chance": 16,
      "artifacts_at_least_0_9": 5,
      "lower_quartile": 0.83203125,
      "maximum": 0.9423828125,
      "median": 0.8662109375,
      "minimum": 0.76953125,
      "upper_quartile": 0.91845703125,
      "values": [
        0.865234375,
        0.8671875,
        0.869140625,
        0.91796875,
        0.76953125,
        0.826171875,
        0.9208984375,
        0.8076171875,
        0.833984375,
        0.9296875,
        0.8447265625,
        0.919921875,
        0.8076171875,
        0.9423828125,
        0.87890625,
        0.8505859375
      ]
    },
    "output_logprob": {
      "artifacts": 16,
      "artifacts_above_chance": 9,
      "artifacts_at_least_0_9": 0,
      "lower_quartile": 0.42529296875,
      "maximum": 0.6123046875,
      "median": 0.5244140625,
      "minimum": 0.341796875,
      "upper_quartile": 0.559814453125,
      "values": [
        0.341796875,
        0.6123046875,
        0.5263671875,
        0.55859375,
        0.3681640625,
        0.5224609375,
        0.5634765625,
        0.591796875,
        0.53125,
        0.427734375,
        0.447265625,
        0.400390625,
        0.544921875,
        0.41796875,
        0.4912109375,
        0.595703125
      ]
    },
    "output_logprob_gap": {
      "artifacts": 16,
      "artifacts_above_chance": 9,
      "artifacts_at_least_0_9": 0,
      "lower_quartile": 0.42529296875,
      "maximum": 0.6123046875,
      "median": 0.5244140625,
      "minimum": 0.341796875,
      "upper_quartile": 0.559814453125,
      "values": [
        0.341796875,
        0.6123046875,
        0.5263671875,
        0.55859375,
        0.3681640625,
        0.5224609375,
        0.5634765625,
        0.591796875,
        0.53125,
        0.427734375,
        0.447265625,
        0.400390625,
        0.544921875,
        0.41796875,
        0.4912109375,
        0.595703125
      ]
    }
  },
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
      "minimum": 0.953125,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 64,
      "upper_quartile": 1.0
    },
    "output_combination": {
      "lower_quartile": 0.8125,
      "maximum": 1.0,
      "median": 0.90625,
      "minimum": 0.640625,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 33,
      "upper_quartile": 0.94140625
    },
    "output_kl": {
      "lower_quartile": 0.6171875,
      "maximum": 1.0,
      "median": 0.75,
      "minimum": 0.09375,
      "targets_above_chance": 56,
      "targets_at_least_0_9": 9,
      "upper_quartile": 0.8125
    },
    "output_logit_mse": {
      "lower_quartile": 0.8125,
      "maximum": 1.0,
      "median": 0.8984375,
      "minimum": 0.625,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 32,
      "upper_quartile": 0.94140625
    },
    "output_logprob": {
      "lower_quartile": 0.41796875,
      "maximum": 0.734375,
      "median": 0.5078125,
      "minimum": 0.09375,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.609375
    },
    "output_logprob_gap": {
      "lower_quartile": 0.41796875,
      "maximum": 0.734375,
      "median": 0.5078125,
      "minimum": 0.09375,
      "targets_above_chance": 32,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.609375
    }
  },
  "population_sha256": "77f26fe7d76302d3d9d3150975489be515bc901ee3c3dbbe6e79b115f5bedfcc",
  "quantizer_seed": "fixed",
  "record_metadata": {
    "document_count": 4000,
    "earliest_published": "2024-01-01T00:54:02Z",
    "identifier_sha256": "6cf2151daecdb3ec893ce81d946bcdfa1c21bbd06d03b7b05064f1782132e412",
    "latest_published": "2024-02-10T00:49:46Z",
    "path": "data\\arxiv_cs_lg_2024.jsonl",
    "pool_sha256": "1a81196b54ad7d254d65bbc28fb10b9fa0be4e91c64b6ada0d5c73128d71e5b5",
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
    "artifact_logprob_change_std": 0.0026236424852210225,
    "base_mean_logprob": -3.795824706554413,
    "base_perplexity": 44.514933028513944,
    "mean_logprob_change": -0.04811721434816718,
    "perplexity_ratio_quantized_over_base": 1.0492936403866167,
    "protocol": "teacher-forced mean token log probability on public held-out references",
    "quantized_mean_logprob": -3.84394192090258,
    "quantized_perplexity": 46.70923612905584,
    "reference_decisions": 512
  },
  "selected_artifact_feature": "artifact_layer_combination",
  "selected_artifact_per_artifact_operating_point": {
    "fpr": {
      "lower_quartile": 0.0,
      "maximum": 0.03125,
      "median": 0.0,
      "minimum": 0.0,
      "upper_quartile": 0.03125,
      "values": [
        0.0,
        0.03125,
        0.0,
        0.0,
        0.0,
        0.0,
        0.03125,
        0.0,
        0.03125,
        0.0,
        0.0,
        0.0,
        0.03125,
        0.0,
        0.03125,
        0.0
      ]
    },
    "threshold": -3.052209187173082,
    "tpr": {
      "lower_quartile": 1.0,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 1.0,
      "upper_quartile": 1.0,
      "values": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ]
    }
  },
  "selected_output_baseline": "output_combination",
  "sequence_length": 512,
  "shadow_artifacts": 16,
  "shadow_calibrated_operating_points": {
    "artifact_layer_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 5,
        "test_fpr": 0.009765625,
        "test_tpr": 1.0,
        "test_true_positives": 512,
        "threshold": -3.052209187173082
      }
    },
    "artifact_reconstruction": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 4,
        "test_fpr": 0.0078125,
        "test_tpr": 1.0,
        "test_true_positives": 512,
        "threshold": -0.9212905398163798
      }
    },
    "output_combination": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.005859375,
        "test_tpr": 0.189453125,
        "test_true_positives": 97,
        "threshold": 1.335231084119784
      }
    },
    "output_kl": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 8,
        "test_fpr": 0.015625,
        "test_tpr": 0.11328125,
        "test_true_positives": 58,
        "threshold": 1.6351732188388208
      }
    },
    "output_logit_mse": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.005859375,
        "test_tpr": 0.193359375,
        "test_true_positives": 99,
        "threshold": 1.3461715541416188
      }
    },
    "output_logprob": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 37,
        "test_fpr": 0.072265625,
        "test_tpr": 0.0625,
        "test_true_positives": 32,
        "threshold": 1.7345066071477622
      }
    },
    "output_logprob_gap": {
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 5,
        "shadow_false_positives": 5,
        "shadow_fpr": 0.009765625,
        "target_fpr": 0.01,
        "test_false_positives": 37,
        "test_fpr": 0.072265625,
        "test_tpr": 0.0625,
        "test_true_positives": 32,
        "threshold": 1.7345066071477622
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
      "auroc": 0.9999732971191406,
      "tpr_at_0_1pct_fpr": 0.986328125,
      "tpr_at_1pct_fpr": 1.0
    },
    "output_combination": {
      "auroc": 0.8899002075195312,
      "tpr_at_0_1pct_fpr": 0.208984375,
      "tpr_at_1pct_fpr": 0.328125
    },
    "output_kl": {
      "auroc": 0.75006103515625,
      "tpr_at_0_1pct_fpr": 0.05859375,
      "tpr_at_1pct_fpr": 0.125
    },
    "output_logit_mse": {
      "auroc": 0.8895301818847656,
      "tpr_at_0_1pct_fpr": 0.205078125,
      "tpr_at_1pct_fpr": 0.326171875
    },
    "output_logprob": {
      "auroc": 0.6443367004394531,
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.05859375
    },
    "output_logprob_gap": {
      "auroc": 0.6443367004394531,
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.05859375
    }
  },
  "targets": 64,
  "test_artifacts": 16,
  "test_decisions": 1024,
  "test_members": 512,
  "test_nonmembers": 512,
  "threat_model": "public base, released llm-compressor W4 artifact, one held-out artifact"
}
```
