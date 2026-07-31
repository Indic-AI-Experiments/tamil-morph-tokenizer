# Productive Modifier Coverage Audit — 2026-07-26

## Why the lexical counts looked too small

Counts such as 642 directly labelled adjectives are counts of explicit lexical
entries, not the system's full adjective coverage. Tamil also forms modifiers
productively from nouns and other categories. Expanding only a hand-written
adjective list would improve a benchmark sample but would not solve the
general coverage problem.

Patches 0439–0443 therefore use two complementary layers:

1. reviewed lexical entries for opaque or lexically restricted forms; and
2. productive noun-class continuations for forms whose spelling and analysis
   are predictable.

The reviewed lists remain intentionally conservative. Productivity belongs in
the continuation grammar, not in a very large generated word list.

## Productive noun modifiers

Patch 0441 attaches reversible modifier continuations to 17 eligible singular
noun-class routes and 20 plural routes. Each route licenses:

- copular adjective forms in `-ஆன`;
- copular neuter/plural nominalizations in `-ஆனது` / `-ஆனவை`;
- privative adjective forms in `-அற்ற`; and
- privative neuter/plural nominalizations in `-அற்றது` / `-அற்றவை`.

The class-aware rewrite handles stem alternations rather than guessing from a
surface suffix. Examples include:

- `மரம் → மரமான, மரமற்ற`
- `தடை → தடையான, தடையற்ற`
- `அளவு → அளவான, அளவற்ற`
- `மரங்கள் → மரங்களான, மரங்களற்ற`

A protected internal join marker prevents unrelated strings ending in similar
letters from being reinterpreted as privatives. Regression exclusions cover
verb lookalikes such as `தோல்வியுற்ற`, `பதிவேற்ற`, and `பொறுப்பேற்ற`.

The 148 class-level continuation relations add approximately 1,011,524
licensed paths to `noun.fst`. This is the main coverage expansion; it is much
larger than the reviewed lexical seed counts.

## Lexical adjective and adverb coverage

Patch 0439 originally added 41 reviewed copular stems and 60 lexically
constrained privatives to the adjective source. Patch 0443 completes the
ownership cleanup: every noun-led relation now lives in `noun.fst`, including
those reviewed exceptions. `adj.fst` retains lexical adjectives and
derivations whose source category is adjective, adverb, demonstrative,
intensifier, or particle.

Patches 0440 and 0442 add typed, compositional adverb readings:

- 26 initial translative adverbs and 111 additional reviewed manner/time forms;
- 6 initial distributives plus 9 remaining corpus-observed distributive types;
- nine formerly opaque common adverbs converted to lemma + source POS +
  translative/adverb features; and
- normalized spelling variants where the variants share one analysis.

Role/predicative translatives such as `விமானியாக`, purpose constructions in
`-ற்காக`, and verbal/complement forms in `-தாக` are excluded from the adverb
expansion. Their shared spelling does not make them manner adverbs.

## Pinned training-inventory audit

The audit combines the pinned multi-corpus recurrence inventory with the frozen
42k training unknown inventory. Counts are unknown surface types followed by
aggregate occurrences.

| Family | Before | After | Recovered |
| --- | ---: | ---: | ---: |
| copular `-ஆன` | 1,045 / 3,379 | 880 / 2,868 | 165 / 511 |
| privative `-அற்ற` | 174 / 715 | 101 / 473 | 73 / 242 |
| reviewed manner suffixes | 367 / 1,423 | 268 / 758 | 99 / 665 |
| distributives | 9 / 33 | 0 / 0 | 9 / 33 |

The residual sets are not a single missing-adjective list. They include plural
and pronominal phrase constructions, dative/purpose forms, role predicates,
verbal forms, lexical false suffix matches, proper names, and bases that still
need independent lexical evidence. They should be classified before any
further grammar expansion.

## Build and validation

The post-0443 build produced:

| Model | Paths | States | Arcs | Size |
| --- | ---: | ---: | ---: | ---: |
| `noun.fst` | 70,014,090 | 82,855 | 212,072 | 862,557 bytes |
| `adj.fst` | 3,081 | 1,381 | 2,206 | 9,864 bytes |
| `adv.fst` | 4,592 | 2,819 | 3,805 | 18,856 bytes |

The morphology source and its build commands live in the sibling
`tamil-morphology` repository. Source validation commands:

```sh
python3 fst/build/build_fsts.py
python3 fst/tests/run_fst_regressions.py
```

The regression run passed 491 miscellaneous morphology checks, 110 inverse
checks, 138 forward-good checks, 2,071 finite-relation reversibility checks,
and all heuristic, Wiktionary-resolution, and unknown-review checks. A
permanent ownership gate enumerates all 3,081 adjective paths and fails if any
noun-led analysis or untyped privative reappears.

After copying the checksum-pinned runtime into this canonical tokenizer, the
bounded signature refresh replaced the complete adjective codebook slice and
merged the reviewed noun relation. The fixed vocabulary remains at 140,922
tokens and 139,895 lemmas. All 542 tokenizer tests passed, including fixed-ID
and exact round-trip validation. The post-0443 codebook contains 54,263
model-qualified semantic keys and 94,569 exact patterns.

## Interpretation

The correct conclusion is not “the adjective model now has only a few dozen
more words.” The system now has:

- a nonredundant adjective/adverb lexicon for opaque items;
- productive, class-constrained modifier morphology for more than one million
  noun paths;
- compositional analyses that preserve lemma and grammatical signal; and
- explicit negative tests at suffix boundaries where overgeneration is risky.

Further work should classify the residual corpus inventory by construction
type and lexical evidence rather than bulk-importing every `-ஆன`, `-அற்ற`, or
`-ஆக` surface.

## Final ownership boundary

The standalone adjective relation now contains **662 distinct bases**, **3,081
paths**, and **3,080 distinct written forms**. Of those bases, 648 have
adjective-leading analyses; the remaining 14 begin with an adverb,
demonstrative, intensifier, or particle analysis. It contains no noun-led
analysis.

Before patch 0443, `adj.fst` contained 2,047 noun-led paths. Of those, 1,070
were exact duplicates already present in `noun.fst`; 977 reviewed paths needed
to be migrated. All 5,128 pre-change adjective paths remain available across
the combined noun/adjective interface. Seventy legacy privative paths were
corrected by adding their previously missing explicit `+noun` category.

This is an ownership and maintenance simplification, not a coverage
reduction. Human-readable tokenizer/API output still shows the lemma and
semantic features, for example:

```text
மாசற்ற -> மாசு <POS_NOUN> <PRIVATIVE_WITHOUT> <ADJ_PARTICIPLE> <POS_ADJ>
```
