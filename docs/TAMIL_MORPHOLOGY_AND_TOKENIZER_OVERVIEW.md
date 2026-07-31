# Tamil Morphology and Tokenizer System

## What This Project Is

This project combines a finite-state Tamil morphological analyzer with a
lossless, morphology-aware representation for language models. It has two
separable products:

1. **Tamil morphology runtime**: analyzes a surface word into a lemma and
   grammatical features, and can generate a surface from an analysis.
2. **Tamil morphology tokenizer**: converts those analyses into a bounded token
   vocabulary while retaining enough realization information to reconstruct
   the original UTF-8 input exactly.

The FST work began from the ThamizhiMorph models described in academic work.
The current system is not an unchanged copy. It incorporates a long reviewed
patch series covering lexical expansion, class corrections, missing
inflections, ambiguity, productive auxiliaries, modern written Tamil,
colloquial forms, Unicode defects, and inverse-generation correctness.

The lexical evidence combines the Tamil Lexicon, Tamil Wiktionary, and Vuizur.
Corpus observations are used to find gaps and test productive families; corpus
frequency alone never licenses an FST root or class assignment.

## Current Release Snapshot

These are the checksum-pinned post-0443 research-preview statistics. Counts describe
different layers and must not be added unless a union is explicitly named.

| Measure | Count | Meaning |
| --- | ---: | --- |
| source lemma dictionary | 129,020 | normalized dictionary lemmas used for coverage auditing |
| runtime-recognized source lemmas | 102,726 | bare source lemmas with at least one analysis |
| runtime-unrecognized source lemmas | 26,294 | mostly historical/rare material, names, noise, or unresolved lexical policy |
| explicit unique noun roots | 127,311 | unique roots assigned to at least one noun LexC class, including roots beyond the 129,020 audit list |
| explicit unique verb lexical strings | 11,399 | unique atomic verb roots/stems across the compiled verb models |
| noun class/subclass paths | 23 | 16 broad numbered classes plus explicit phonological/declensional splits |
| verb base/irregular classes | 24 | productive and irregular conjugation owners across the verb FSTs |
| productive auxiliary continuation classes | 70 | active/passive connector and predicative construction templates |
| productive auxiliary route groups | 47 | symbolic compression groups for lemmas sharing the same reachable continuations |
| productive auxiliary root relations | 4,913,950 | licensed lemma/connector/continuation paths before continuation templates are applied |
| audited ending/formation families | 38 | longest-suffix evidence groups such as `-க்கை`, `-விப்பு`, `-ிப்பு`, `-மை`, `-தல்` |
| named Foma definitions | 242 | named grammar, rewrite, cleanup, and composition definitions in compiled source entry files |
| unique LexC sections | 360 | lexical root owners and continuation sections across the compiled source files |
| distinct source/runtime tags | 224 | raw analysis labels observed in source declarations or lemma runtime analyses |
| representative paradigm probes | 574,379 | inverse-generation probes across explicit noun and verb roots |
| paradigm probe failures | 0 | missing or malformed outputs found by that audit |
| compiled FSTs | 12 | packaged runtime transducers |
| semantic tokens | 284 | fixed grammatical/semantic labels available to the codec |
| fixed vocabulary lemmas | 139,895 | atomic lexical tokens reachable from the released FST and decomposition system |
| fixed vocabulary tokens | 140,922 | lemmas plus semantic, structural, realization, byte, and 378 Tamil-grapheme tokens |
| semantic signature keys | 54,263 | distinct canonical semantic token sequences after derivable labels are removed |
| exact raw-tag patterns | 94,569 | distinct realization-sensitive patterns stored in the checksum-pinned codebook |
| compact symbolic upper analyses | 2,107,907,215 | unique upper analyses counted from compact symbolic inventories |
| enumerated relation paths | 2,381,414,364 | post-0443 relation count after removing 1,070 duplicate noun/adjective paths |
| exact signature round-trip failures | 0 | failed inverse-forward witnesses among all 94,569 patterns |

The complete generated tables are in
[`FST_CLASS_RULE_VOCABULARY_REFERENCE.md`](FST_CLASS_RULE_VOCABULARY_REFERENCE.md).
The machine-readable source is `outputs/fst_system_audit/`.

## The Twelve FSTs

| Model | Responsibility |
| --- | --- |
| `noun.fst` | noun declension, number, case, oblique stems, clitics, and noun-derived continuations |
| `pronoun.fst` | personal, demonstrative, reflexive, and interrogative pronoun paradigms |
| `verb-c3.fst` | verb class 3 |
| `verb-c4.fst` | verb class 4 |
| `verb-c11.fst` | strong class 11 |
| `verb-c12.fst` | class 12 |
| `verb-c62.fst` | class 6.2 |
| `verb-c-rest.fst` | the other numbered and reviewed irregular verb classes |
| `verb-auxiliary.fst` | productive auxiliary chains, passive/modal paths, and typed nonfinite connectors |
| `adj.fst` | lexical adjectives plus adjective-, adverb-, demonstrative-, intensifier-, and particle-derived adjectival analyses; no noun-led paths |
| `adv.fst` | adverbs and productive adverbial relations |
| `part.fst` | particles, postpositions, quantifiers, complementizers, selected closed classes, and abbreviations |

They remain separate to preserve provenance and class ownership. The runtime
merges and deduplicates analyses while retaining the contributing model names.

## Noun Morphology

Tamil noun inflection cannot be predicted safely from the final Unicode code
point alone. The system therefore distinguishes lexical classes by the
interaction of the citation form, oblique stem, plural allomorph, and case
attachment.

The 23 compiled class/subclass paths include:

- vowel-final classes with `வ்` or `ய்` obliques;
- nonalternating consonant-final nouns;
- multiple short-`உ` behaviors, including deletion and strengthening;
- `று -> ற்று`, `ண்`, `ன்`, `ல் -> ற்`, and `ள் -> ட்` alternations;
- human versus nonhuman `ன்` behavior;
- retained, alternating, and dual `ள்` subclasses;
- `ம் -> த்து` obliques;
- direct versus `ற்று` behavior for selected `ர்`-final nouns.

For example:

```text
மரங்களை
surface:  மரங்களை
analysis: மரம்+noun+pl+acc
tokens:   மரம் <POS_NOUN> <NUM_PL> <CASE_ACC>
```

The surface is metadata, not a duplicate model token. The noun class determines
that `மரம்` realizes an accusative plural as `மரங்களை`.

### Ending families are audits, not automatic morphology

The 38 longest-suffix groups expose vocabulary structure and systematic gaps.
Narrow formations such as `-க்கை`, `-விப்பு`, `-ிப்பு`, `-ைப்பு`, `-ப்பு`,
`-வியல்`, `-ியம்`, and `-பூ` have strong observed class invariants and are
checked for class outliers. Broad endings such as `-தல்`, `-ி`, `-ு`, `-ன்`,
or `-ர்` mix several lexical categories and cannot justify bulk import.

This distinction prevents a common coverage error: treating every string with
the same final letters as a member of the same morphological class.

## Productive Nominal Modifiers and Adverbials

Eligible singular and plural noun classes productively license reversible
copular modifiers in `-ஆன`, privatives in `-அற்ற`, and their neuter/plural
nominalizations. The class grammar handles stem alternations:

```text
மரம்+noun+nom+cop=ஆ+adjpart=ன          -> மரமான
மரம்+noun+privative=அற்ற+adjpart=அ+adj -> மரமற்ற
தடை+noun+privative=அற்ற+adjpart=அ+adj  -> தடையற்ற
```

These class continuations add approximately 1.01 million noun paths. Reviewed
noun exceptions also live in `noun.fst`; lexical adjective lists remain in
`adj.fst` for opaque stems and adjective-owned derivations. This gives every
noun-derived modifier one model owner without reducing the combined language.

Adverb coverage preserves the source lemma and POS:

```text
முதல்முறை+noun+trans=ஆக+adv -> முதல்முறையாக
பிஸி+adj+trans=ஆக+adv        -> பிஸியாக
மாதம்+noun+time+distrib+adv  -> மாதந்தோறும்
```

Role predicates, purpose forms, and verbal/complement `-தாக` forms are not
bulk-labelled as adverbs. See
[`PRODUCTIVE_MODIFIER_COVERAGE_2026_07_26.md`](PRODUCTIVE_MODIFIER_COVERAGE_2026_07_26.md).

## Verb Morphology

The 24 base/irregular conjugation owners cover numbered ThamizhiMorph classes
and reviewed modern paradigms such as `போ`, `வா`, `கேள்`, and `நில்`. Verb
analyses can encode finiteness, tense, polarity, person/number/gender,
imperative or conditional mood, voice, participles, verbal nouns, causatives,
and register.

Citation forms ending in `-தல்` are treated carefully. A dictionary headword
such as an action nominal may provide evidence for a verb stem, but the written
nominal itself is not forced to be an ordinary finite verb. For example,
`தாக்கல்` preserves both its lexical noun and derived action-nominal readings:

```text
தாக்கல் <POS_NOUN> <CASE_NOM>
தாக்கு <POS_VERBAL_NOUN> <ACTION_NOMINAL>
```

Phrase-level constructions such as `தாக்கல் செய்` should eventually receive
phrase semantics; corrupting the single-word POS inventory is not a substitute.

## Auxiliaries and Typed Connectors

Tamil verbal compounds contain grammatical information in the connector as
well as the final auxiliary. A generic `<AUXILIARY>` token would lose that
structure. The tokenizer emits the auxiliary lemma and a typed link:

```text
படித்துக்கொடுத்தான்
analysis: படித்துக்கொடு+verb+fin+complex+nonattitude+strong+past=இன்+3sgm=ஆன்
tokens:   படி <LINK_VPART> கொடு <TENSE_PAST> <PERSON_3SG_MASC>
```

`<LINK_VPART>` states that the first verb is connected through a verbal
participle. `<LINK_INFINITIVE>` marks an infinitival connection. Passive `படு`
is represented as `<VOICE_PASSIVE>` when it is grammatical voice rather than
an independent lexical event.

The dedicated auxiliary FST has 4,913,950 licensed root relations feeding 70
continuation classes and compresses lemmas
with identical reachability into 47 symbolic route groups. It avoids storing
tens of thousands of compound surface lemmas as independent lexical tokens and
allows newly licensed base verbs to participate systematically.

```text
செய்யப்படணும்
செய் <VOICE_PASSIVE> <MODAL> <LINK_INFINITIVE> வேண்டு
     <TENSE_FUTURE> <PERSON_3SG_NEUT> <REGISTER_COLLOQUIAL>
```

## Sandhi and Realization

Sandhi is not discarded as spelling noise. The FST relations encode stem
alternation and linking material, including `க்`, `ச்`, `த்`, and `ப்` paths.
Semantically relevant sandhi has named tokens such as `<SANDHI_K>`. Exact raw
realization is retained by the signature codebook when multiple surface
realizations share the same canonical semantic sequence.

This separation removes redundancy without losing the ability to regenerate
the surface:

- the lemma and semantic tokens carry reusable linguistic content;
- the FST supplies the default realization;
- a bounded variant token is emitted only when the semantic sequence has more
  than one valid exact realization and the nondefault choice is required;
- ordinary unknown Tamil uses fixed reversible grapheme tokens; malformed,
  unsupported, or other arbitrary input uses bounded UTF-8 byte tokens.

## Ambiguity

The analyzer preserves every valid FST analysis. A deterministic ranking
heuristic selects `best_analysis` for applications that need one reading, but
selection does not delete alternatives.

In compact ambiguity mode, the longest common semantic prefix is emitted once.
`<READINGS>` starts the residual alternatives and `<ALT>` separates them. This
preserves feature co-occurrence without duplicating the word or maintaining a
parallel candidate-token vocabulary. Different lemmas simply occur inside
their respective complete residual readings.

This policy separates three questions:

1. **coverage**: did the FST include a valid reading?
2. **precision**: did it include an invalid reading?
3. **ranking**: did a context-free heuristic choose the intended reading?

Only the first two are properties of the FST language. Contextual
disambiguation is a later model or phrase-level task.

## Semantic Signatures

A semantic signature is the canonical sequence of model-relevant tokens for an
analysis after labels that can be inferred from other labels are removed. For
example, a verb analysis does not need separate generic `verb`, `finite`, and
`complex` tokens when the surviving tense, agreement, voice, link, and
auxiliary tokens already determine that structure under the schema.

The release contains:

- **54,263 semantic keys**: distinct canonical meanings/feature bundles;
- **94,569 exact patterns**: semantic keys plus distinctions needed for exact
  realization;
- a maximum of **64 exact variants** for one semantic key.

The post-0443 compact symbolic relation count is 2,107,907,215. The
post-0443 relation count is 2,381,414,364 paths. The
dedicated auxiliary inventory
symbolically collapses repeated upper analyses reachable by multiple lower
routes; path enumeration counts those routes separately. This is expected and
does not mean that analyses are missing.

## Generated and Heuristic Forms

Some morphology consumers need a finite surface dictionary; the tokenizer
does not. The morphology release audits these optional static artifacts:

| Static inventory | Count |
| --- | ---: |
| direct and secondary generated forms | 3,084,718 |
| controlled heuristic forms | 0 |
| full static dictionary | 3,111,433 |

“Heuristic” refers to bounded static generation from a source citation lemma
classified into a plausible productive stem/class even though the citation
string itself has no direct runtime analysis. The current release records the
classifications for review but includes zero heuristic surfaces. They are not
needed in the tokenizer wheel.

The tokenizer needs the FSTs, its bounded lexical/semantic vocabulary, and the
reversible fallback. It does not need the three-million-line surface list.

## Reversibility

The structured codec preserves surface spans and offsets for inspection but
does not emit a second copy of an analyzed surface into the model token stream.
Decoding uses:

1. lemma and semantic tokens;
2. the inverse FST;
3. an exact-pattern variant only when necessary;
4. UTF-8 bytes for genuinely unknown or nonmorphological material.

The checksum-pinned signature audit found a witness and completed an
inverse-forward round trip for all 94,569 patterns, with zero failures. This is
a structural release gate, not a claim that every possible Tamil sentence has
the intended contextual analysis.

## Coverage and Honest Limits

On the contaminated Mozhi development corpus, the final release handles
372,996 of 519,840 Tamil spans: 368,694 by direct FST analysis and 4,302 by the
reviewed entity layer. The remaining 145,719 occurrences comprise 102,305
unique surfaces.

That 28.03% occurrence fallback rate is not equivalent to 28% missing common
Tamil vocabulary. The tail includes open names, foreign words, spelling and
OCR noise, fragments, classical joins, code mixing, and productive structures
that were not licensed without sufficient evidence. The codec remains exact
for them. Development coverage is a diagnostic; protected datasets must be
used for the final comparative evaluation.

The strongest supported claims for this release are:

- broad, systematically tested Tamil morphological coverage;
- explicit preservation of ambiguity;
- lossless bounded encoding for all UTF-8 input;
- zero failures in the published class-probe and signature-witness gates;
- substantially richer Tamil grammatical structure than generic subword
  tokenization exposes directly.

Claims about downstream translation quality, sample efficiency, or superiority
to a particular tokenizer require the planned controlled experiments.

## Reproducibility

Canonical generated details:

- `docs/FST_CLASS_RULE_VOCABULARY_REFERENCE.md`
- `outputs/fst_system_audit/stats.json`
- `outputs/fst_system_audit/*.csv`
- `tamil_morph_tokenizer/data/vocabulary/manifest.json`
- `outputs/reversible_signature_audit/summary.json`
- `outputs/signature_pattern_roundtrip_audit/summary.json`
- `morphology.lock.json`
- `tokenizer.release.json`

Regenerate the reference and release manifests with:

```bash
.venv/bin/python scripts/audit_fst_system.py
.venv/bin/python scripts/build_release_manifests.py
```
