# CalibTrace single-artifact attack report

Evaluation uses 72 shadow artifacts, 24 completely held-out artifacts, and 64 candidate records at W4/N=128.

| Feature | AUROC | ROC TPR @ FPR<=1% | ROC TPR @ zero observed FP |
|---|---:|---:|---:|
| artifact_reconstruction | 0.9917 | 0.8802 | 0.5352 |
| output_logit_mse | 0.9130 | 0.4010 | 0.1354 |
| output_kl | 0.6038 | 0.0169 | 0.0000 |
| output_true_logprob | 0.5413 | 0.0026 | 0.0013 |

## Layerwise localization

Each layer is scored alone with the same shadow-only candidate normalization. These are localization diagnostics, not separately bootstrapped claims.

| Layer | AUROC | ROC TPR @ FPR<=1% | Frozen-threshold test TPR |
|---|---:|---:|---:|
| layer4.0.conv1 | 1.0000 | 1.0000 | 1.0000 |
| layer4.0.conv2 | 1.0000 | 1.0000 | 1.0000 |
| layer4.1.conv1 | 1.0000 | 1.0000 | 1.0000 |
| layer4.1.conv2 | 1.0000 | 1.0000 | 1.0000 |
| fc | 0.9998 | 0.9974 | 0.9987 |
| layer4.0.shortcut.0 | 0.9962 | 0.9010 | 0.9193 |
| layer3.1.conv1 | 0.9800 | 0.7292 | 0.7513 |
| layer3.0.conv2 | 0.9798 | 0.7318 | 0.7695 |
| layer3.1.conv2 | 0.9703 | 0.6107 | 0.6888 |
| layer3.0.conv1 | 0.9545 | 0.5352 | 0.5599 |
| layer2.1.conv2 | 0.7310 | 0.0703 | 0.0547 |
| layer2.1.conv1 | 0.6936 | 0.0638 | 0.0404 |
| layer3.0.shortcut.0 | 0.6718 | 0.0612 | 0.0807 |
| layer2.0.conv2 | 0.6667 | 0.0521 | 0.0768 |
| layer2.0.conv1 | 0.6218 | 0.0182 | 0.0638 |
| layer1.0.conv2 | 0.5533 | 0.0130 | 0.0312 |
| layer1.1.conv1 | 0.5524 | 0.0312 | 0.0326 |
| layer1.1.conv2 | 0.5231 | 0.0182 | 0.0169 |
| layer1.0.conv1 | 0.5100 | 0.0039 | 0.0065 |
| layer2.0.shortcut.0 | 0.5039 | 0.0104 | 0.0234 |
| conv1 | 0.4950 | 0.0065 | 0.0182 |

The held-out set has 768 nonmembers, so its empirical FPR resolution is 0.130%. The final column is the zero-observed-false-positive point; it must not be read as a resolved 0.1% estimate.

## Shadow-calibrated operating points

Thresholds below are selected using shadow nonmembers only and then frozen before evaluation on held-out artifacts.

| Feature | Target FPR | Shadow FPR | Test FPR | Test TPR |
|---|---:|---:|---:|---:|
| artifact_reconstruction | 1% | 0.0100 | 0.0091 | 0.8776 |
| artifact_reconstruction | 0.1% | 0.0009 | 0.0013 | 0.7018 |
| output_logit_mse | 1% | 0.0100 | 0.0143 | 0.4622 |
| output_logit_mse | 0.1% | 0.0009 | 0.0013 | 0.2565 |
| output_kl | 1% | 0.0100 | 0.0104 | 0.0195 |
| output_kl | 0.1% | 0.0009 | 0.0026 | 0.0013 |
| output_true_logprob | 1% | 0.0100 | 0.0208 | 0.0065 |
| output_true_logprob | 0.1% | 0.0009 | 0.0039 | 0.0013 |

Artifact minus output-logit-MSE AUROC: 0.0787.

Full crossed target/artifact bootstrap intervals and metadata:

```json
{
  "artifact_minus_output_logit_mse_auroc": 0.0787116156684029,
  "cluster_bootstrap": {
    "artifact_minus_output_logit_mse_auroc": {
      "lower_95": 0.0528081243376725,
      "upper_95": 0.11004550846588251
    },
    "artifact_reconstruction": {
      "auroc": {
        "lower_95": 0.9829054312035537,
        "upper_95": 0.9977375037306246
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.44544094028325304,
        "upper_95": 0.8923303982389433
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.6684046204585007,
        "upper_95": 0.9620430065256702
      }
    },
    "output_kl": {
      "auroc": {
        "lower_95": 0.5523925514940479,
        "upper_95": 0.6542775017993309
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.025398756264455553
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.06802810129287318
      }
    },
    "output_logit_mse": {
      "auroc": {
        "lower_95": 0.881412926881969,
        "upper_95": 0.938175285828878
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.09584256984135463,
        "upper_95": 0.42444876577225776
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.2588794728167007,
        "upper_95": 0.5670261570481163
      }
    },
    "output_true_logprob": {
      "auroc": {
        "lower_95": 0.484354263860099,
        "upper_95": 0.5923993526059687
      },
      "tpr_at_0_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0077521886940040315
      },
      "tpr_at_1pct_fpr": {
        "lower_95": 0.0,
        "upper_95": 0.0166902149157315
      }
    }
  },
  "empirical_test_fpr_resolution": 0.0013020833333333333,
  "fit_free_fixed_score": {
    "metrics": {
      "auroc": 0.7208404541015624,
      "tpr_at_0_1pct_fpr": 0.03125,
      "tpr_at_1pct_fpr": 0.036458333333333336
    },
    "per_artifact_auroc": {
      "artifacts": 24,
      "artifacts_above_chance": 24,
      "artifacts_at_least_0_9": 0,
      "lower_quartile": 0.669677734375,
      "maximum": 0.8515625,
      "median": 0.71337890625,
      "minimum": 0.5654296875,
      "upper_quartile": 0.774169921875,
      "values": [
        0.75,
        0.70703125,
        0.650390625,
        0.75390625,
        0.669921875,
        0.677734375,
        0.740234375,
        0.650390625,
        0.677734375,
        0.6689453125,
        0.68359375,
        0.7685546875,
        0.5654296875,
        0.791015625,
        0.794921875,
        0.796875,
        0.818359375,
        0.7099609375,
        0.8076171875,
        0.716796875,
        0.8515625,
        0.65234375,
        0.7626953125,
        0.6533203125
      ]
    },
    "protocol": "predefined negative residual-energy score with zero learned direction, normalization, layer weighting, regularization, or feature selection"
  },
  "layerwise_artifact_reconstruction": [
    {
      "auroc": 1.0,
      "layer": "layer4.0.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 11,
        "test_fpr": 0.014322916666666666,
        "test_tpr": 1.0,
        "test_true_positives": 768,
        "threshold": -2.1551687412626843
      },
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "layer4.0.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 5,
        "test_fpr": 0.006510416666666667,
        "test_tpr": 1.0,
        "test_true_positives": 768,
        "threshold": -2.2696330908540756
      },
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "layer4.1.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.009114583333333334,
        "test_tpr": 1.0,
        "test_true_positives": 768,
        "threshold": -1.4881739274002181
      },
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 1.0,
      "layer": "layer4.1.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 9,
        "test_fpr": 0.01171875,
        "test_tpr": 1.0,
        "test_true_positives": 768,
        "threshold": -1.0762270102052105
      },
      "tpr_at_0_1pct_fpr": 1.0,
      "tpr_at_1pct_fpr": 1.0
    },
    {
      "auroc": 0.9998016357421875,
      "layer": "fc",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 17,
        "test_fpr": 0.022135416666666668,
        "test_tpr": 0.9986979166666666,
        "test_true_positives": 767,
        "threshold": 0.46393575503066203
      },
      "tpr_at_0_1pct_fpr": 0.9231770833333334,
      "tpr_at_1pct_fpr": 0.9973958333333334
    },
    {
      "auroc": 0.9962124294704862,
      "layer": "layer4.0.shortcut.0",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 9,
        "test_fpr": 0.01171875,
        "test_tpr": 0.9192708333333334,
        "test_true_positives": 706,
        "threshold": 0.6264225855850603
      },
      "tpr_at_0_1pct_fpr": 0.7669270833333334,
      "tpr_at_1pct_fpr": 0.9010416666666666
    },
    {
      "auroc": 0.9800008138020833,
      "layer": "layer3.1.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 8,
        "test_fpr": 0.010416666666666666,
        "test_tpr": 0.7513020833333334,
        "test_true_positives": 577,
        "threshold": 0.7992867091193951
      },
      "tpr_at_0_1pct_fpr": 0.3307291666666667,
      "tpr_at_1pct_fpr": 0.7291666666666666
    },
    {
      "auroc": 0.979824490017361,
      "layer": "layer3.0.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 10,
        "test_fpr": 0.013020833333333334,
        "test_tpr": 0.76953125,
        "test_true_positives": 591,
        "threshold": 0.8343439333141779
      },
      "tpr_at_0_1pct_fpr": 0.5091145833333334,
      "tpr_at_1pct_fpr": 0.7317708333333334
    },
    {
      "auroc": 0.9702741834852431,
      "layer": "layer3.1.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 10,
        "test_fpr": 0.013020833333333334,
        "test_tpr": 0.6888020833333334,
        "test_true_positives": 529,
        "threshold": 0.928707086496366
      },
      "tpr_at_0_1pct_fpr": 0.21744791666666666,
      "tpr_at_1pct_fpr": 0.6106770833333334
    },
    {
      "auroc": 0.9544847276475695,
      "layer": "layer3.0.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 8,
        "test_fpr": 0.010416666666666666,
        "test_tpr": 0.5598958333333334,
        "test_true_positives": 430,
        "threshold": 1.114124519889565
      },
      "tpr_at_0_1pct_fpr": 0.3385416666666667,
      "tpr_at_1pct_fpr": 0.53515625
    },
    {
      "auroc": 0.7310112847222222,
      "layer": "layer2.1.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.009114583333333334,
        "test_tpr": 0.0546875,
        "test_true_positives": 42,
        "threshold": 1.8679021787007561
      },
      "tpr_at_0_1pct_fpr": 0.015625,
      "tpr_at_1pct_fpr": 0.0703125
    },
    {
      "auroc": 0.6935899522569444,
      "layer": "layer2.1.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 3,
        "test_fpr": 0.00390625,
        "test_tpr": 0.040364583333333336,
        "test_true_positives": 31,
        "threshold": 1.8594317985458404
      },
      "tpr_at_0_1pct_fpr": 0.006510416666666667,
      "tpr_at_1pct_fpr": 0.06380208333333333
    },
    {
      "auroc": 0.6717817518446181,
      "layer": "layer3.0.shortcut.0",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 12,
        "test_fpr": 0.015625,
        "test_tpr": 0.08072916666666667,
        "test_true_positives": 62,
        "threshold": 1.8058837637344007
      },
      "tpr_at_0_1pct_fpr": 0.005208333333333333,
      "tpr_at_1pct_fpr": 0.061197916666666664
    },
    {
      "auroc": 0.6667226155598959,
      "layer": "layer2.0.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 19,
        "test_fpr": 0.024739583333333332,
        "test_tpr": 0.07682291666666667,
        "test_true_positives": 59,
        "threshold": 1.78065567808009
      },
      "tpr_at_0_1pct_fpr": 0.0026041666666666665,
      "tpr_at_1pct_fpr": 0.052083333333333336
    },
    {
      "auroc": 0.6218312581380208,
      "layer": "layer2.0.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 23,
        "test_fpr": 0.029947916666666668,
        "test_tpr": 0.06380208333333333,
        "test_true_positives": 49,
        "threshold": 1.9140242033356862
      },
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.018229166666666668
    },
    {
      "auroc": 0.5533362494574653,
      "layer": "layer1.0.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 14,
        "test_fpr": 0.018229166666666668,
        "test_tpr": 0.03125,
        "test_true_positives": 24,
        "threshold": 2.0942820716383315
      },
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.013020833333333334
    },
    {
      "auroc": 0.5524275037977431,
      "layer": "layer1.1.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 10,
        "test_fpr": 0.013020833333333334,
        "test_tpr": 0.032552083333333336,
        "test_true_positives": 25,
        "threshold": 2.0011384751702956
      },
      "tpr_at_0_1pct_fpr": 0.0013020833333333333,
      "tpr_at_1pct_fpr": 0.03125
    },
    {
      "auroc": 0.5231289333767362,
      "layer": "layer1.1.conv2",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.009114583333333334,
        "test_tpr": 0.016927083333333332,
        "test_true_positives": 13,
        "threshold": 2.137273697617136
      },
      "tpr_at_0_1pct_fpr": 0.0026041666666666665,
      "tpr_at_1pct_fpr": 0.018229166666666668
    },
    {
      "auroc": 0.5100301106770833,
      "layer": "layer1.0.conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 8,
        "test_fpr": 0.010416666666666666,
        "test_tpr": 0.006510416666666667,
        "test_true_positives": 5,
        "threshold": 2.0817342353564894
      },
      "tpr_at_0_1pct_fpr": 0.0013020833333333333,
      "tpr_at_1pct_fpr": 0.00390625
    },
    {
      "auroc": 0.503936767578125,
      "layer": "layer2.0.shortcut.0",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 20,
        "test_fpr": 0.026041666666666668,
        "test_tpr": 0.0234375,
        "test_true_positives": 18,
        "threshold": 2.039199518908421
      },
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.010416666666666666
    },
    {
      "auroc": 0.49504597981770837,
      "layer": "conv1",
      "shadow_calibrated_1pct": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 16,
        "test_fpr": 0.020833333333333332,
        "test_tpr": 0.018229166666666668,
        "test_true_positives": 14,
        "threshold": 1.9350711272045638
      },
      "tpr_at_0_1pct_fpr": 0.0026041666666666665,
      "tpr_at_1pct_fpr": 0.006510416666666667
    }
  ],
  "metrics": {
    "artifact_reconstruction": {
      "auroc": 0.9917449951171875,
      "tpr_at_0_1pct_fpr": 0.53515625,
      "tpr_at_1pct_fpr": 0.8802083333333334
    },
    "output_kl": {
      "auroc": 0.60382080078125,
      "tpr_at_0_1pct_fpr": 0.0,
      "tpr_at_1pct_fpr": 0.016927083333333332
    },
    "output_logit_mse": {
      "auroc": 0.9130333794487846,
      "tpr_at_0_1pct_fpr": 0.13541666666666666,
      "tpr_at_1pct_fpr": 0.4010416666666667
    },
    "output_true_logprob": {
      "auroc": 0.5413411458333334,
      "tpr_at_0_1pct_fpr": 0.0013020833333333333,
      "tpr_at_1pct_fpr": 0.0026041666666666665
    }
  },
  "per_artifact_auroc": {
    "artifact_reconstruction": {
      "artifacts": 24,
      "artifacts_above_chance": 24,
      "artifacts_at_least_0_9": 24,
      "lower_quartile": 0.9990234375,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 0.9892578125,
      "upper_quartile": 1.0,
      "values": [
        1.0,
        0.9990234375,
        1.0,
        1.0,
        1.0,
        0.9990234375,
        1.0,
        1.0,
        1.0,
        1.0,
        0.9951171875,
        1.0,
        1.0,
        1.0,
        0.9970703125,
        0.9892578125,
        1.0,
        1.0,
        1.0,
        0.9951171875,
        0.9990234375,
        1.0,
        1.0,
        0.9990234375
      ]
    },
    "output_kl": {
      "artifacts": 24,
      "artifacts_above_chance": 23,
      "artifacts_at_least_0_9": 0,
      "lower_quartile": 0.546875,
      "maximum": 0.732421875,
      "median": 0.607421875,
      "minimum": 0.4775390625,
      "upper_quartile": 0.654541015625,
      "values": [
        0.5810546875,
        0.6728515625,
        0.7197265625,
        0.5595703125,
        0.4775390625,
        0.732421875,
        0.5537109375,
        0.6455078125,
        0.5380859375,
        0.5283203125,
        0.6337890625,
        0.568359375,
        0.5439453125,
        0.6953125,
        0.6484375,
        0.5693359375,
        0.6875,
        0.533203125,
        0.6337890625,
        0.6337890625,
        0.701171875,
        0.5478515625,
        0.63671875,
        0.50390625
      ]
    },
    "output_logit_mse": {
      "artifacts": 24,
      "artifacts_above_chance": 24,
      "artifacts_at_least_0_9": 18,
      "lower_quartile": 0.898193359375,
      "maximum": 0.9638671875,
      "median": 0.91259765625,
      "minimum": 0.8427734375,
      "upper_quartile": 0.943359375,
      "values": [
        0.8701171875,
        0.9501953125,
        0.9423828125,
        0.9189453125,
        0.9130859375,
        0.90234375,
        0.8583984375,
        0.912109375,
        0.9013671875,
        0.9423828125,
        0.90625,
        0.86328125,
        0.8447265625,
        0.947265625,
        0.9638671875,
        0.900390625,
        0.9619140625,
        0.9560546875,
        0.8427734375,
        0.9228515625,
        0.9072265625,
        0.8916015625,
        0.9130859375,
        0.9462890625
      ]
    },
    "output_true_logprob": {
      "artifacts": 24,
      "artifacts_above_chance": 16,
      "artifacts_at_least_0_9": 0,
      "lower_quartile": 0.49267578125,
      "maximum": 0.689453125,
      "median": 0.548828125,
      "minimum": 0.373046875,
      "upper_quartile": 0.59521484375,
      "values": [
        0.548828125,
        0.6240234375,
        0.576171875,
        0.4404296875,
        0.4697265625,
        0.56640625,
        0.611328125,
        0.59375,
        0.52734375,
        0.548828125,
        0.4970703125,
        0.49609375,
        0.5537109375,
        0.5302734375,
        0.5322265625,
        0.5576171875,
        0.599609375,
        0.4521484375,
        0.6669921875,
        0.67578125,
        0.689453125,
        0.4541015625,
        0.482421875,
        0.373046875
      ]
    }
  },
  "per_target_auroc": {
    "artifact_reconstruction": {
      "lower_quartile": 0.9861111111111112,
      "maximum": 1.0,
      "median": 1.0,
      "minimum": 0.8680555555555556,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 61,
      "upper_quartile": 1.0
    },
    "output_kl": {
      "lower_quartile": 0.5399305555555556,
      "maximum": 0.9097222222222222,
      "median": 0.6458333333333333,
      "minimum": 0.2361111111111111,
      "targets_above_chance": 50,
      "targets_at_least_0_9": 1,
      "upper_quartile": 0.7152777777777778
    },
    "output_logit_mse": {
      "lower_quartile": 0.8802083333333333,
      "maximum": 1.0,
      "median": 0.9375,
      "minimum": 0.6388888888888888,
      "targets_above_chance": 64,
      "targets_at_least_0_9": 44,
      "upper_quartile": 0.9722222222222222
    },
    "output_true_logprob": {
      "lower_quartile": 0.4227430555555556,
      "maximum": 0.8611111111111112,
      "median": 0.5694444444444444,
      "minimum": 0.20833333333333331,
      "targets_above_chance": 40,
      "targets_at_least_0_9": 0,
      "upper_quartile": 0.6805555555555556
    }
  },
  "shadow_artifacts": 72,
  "shadow_calibrated_operating_points": {
    "artifact_reconstruction": {
      "0_1pct_target_fpr": {
        "allowed_shadow_false_positives": 2,
        "shadow_false_positives": 2,
        "shadow_fpr": 0.0008680555555555555,
        "target_fpr": 0.001,
        "test_false_positives": 1,
        "test_fpr": 0.0013020833333333333,
        "test_tpr": 0.7018229166666666,
        "test_true_positives": 539,
        "threshold": 1.1863228310733593
      },
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 7,
        "test_fpr": 0.009114583333333334,
        "test_tpr": 0.8776041666666666,
        "test_true_positives": 674,
        "threshold": 0.6320891888706701
      }
    },
    "output_kl": {
      "0_1pct_target_fpr": {
        "allowed_shadow_false_positives": 2,
        "shadow_false_positives": 2,
        "shadow_fpr": 0.0008680555555555555,
        "target_fpr": 0.001,
        "test_false_positives": 2,
        "test_fpr": 0.0026041666666666665,
        "test_tpr": 0.0013020833333333333,
        "test_true_positives": 1,
        "threshold": 2.8994702725810604
      },
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 8,
        "test_fpr": 0.010416666666666666,
        "test_tpr": 0.01953125,
        "test_true_positives": 15,
        "threshold": 1.156656962679454
      }
    },
    "output_logit_mse": {
      "0_1pct_target_fpr": {
        "allowed_shadow_false_positives": 2,
        "shadow_false_positives": 2,
        "shadow_fpr": 0.0008680555555555555,
        "target_fpr": 0.001,
        "test_false_positives": 1,
        "test_fpr": 0.0013020833333333333,
        "test_tpr": 0.2565104166666667,
        "test_true_positives": 197,
        "threshold": 1.5128414701799355
      },
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 11,
        "test_fpr": 0.014322916666666666,
        "test_tpr": 0.4622395833333333,
        "test_true_positives": 355,
        "threshold": 1.1473534408864206
      }
    },
    "output_true_logprob": {
      "0_1pct_target_fpr": {
        "allowed_shadow_false_positives": 2,
        "shadow_false_positives": 2,
        "shadow_fpr": 0.0008680555555555555,
        "target_fpr": 0.001,
        "test_false_positives": 3,
        "test_fpr": 0.00390625,
        "test_tpr": 0.0013020833333333333,
        "test_true_positives": 1,
        "threshold": 4.012679962871148
      },
      "1pct_target_fpr": {
        "allowed_shadow_false_positives": 23,
        "shadow_false_positives": 23,
        "shadow_fpr": 0.009982638888888888,
        "target_fpr": 0.01,
        "test_false_positives": 16,
        "test_fpr": 0.020833333333333332,
        "test_tpr": 0.006510416666666667,
        "test_true_positives": 5,
        "threshold": 2.548056789252259
      }
    }
  },
  "targets": 64,
  "test_artifacts": 24,
  "test_decisions": 1536,
  "test_members": 768,
  "test_nonmembers": 768,
  "threat_model": "public base, known quantizer, one held-out released artifact"
}
```
