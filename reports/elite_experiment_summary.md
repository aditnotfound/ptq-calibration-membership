# Strengthened experiment summary

Exact GPTQ/AutoRound population match: `True`.

Exact natural-text GPTQ/AWQ population match: `True`.

Scaling sweep token-pool match: `True`.

Scaling sweep membership-design match: `True`.

| Run | Method | Compute | W | N | Source | Artifact AUROC | Output AUROC | Unseen-candidate artifact | Unseen-candidate output | Reference PPL ratio |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| gptq_natural_postcutoff_report | GPTQ | float16 | 4 | 128 | text_jsonl | 1.0000 | 0.8738 | 1.0000 | 0.6544 | 1.0571 |
| awq_natural_postcutoff_report | AWQ | float16 | 4 | 128 | text_jsonl | 0.7852 | 0.5033 | 0.5016 | 0.4952 | 1.0537 |
| gptq_pythia410m_natural_report | GPTQ | bfloat16 | 4 | 128 | text_jsonl | 1.0000 | 0.7402 | 1.0000 | 0.5977 | 1.0744 |
| gptq_homogeneous_no_nonce_report | GPTQ | float16 | 4 | 128 | synthetic | 1.0000 | 0.5474 | 0.9910 | 0.5329 | 1.1060 |
| matched_gptq_report | GPTQ | float16 | 4 | 128 | synthetic | 1.0000 | 0.8112 | 1.0000 | 0.6948 | 1.0461 |
| matched_autoround_report | AutoRound | float16 | 4 | 128 | synthetic | 0.9299 | 1.0000 | 0.6306 | 1.0000 | 0.9933 |
| scale_gptq_n64_w4_report | GPTQ | float16 | 4 | 64 | text_jsonl | 1.0000 | 0.9799 | 1.0000 | 0.7798 | 1.0491 |
| scale_gptq_n128_w4_report | GPTQ | float16 | 4 | 128 | text_jsonl | 1.0000 | 0.8279 | 0.9940 | 0.6312 | 1.0472 |
| scale_gptq_n256_w4_report | GPTQ | float16 | 4 | 256 | text_jsonl | 1.0000 | 0.7066 | 0.9360 | 0.5797 | 1.0480 |
| scale_gptq_n128_w8_report | GPTQ | float16 | 8 | 128 | text_jsonl | 1.0000 | 0.7379 | 0.9801 | 0.5717 | 1.0023 |
