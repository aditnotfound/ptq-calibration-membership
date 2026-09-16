# CalibTrace named-library replication summary

Every row is a held-out single-artifact membership evaluation on `facebook/opt-125m` at
W4/N=128 with the same population design: 32 shadow artifacts, 16 held-out artifacts, 32
tracked candidate records, and fixed row and column membership margins. The artifact
feature and the output baseline are both selected on shadow artifacts only.

| Run | Method | Weights changed by one swap | Artifact AUROC | Output AUROC | Artifact - output | 95% interval |
|---|---|---:|---:|---:|---:|---:|
| AutoRound iters=0 | AutoRound | 12.3% | 0.6621 | 0.5315 | +0.1306 | [+0.0332, +0.2356] |
| AutoRound iters=10 | AutoRound | 65.8% | 0.6030 | 0.6936 | -0.0905 | [-0.1947, +0.0089] |
| AutoRound iters=50 | AutoRound | 73.7% | 0.6696 | 0.9999 | -0.3303 | [-0.4031, -0.2549] |
| AutoRound iters=200 | AutoRound | 73.7% | 0.8983 | 1.0000 | -0.1017 | [-0.1470, -0.0633] |
| AutoRound iters=200 (no reference) | AutoRound | 73.7% | 0.7525 | 1.0000 | -0.2475 | [-0.3326, -0.1547] |
| GPTQ one-shot | AutoRound | 20.8% | 1.0000 | 0.8251 | +0.1749 | [+0.1139, +0.2469] |

## Selected features

| Run | Artifact feature | Fixed aggregate AUROC | Output baseline | Held-out decisions |
|---|---|---:|---|---:|
| AutoRound iters=0 | `artifact_layer_combination` | 0.5358 | `output_logit_mse` | 512 |
| AutoRound iters=10 | `artifact_layer_combination` | 0.6000 | `output_kl` | 512 |
| AutoRound iters=50 | `artifact_layer_combination` | 0.6005 | `output_kl` | 512 |
| AutoRound iters=200 | `artifact_layer_combination` | 0.5461 | `output_logit_mse` | 512 |
| AutoRound iters=200 (no reference) | `artifact_layer_combination` | 0.4343 | `output_logit_mse` | 512 |
| GPTQ one-shot | `artifact_reconstruction` | 1.0000 | `output_combination` | 512 |

A positive `artifact - output` value means white-box artifact access recovers calibration
membership better than ordinary output observation of the same released model. A negative
value means the artifact adds nothing beyond what outputs already reveal.
