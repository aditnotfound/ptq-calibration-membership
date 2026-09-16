# Initial repository import

Source: the author's `crying_supp.zip`, SHA-256:

```text
8ca8ff1bbd1036cca071177741957291f245aeb89fda26efc2a6a72c4e2ac3a8
```

## Included

Imported 151 supplied files: 18 package source files, 13 scripts, 29 YAML configurations, 9 test files, 78 reports, the original README, original gitignore, dependency metadata and third-party asset notes.

All scientific source, scripts, configurations and tests remain byte-for-byte identical to the supplied archive. The original README and gitignore are retained in `docs/`; the repository root has a new README and expanded ignore rules.

In 32 report files, a machine-specific Windows home/project prefix was removed from historical corpus paths, leaving relative data paths. No numeric results were changed. The [import manifest](../reproducibility/supplement_manifest.json) records each source hash, repository hash, destination and transformation. Historical reports were not independently recalculated during this import.

## Excluded and unavailable

- Excluded 41 generated `.pyc` cache files. Some referred to sources absent from the archive; bytecode is not a substitute for missing source.
- Raw `results/*_scores.jsonl` and population manifests were not supplied.
- Original natural-text corpus snapshots, CIFAR images, base/quantized model weights and model caches were not supplied and are not uploaded.
- The paper's TeX/PDF files were not included in this code archive. In particular, the unchanged manuscript test cannot find `paper/sections/abstract.tex`.
- No credentials, SSH keys, account settings or later follow-up experiment files were copied into this repository.

## Packaging work and checks

Codex organized the supplied files, wrote the repository documentation and integrity checker, added a lightweight CI workflow, normalized the report paths described above, and ran the available tests. This packaging work does not replace or relabel the original author-supplied research.

The full imported test suite had 25 passing tests, two missing-prerequisite failures and one CUDA skip. See [reproduction notes](reproduction.md#test-status) and the [machine-readable record](../reproducibility/import_validation.json). No GPU quantization run, corpus collection or original-report reproduction was performed for this upload.

The integrity workflow checks hashes, parseability and common secret/file hazards. It does not guarantee the absence of every possible secret and does not validate scientific conclusions. No synthetic passing badge is used to obscure the full-suite outcomes.

## Future changes

The manifest is a fingerprint of this imported snapshot. If you intentionally change an imported file, record the change and update its repository hash/transformation entry while keeping its source hash. Do not regenerate the source hashes to hide differences. Keep new experiment results separate from historical reports.

No license grant has been added. Choose any future open-source license explicitly and review third-party terms first. Keep the repository private until the desired visibility and workshop anonymity rules are settled.
