# Development Corpus Coverage, 2026-07-23

## Scope

This report measures the current 12-model morphology release, through patch
`0435`, on pinned development corpora. The FST binaries used for the run are
byte-identical to the artifacts in the `tamil-morphology` and
`tamil-morph-tokenizer` release repositories.

These corpora were inspected during system development. The results are
coverage and regression diagnostics, not held-out evidence of tokenizer or
downstream-model quality. Protected translation evaluation sets were not read.

## General-Text Coverage

`Handled` means that a Tamil surface received either a direct lexical FST
analysis or a reviewed entity-layer analysis. It excludes suffix heuristics
and lossless byte fallback. `Direct FST` is the stricter morphology-only
measure.

| Development corpus | Tamil spans | Direct FST | Entity only | Handled | Analyzed unique types | Unknown-surface types |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mozhi full | 520,630 | 378,509 (72.70%) | 4,233 (0.81%) | 382,742 (73.52%) | 73,508 / 172,080 (42.72%) | 97,845 |
| Sangraha verified v1 | 1,005,555 | 816,285 (81.18%) | 8,388 (0.83%) | 824,673 (82.01%) | 93,851 / 195,227 (48.07%) | 101,376 |
| Sangraha verified v2 | 1,006,108 | 825,047 (82.00%) | 9,145 (0.91%) | 834,192 (82.91%) | 90,168 / 184,307 (48.92%) | 94,139 |
| Dravidian CodeMix train | 85,465 | 68,003 (79.57%) | 881 (1.03%) | 68,884 (80.60%) | 10,921 / 20,573 (53.08%) | 9,652 |
| TamilTech-QA train | 3,639 | 2,932 (80.57%) | 17 (0.47%) | 2,949 (81.04%) | 1,496 / 2,066 (72.41%) | 570 |

The occurrence-weighted micro-average across these five inputs is:

- 2,621,397 Tamil spans;
- 2,090,776 direct FST analyses, or 79.76%;
- 22,664 entity-only analyses, or 0.86%;
- 2,113,440 handled spans, or 80.62%;
- 507,957 spans without an FST/entity analysis, or 19.38%.

The aggregate is occurrence-weighted. Unique-type counts are not added across
corpora because the inventories overlap.

Mozhi's 97,845 `unknown_tamil_surface` types are not the arithmetic complement
of its 73,508 analyzed types. Another 727 types are handled by controlled
non-FST paths such as suffix heuristics or semantic specials. Unknown input is
still represented exactly by the reversible UTF-8 codec; unknown morphology
and lossless tokenizer coverage are different measures.

## Mozhi Detail

The full pinned Mozhi snapshot contains 8,682 documents. Current results are:

| Domain | Tamil spans | Direct FST | Entity only | Handled | Unknown-surface fallback |
| --- | ---: | ---: | ---: | ---: | ---: |
| News | 309,442 | 258,355 (83.49%) | 2,951 (0.95%) | 261,306 (84.44%) | 47,514 (15.35%) |
| Encyclopedia | 49,943 | 36,675 (73.43%) | 1,156 (2.31%) | 37,831 (75.75%) | 11,974 (23.98%) |
| Classical literature | 161,245 | 83,479 (51.77%) | 126 (0.08%) | 83,605 (51.85%) | 77,314 (47.95%) |

The remaining tail is not a single missing-lexicon bucket. It includes open
names, foreign material, code mixing, spelling and OCR noise, fragments,
classical joins, unattested or unsupported derivations, and genuine residual
morphology gaps. Classical literature is the largest remaining gap and should
not be conflated with modern prose coverage.

Compared with the historical post-`0351` run:

- handled occurrence coverage rose from 71.75% to 73.52%, a gain of 1.76
  percentage points;
- direct FST analyses rose from 368,694 to 378,509;
- analyzed unique surfaces rose from 69,031 to 73,508;
- `unknown_tamil_surface` unique types fell from 102,305 to 97,845.

The current tokenizer's word-boundary policy produces 520,630 Tamil spans,
790 more than the older run over the same documents. Raw count deltas should
therefore be read together with rates and exact denominators.

## Linguistic and Entity Stress Audits

### UD Tamil TTB train and development

The audit contains 6,590 Tamil token occurrences and 2,893 unique Tamil
surfaces. Its headline policy excludes `PROPN` and components of UD multiword
tokens, leaving 4,196 tokens:

- 3,987 have at least one FST analysis: 95.02%;
- 2,959 are exact matches under the audit's lemma, allowed-POS, feature, and
  deterministic-best-analysis policy: 70.52%;
- 209 are unknown;
- the remaining analyzed tokens are divided among lemma, POS, feature, and
  best-analysis mismatches.

UD and the FST use different taxonomic and lemma conventions, so the exact
match rate is a diagnostic, not an intrinsic morphology accuracy score.

### Naamapadam Tamil train

The audit contains 716,045 labeled entity occurrences across 497,882 records.
The final Tamil token in 302,433 entity occurrences receives a core FST
analysis, or 42.24%.

This is not named-entity recall. It measures how often the morphology layer can
analyze the final token of an entity mention. Entity identity and type remain a
separate contextual task; unmatched names must not be bulk-imported as common
nouns merely to increase this percentage.

## Reproducibility

Pinned inputs:

| Input | Pin |
| --- | --- |
| Mozhi | revision `a55b8f464771debb232e0bb4e58fa6486675a03d`, `data/2026-05-30.parquet`, SHA-256 `dfb640852304d2c6e76356f2ae07e197d2843d9df633689686e1aea9bcc715e7` |
| Sangraha verified v1 | prepared SHA-256 `2d512c4039350bb0d5a57ea8fa0c6ed531b26d517781dfd2ad8ec160e81ebff0` |
| Sangraha verified v2 | prepared SHA-256 `0b857a7fc925d4558550c05fa65c039f36303b88dde8f726c4b377ae4f2e8f4f` |
| Dravidian CodeMix train | prepared SHA-256 `eb2f789375fb231ee18799e16b0b0a1b8df3c93885103cbee73e53d392f9c9e0` |
| TamilTech-QA train | prepared SHA-256 `d4c34b6f0cd5a3cd9a92871305a873f8f348c5a8d1de1360d413e6c124810c2b` |
| UD Tamil TTB train/dev | SHA-256 `57f7673bcf070ddc968b05c1fdbc3367593435ad97291bc10a35f42827d7cd69` / `b81f508f4903a606566587c7bb8248bf628d8d634c74bb40e0dd7b9050a0fede` |
| Naamapadam Tamil archive | SHA-256 `bb7e3d023462a4a61c5823581247f91e9706aada8149048ffac9b7829a8ff867` |

The detailed machine-readable outputs are:

- `outputs/hf_dataset_eval/mozhi-full-current-release-0435_summary.json`;
- `outputs/hf_dataset_eval/mozhi-full-current-release-0435_surface_inventory.csv`;
- `outputs/hf_dataset_eval/mozhi-full-current-release-0435_unknown_tamil_surfaces.csv`;
- `outputs/multicorpus_development_audit_current_release_0435/*/summary.json`;
- the corresponding analyzed, unknown, UD diagnostic, and Naamapadam files in
  those output directories.

The principal commands are:

```bash
python scripts/evaluate_tokenizer_on_hf_dataset.py \
  --dataset mozhi-ai/tamil-corpus \
  --revision a55b8f464771debb232e0bb4e58fa6486675a03d \
  --data-file data/2026-05-30.parquet \
  --split train \
  --text-column text \
  --limit 0 \
  --top-n 2000 \
  --name mozhi-full-current-release-0435

python scripts/audit_development_corpus.py \
  --input PATH_TO_PINNED_PARQUET \
  --output-dir outputs/multicorpus_development_audit_current_release_0435/NAME

python scripts/audit_ud_tamil_morphology.py \
  --input outputs/development_corpora/ud/parquet/ta_ttb/train.parquet \
  --input outputs/development_corpora/ud/parquet/ta_ttb/dev.parquet \
  --output-dir outputs/multicorpus_development_audit_current_release_0435/ud_ttb_train_dev

python scripts/audit_naamapadam_entities.py \
  --archive outputs/development_corpora/naamapadam/data/ta_IndicNER_v1.0.zip \
  --member ta_train.json \
  --output-dir outputs/multicorpus_development_audit_current_release_0435/naamapadam_train
```
