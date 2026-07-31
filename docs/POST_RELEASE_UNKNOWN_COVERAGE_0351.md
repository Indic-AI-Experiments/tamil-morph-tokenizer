# Post-Release Unknown Coverage 0351

> Historical milestone record. Counts below describe release 0351 and are not
> current-release statistics; use `release/*.json` and
> `outputs/fst_system_audit/stats.json` for current values.

## Scope

Patch batch `0351` is an evidence-qualified follow-up to the 0350 morphology
release. It targets recurring unknowns found in at least two development
corpora, not isolated Mozhi strings. The batch adds 40 reviewed common
noun/loan readings, productive accusative focus/all continuations, 24
closed-class colloquial surfaces with 25 analyses, and class-wide colloquial
`வேண்டும் -> -ணும்` modal realization over licensed infinitives and passives.

Representative recoveries include `திரையில்`, `அரங்கில்`, `ருசியாக`,
`கூட்டத்தையே`, `மரத்தையெல்லாம்`, `யாரு`, `என்னோட`, `இதுல`, `இவங்க`,
`இருக்கணும்`, `செய்யணும்`, and `செய்யப்படணும்`. The modal analysis retains
the base verb, `<LINK_INFINITIVE>`, auxiliary lemma `வேண்டு`, `<MODAL>`,
future/neuter realization, and `<REGISTER_COLLOQUIAL>`.

## Cross-Corpus Result

All rates include reviewed entity-only handling and also record direct FST
coverage separately.

| Development corpus | 0350 handled | 0351 handled | Gain | 0351 unique unknowns | Unique reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mozhi full | 372,337 | 372,996 | +659 | 102,305 | -296 |
| Sangraha verified v1 | 796,381 | 798,995 | +2,614 | 107,808 | -512 |
| Sangraha verified v2 | 805,296 | 807,942 | +2,646 | 100,376 | -496 |
| Dravidian CodeMix train | 64,744 | 65,827 | +1,083 | 10,732 | -119 |
| TamilTech-QA train | 2,694 | 2,794 | +100 | 669 | -58 |

The final Mozhi split contains 519,840 Tamil spans. Direct FST analysis covers
368,694 occurrences; reviewed entity-only analysis covers 4,302; unknown
fallback covers 145,719. The increase is therefore morphological/lexical, not
an entity-gazetteer accounting change.

On the recurring-unknown union, staged models recover 279 types and 6,299
summed corpus occurrences: 227 noun, 28 auxiliary, and 24 particle/closed-
class types. Larger gains in both Sangraha samples and CodeMix show that the
batch is not Mozhi-specific memorization.

## Reversibility Defect Found And Fixed

The exhaustive signature witness audit exposed 64 forward-only reviewed
relations from the earlier finite-union compiler. Foma brace literals encoded
the complete analysis as character symbols, while the base FST used existing
multichar morphology symbols; forward surface lookup worked, but inverse
lookup could not follow the same upper path. Replacing those with whole-string
symbols repaired inverse lookup but could shadow longer surfaces such as
`எதிராக` through greedy tokenization.

The shared builder now reads each base FST alphabet, segments both sides using
the existing symbols, and adds only missing individual characters. This
introduces neither incompatible upper paths nor surface-shadowing multichar
symbols. Source regressions now inverse-check all 140 direct-union TSV pairs.
The checksum-pinned exhaustive audit passes all 35,262 exact patterns over
382,919,216 enumerated relation paths with zero failures.

## Released Inventories

| Inventory | Count |
| --- | ---: |
| Lemma dictionary | 129,020 |
| Direct static-generator union | 3,774,096 |
| Controlled heuristic forms | 8,049,056 |
| Generated/secondary union | 10,207,184 |
| Full static dictionary | 10,234,220 |
| Directly runtime-recognized dictionary lemmas | 102,345 |
| Semantic signature keys | 21,470 |
| Exact raw-tag patterns | 35,262 |
| Fixed vocabulary tokens | 140,263 |
| Fixed vocabulary lemmas | 139,514 |

The lemma audit partitions the 129,020 dictionary entries into 87,286
runtime-analyzed explicit LexC entries, 15,059 runtime-analyzed entries without
an explicit LexC row, 25,924 controlled heuristic-only classifications, and
751 unclassified entries.

## Release Gates

- Source positive, rejected-form, dictionary, and full-mode regressions pass.
- All 140 direct-union finite relation pairs are inverse-generatable.
- Required morphology passes 149/149.
- Exact signature witnesses pass 35,262/35,262 with zero failures.
- The fixed vocabulary has zero blocking or splitter-unreachable lemmas.
- The tokenizer suite passes 1,029 tests with one optional skip.

Residual unknowns remain a mixture of classical joins, productive structures
not yet licensed, names, loans, spelling/transcription variants, fragments,
and noise. They remain reversible through unknown-surface encoding. Further
FST changes require a canonical analysis, independent evidence, a generalized
family, and contrastive negative tests; zero unknown types is not the target.
