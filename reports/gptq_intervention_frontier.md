# GPTQ intervention frontier

| Intervention | Artifact AUROC | Artifact CF AUROC [95% CI] | Output CF AUROC [95% CI] | PPL ratio |
|---|---:|---:|---:|---:|
| Sequential, damping 0.01 | 1.0000 | 0.9360 [0.8776, 0.9849] | 0.5797 [0.5108, 0.6530] | 1.0480 |
| Sequential, damping 0.1 | 1.0000 | 0.8730 [0.8083, 0.9353] | 0.5528 [0.4808, 0.6240] | 1.0480 |
| Sequential, damping 1.0 | 0.9995 | 0.6899 [0.6295, 0.7643] | 0.5152 [0.4414, 0.5853] | 1.0459 |
| Independent, damping 0.01 | 1.0000 | 0.9360 [0.8776, 0.9849] | 0.5797 [0.5108, 0.6530] | 1.0480 |

Sequential and independent processing produce identical quantized-weight hashes and attack-score payloads for all 40 paired artifacts.
