# Independent GPTQ population replications

3 independent populations contain 128 quantized artifacts and 4096 held-out decisions.

| Population | Shadow | Test | Artifact AUROC | Artifact CF | Raw fixed | Min artifact AUROC | Min artifact CF AUROC |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | 32 | 32 | 1.0000 | 1.0000 | 0.6732 | 1.0000 | 1.0000 |
| fresh 1 | 16 | 16 | 1.0000 | 0.9999 | 0.6684 | 1.0000 | 0.9990 |
| fresh 2 | 16 | 16 | 1.0000 | 0.9989 | 0.6746 | 1.0000 | 0.9961 |
