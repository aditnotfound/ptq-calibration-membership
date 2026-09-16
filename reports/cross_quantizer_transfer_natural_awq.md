# Cross-quantizer transfer

Every attack component is fit on shadow artifacts from the source PTQ family and applied without retuning to held-out artifacts from the target family. The two arms use the exact same records and membership matrix.

| Source | Target | Artifact AUROC | Output AUROC | Decisions |
|---|---|---:|---:|---:|
| GPTQ | AWQ | 0.4997 | 0.4979 | 2048 |
| AWQ | GPTQ | 0.4070 | 0.4895 | 2048 |

Full metrics and metadata:

```json
{
  "exact_population_match": true,
  "population_sha256": "f2dadc85c4fc75300397fe4f1562efdc60d90becb7f717d0554d1e81f8f4f765",
  "record_pool_sha256": "0f507b9770faeaeb93f062886772c8728eb57429226fb5d0532c26727f5f7e84",
  "transfers": [
    {
      "cluster_bootstrap": {
        "artifact_layer_combination": {
          "auroc": {
            "lower_95": 0.4651799623280741,
            "upper_95": 0.53400490904545
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.011127733683549359
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.002011720673692505,
            "upper_95": 0.025718267945726774
          }
        },
        "artifact_minus_selected_output_auroc": {
          "lower_95": -0.046725910798673824,
          "upper_95": 0.051808543075951535
        },
        "artifact_reconstruction": {
          "auroc": {
            "lower_95": 0.46415571707133674,
            "upper_95": 0.5312390380865742
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.008639117379824708
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.030891935478012614
          }
        },
        "output_combination": {
          "auroc": {
            "lower_95": 0.4655228671319845,
            "upper_95": 0.5359202852271218
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.012015355436408064
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.029445353105804525
          }
        },
        "output_kl": {
          "auroc": {
            "lower_95": 0.4651092116811925,
            "upper_95": 0.535032303320373
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.019362494008402332
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.03700277602080258
          }
        },
        "output_logit_mse": {
          "auroc": {
            "lower_95": 0.45965351690420125,
            "upper_95": 0.5327120910282953
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.016280811513328122
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.031533355183665075
          }
        },
        "output_logprob": {
          "auroc": {
            "lower_95": 0.46703286404081157,
            "upper_95": 0.5322796471483843
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.01454933470191067
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.026162247317576857
          }
        },
        "output_logprob_gap": {
          "auroc": {
            "lower_95": 0.4659438492305668,
            "upper_95": 0.545805496318276
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.008698633053698418
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.0229227415192459
          }
        },
        "selected_artifact": {
          "auroc": {
            "lower_95": 0.4651799623280741,
            "upper_95": 0.53400490904545
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.011127733683549359
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.002011720673692505,
            "upper_95": 0.025718267945726774
          }
        },
        "selected_output": {
          "auroc": {
            "lower_95": 0.4604341140734193,
            "upper_95": 0.5354766199625531
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.018968378374651207
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.03321379860595944
          }
        }
      },
      "fixed_degree_randomization_test": {
        "null_lower_95": 0.4994535207748413,
        "null_mean": 0.4999966044425964,
        "null_upper_95": 0.5005445718765259,
        "observed_auroc": 0.49970436096191406,
        "p_value_greater_equal": 0.8517148285171483,
        "replicates": 10000
      },
      "folds": 2,
      "metrics": {
        "artifact_layer_combination": {
          "auroc": 0.49970436096191406,
          "tpr_at_0_1pct_fpr": 0.0009765625,
          "tpr_at_1pct_fpr": 0.0087890625
        },
        "artifact_reconstruction": {
          "auroc": 0.4982032775878906,
          "tpr_at_0_1pct_fpr": 0.0,
          "tpr_at_1pct_fpr": 0.01171875
        },
        "output_combination": {
          "auroc": 0.49979114532470703,
          "tpr_at_0_1pct_fpr": 0.0,
          "tpr_at_1pct_fpr": 0.0078125
        },
        "output_kl": {
          "auroc": 0.5020866394042969,
          "tpr_at_0_1pct_fpr": 0.00390625,
          "tpr_at_1pct_fpr": 0.0107421875
        },
        "output_logit_mse": {
          "auroc": 0.4968414306640625,
          "tpr_at_0_1pct_fpr": 0.0048828125,
          "tpr_at_1pct_fpr": 0.01171875
        },
        "output_logprob": {
          "auroc": 0.5000505447387695,
          "tpr_at_0_1pct_fpr": 0.0,
          "tpr_at_1pct_fpr": 0.0087890625
        },
        "output_logprob_gap": {
          "auroc": 0.5044393539428711,
          "tpr_at_0_1pct_fpr": 0.0009765625,
          "tpr_at_1pct_fpr": 0.005859375
        },
        "selected_artifact": {
          "auroc": 0.49970436096191406,
          "tpr_at_0_1pct_fpr": 0.0009765625,
          "tpr_at_1pct_fpr": 0.0087890625
        },
        "selected_output": {
          "auroc": 0.49789905548095703,
          "tpr_at_0_1pct_fpr": 0.0048828125,
          "tpr_at_1pct_fpr": 0.01171875
        }
      },
      "protocol": "zero-shot quantizer-family transfer: every direction, normalization, feature combination, and feature choice is fit on source-family shadow artifacts; evaluated candidates are excluded by candidate-fold cross-fitting",
      "seed": 20261021,
      "selections": [
        {
          "fold": 0,
          "held_out_candidates": [
            13,
            16,
            51,
            62,
            57,
            1,
            43,
            58,
            35,
            22,
            3,
            49,
            6,
            17,
            32,
            28,
            39,
            23,
            29,
            53,
            63,
            40,
            9,
            10,
            44,
            7,
            41,
            12,
            38,
            59,
            18,
            14
          ],
          "layer_regularization": 1.0,
          "layer_validation_auroc": 1.0,
          "output_regularization": 0.01,
          "output_validation_auroc": 0.6786843190251501,
          "selected_artifact_feature": "artifact_layer_combination",
          "selected_output_feature": "output_logit_mse",
          "training_candidates": [
            0,
            2,
            4,
            5,
            8,
            11,
            15,
            19,
            20,
            21,
            24,
            25,
            26,
            27,
            30,
            31,
            33,
            34,
            36,
            37,
            42,
            45,
            46,
            47,
            48,
            50,
            52,
            54,
            55,
            56,
            60,
            61
          ]
        },
        {
          "fold": 1,
          "held_out_candidates": [
            27,
            0,
            56,
            24,
            55,
            5,
            2,
            26,
            19,
            52,
            21,
            15,
            61,
            54,
            20,
            47,
            11,
            48,
            33,
            46,
            45,
            42,
            30,
            8,
            37,
            60,
            50,
            34,
            4,
            25,
            36,
            31
          ],
          "layer_regularization": 1.0,
          "layer_validation_auroc": 1.0,
          "output_regularization": 1.0,
          "output_validation_auroc": 0.6398750897124621,
          "selected_artifact_feature": "artifact_layer_combination",
          "selected_output_feature": "output_combination",
          "training_candidates": [
            1,
            3,
            6,
            7,
            9,
            10,
            12,
            13,
            14,
            16,
            17,
            18,
            22,
            23,
            28,
            29,
            32,
            35,
            38,
            39,
            40,
            41,
            43,
            44,
            49,
            51,
            53,
            57,
            58,
            59,
            62,
            63
          ]
        }
      ],
      "source_method": "GPTQ",
      "target_method": "AWQ",
      "test_decisions": 2048
    },
    {
      "cluster_bootstrap": {
        "artifact_layer_combination": {
          "auroc": {
            "lower_95": 0.6677598474137421,
            "upper_95": 0.7712067876414377
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.016233026921085518,
            "upper_95": 0.1320483054152668
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.022725035790980674,
            "upper_95": 0.14161890920679576
          }
        },
        "artifact_minus_selected_output_auroc": {
          "lower_95": -0.1626853507477801,
          "upper_95": -0.017512333934910935
        },
        "artifact_reconstruction": {
          "auroc": {
            "lower_95": 0.3624680412172687,
            "upper_95": 0.4389825338061425
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
        "output_combination": {
          "auroc": {
            "lower_95": 0.49392109633167863,
            "upper_95": 0.6003966615893803
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0018723976314523048,
            "upper_95": 0.04392618283981003
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.012482396280789516,
            "upper_95": 0.07633783539677907
          }
        },
        "output_kl": {
          "auroc": {
            "lower_95": 0.46020898864149434,
            "upper_95": 0.5524596553713793
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.013838142292490115
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.0441832652664987
          }
        },
        "output_logit_mse": {
          "auroc": {
            "lower_95": 0.46957403430010697,
            "upper_95": 0.5794689565755857
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.04425024461839529
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0040078156312625245,
            "upper_95": 0.06742163133585218
          }
        },
        "output_logprob": {
          "auroc": {
            "lower_95": 0.46471358298618537,
            "upper_95": 0.5361610026142053
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.014326647564469915
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.029105088011126188
          }
        },
        "output_logprob_gap": {
          "auroc": {
            "lower_95": 0.46577136998376123,
            "upper_95": 0.5380507324421703
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.013619340721020017
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.03232016041213691
          }
        },
        "selected_artifact": {
          "auroc": {
            "lower_95": 0.3624680412172687,
            "upper_95": 0.4389825338061425
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
        "selected_output": {
          "auroc": {
            "lower_95": 0.4407554011483133,
            "upper_95": 0.5411313015209018
          },
          "tpr_at_0_1pct_fpr": {
            "lower_95": 0.0,
            "upper_95": 0.028658116596870176
          },
          "tpr_at_1pct_fpr": {
            "lower_95": 0.004724572902496334,
            "upper_95": 0.06446573930031474
          }
        }
      },
      "fixed_degree_randomization_test": {
        "null_lower_95": 0.49533557891845703,
        "null_mean": 0.49998979806900024,
        "null_upper_95": 0.5046360492706299,
        "observed_auroc": 0.4070100784301758,
        "p_value_greater_equal": 1.0,
        "replicates": 10000
      },
      "folds": 2,
      "metrics": {
        "artifact_layer_combination": {
          "auroc": 0.7127981185913086,
          "tpr_at_0_1pct_fpr": 0.046875,
          "tpr_at_1pct_fpr": 0.0556640625
        },
        "artifact_reconstruction": {
          "auroc": 0.4070100784301758,
          "tpr_at_0_1pct_fpr": 0.0,
          "tpr_at_1pct_fpr": 0.0
        },
        "output_combination": {
          "auroc": 0.545806884765625,
          "tpr_at_0_1pct_fpr": 0.005859375,
          "tpr_at_1pct_fpr": 0.033203125
        },
        "output_kl": {
          "auroc": 0.5051422119140625,
          "tpr_at_0_1pct_fpr": 0.0,
          "tpr_at_1pct_fpr": 0.0048828125
        },
        "output_logit_mse": {
          "auroc": 0.5210494995117188,
          "tpr_at_0_1pct_fpr": 0.0166015625,
          "tpr_at_1pct_fpr": 0.021484375
        },
        "output_logprob": {
          "auroc": 0.5004072189331055,
          "tpr_at_0_1pct_fpr": 0.00390625,
          "tpr_at_1pct_fpr": 0.0126953125
        },
        "output_logprob_gap": {
          "auroc": 0.5018482208251953,
          "tpr_at_0_1pct_fpr": 0.0009765625,
          "tpr_at_1pct_fpr": 0.0078125
        },
        "selected_artifact": {
          "auroc": 0.4070100784301758,
          "tpr_at_0_1pct_fpr": 0.0,
          "tpr_at_1pct_fpr": 0.0
        },
        "selected_output": {
          "auroc": 0.48947906494140625,
          "tpr_at_0_1pct_fpr": 0.0068359375,
          "tpr_at_1pct_fpr": 0.0263671875
        }
      },
      "protocol": "zero-shot quantizer-family transfer: every direction, normalization, feature combination, and feature choice is fit on source-family shadow artifacts; evaluated candidates are excluded by candidate-fold cross-fitting",
      "seed": 20261021,
      "selections": [
        {
          "fold": 0,
          "held_out_candidates": [
            13,
            16,
            51,
            62,
            57,
            1,
            43,
            58,
            35,
            22,
            3,
            49,
            6,
            17,
            32,
            28,
            39,
            23,
            29,
            53,
            63,
            40,
            9,
            10,
            44,
            7,
            41,
            12,
            38,
            59,
            18,
            14
          ],
          "layer_regularization": 1.0,
          "layer_validation_auroc": 0.4981675752439415,
          "output_regularization": 1.0,
          "output_validation_auroc": 0.46811580924458285,
          "selected_artifact_feature": "artifact_reconstruction",
          "selected_output_feature": "output_logit_mse",
          "training_candidates": [
            0,
            2,
            4,
            5,
            8,
            11,
            15,
            19,
            20,
            21,
            24,
            25,
            26,
            27,
            30,
            31,
            33,
            34,
            36,
            37,
            42,
            45,
            46,
            47,
            48,
            50,
            52,
            54,
            55,
            56,
            60,
            61
          ]
        },
        {
          "fold": 1,
          "held_out_candidates": [
            27,
            0,
            56,
            24,
            55,
            5,
            2,
            26,
            19,
            52,
            21,
            15,
            61,
            54,
            20,
            47,
            11,
            48,
            33,
            46,
            45,
            42,
            30,
            8,
            37,
            60,
            50,
            34,
            4,
            25,
            36,
            31
          ],
          "layer_regularization": 1.0,
          "layer_validation_auroc": 0.46206880754958995,
          "output_regularization": 1.0,
          "output_validation_auroc": 0.49134942813077404,
          "selected_artifact_feature": "artifact_reconstruction",
          "selected_output_feature": "output_kl",
          "training_candidates": [
            1,
            3,
            6,
            7,
            9,
            10,
            12,
            13,
            14,
            16,
            17,
            18,
            22,
            23,
            28,
            29,
            32,
            35,
            38,
            39,
            40,
            41,
            43,
            44,
            49,
            51,
            53,
            57,
            58,
            59,
            62,
            63
          ]
        }
      ],
      "source_method": "AWQ",
      "target_method": "GPTQ",
      "test_decisions": 2048
    }
  ]
}
```
