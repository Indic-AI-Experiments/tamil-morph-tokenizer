# Tokenizer Output and Fixed-Vocabulary Contract

## Purpose

This document defines the public analysis record and the model-facing token
stream for the Tamil morphology-aware tokenizer. The input surface is retained
as metadata but is not emitted as an atomic model token.

`compact_ambiguity` is the default for `TamilMorphTokenizer`, the CLI, and the
reversible codec. It factors the longest semantic prefix shared by all distinct
readings, then emits the residual readings after one `<READINGS>` marker,
separated by `<ALT>`. This preserves feature co-occurrence without candidate
token families or repeated start/end boundaries. `best` and `all_analyses` are
explicit opt-in modes.

## Word Analysis Record

The primary diagnostic/API representation is:

```json
{
  "surface": "மரங்களை",
  "span": {"start": 0, "end": 8},
  "lemma": "மரம்",
  "tokens": ["மரம்", "<POS_NOUN>", "<NUM_PL>", "<CASE_ACC>"],
  "selected_analysis": {
    "raw": "மரம்+noun+pl+acc",
    "model": "noun.fst",
    "lemma": "மரம்",
    "tags": ["noun", "pl", "acc"]
  },
  "analyses": [
    {
      "raw": "மரம்+noun+pl+acc",
      "model": "noun.fst",
      "lemma": "மரம்",
      "tags": ["noun", "pl", "acc"]
    }
  ],
  "ambiguous": false,
  "fallback": null
}
```

`surface` is observability and reconstruction metadata. It is never inserted
into `tokens` merely because it appeared in the input.

`tokens` is the single model-facing sequence. The reversible codec inserts
bounded structural, realization or residual tokens into that sequence only
when they are required by the decoding contract.

## Canonical Ambiguity Grammar

Earlier prototypes used dynamic lemma-candidate strings, a parallel family of
207 candidate semantic labels, or two analysis-boundary tokens around every
reading. Those representations were respectively unbounded, lossy, and
redundant. They are not part of the current vocabulary.

The canonical grammar is:

```text
common-prefix <READINGS> best-residual <ALT> alternative-residual ...
```

For same-lemma case ambiguity:

```text
இந்தியா <POS_NOUN> <READINGS> <CASE_LOC> <ALT> <CASE_ABL>
```

For different lemmas:

```text
<READINGS>
எத்தனை <POS_QUANTIFIER> <DEICTIC_INTERROGATIVE>
<ALT>
எத்தன் <POS_NOUN> <CASE_ACC>
```

The deterministic best reading is first. Remaining distinct semantic readings
are sorted canonically. Semantically identical FST analyses collapse to one
model reading while remaining available in record metadata. In a reversible
word span, `<FST_SIGNATURE_START>` terminates the ambiguity section; in a
`TokenizedWord`, the token tuple boundary does so. No ambiguity-end token is
needed.

### Dynamically generated morphology fallbacks

An unmapped raw tag currently becomes `<MORPH_RAWTAG>`. This is readable for a
demo but violates a frozen-vocabulary contract. Release builds must require
every runtime-observed tag to be mapped and must version the tag schema.

### Raw input surfaces

Earlier compact and all-analysis modes put the complete input word in the
token sequence. Analyzed words are now surface-free in all three modes.
Unknown Tamil still defaults to the whole surface in the ordinary demo
tokenizer, so that remaining path is an unbounded runtime token.

Analyzed surfaces move to record metadata. In `StructuredReversibleCodec`,
ordinary unknown Tamil uses a released 378-token grapheme alphabet. A span
containing an unsupported grapheme, joiner sequence, or malformed/mixed
combining sequence uses bounded UTF-8 bytes as the final exact escape.

### Punctuation and abbreviations

Punctuation is split from adjacent lexical words and preserved exactly in the
reversible surface stream. It does not receive semantic labels that duplicate
its bytes. Periods internal to decimals and genuine multi-segment dotted Tamil
abbreviations remain within those structured spans; terminal punctuation after
them is separate. A single Tamil word followed by a period is never classified
as an abbreviation by shape alone, so `பா.` becomes `பா` plus `.`. Explicit FST
abbreviation readings remain valid and participate in the same canonical
ambiguity grammar. See `PUNCTUATION_AND_ABBREVIATION_POLICY.md`.

## Implemented Reversible Prototype

`StructuredReversibleCodec` produces diagnostic span metadata and one
model-facing `tokens` sequence. Conditional realization selectors, Tamil
grapheme fallback, and byte escape, when needed, occur inside that same exactly
decodable sequence.

The exact raw FST tag suffix is recovered from a checksum-pinned codebook keyed
by semantic morphology and one of 12 fixed model tokens. A non-default pattern
uses one bounded `<TAG_VARIANT_n>`. Consequently,
`decode_tokens(tokens)` does not consult surface or analysis metadata.
`FixedVocabulary` assigns deterministic line-number IDs and verifies the token
file checksum. The current exhaustive artifact contains 140,922 tokens,
including 139,895 lemma tokens, 378 Tamil grapheme tokens, and a 284-entry
model-factor region containing 222 grammatical or semantic labels plus 62
secondary lexical components. Its released morphology relation contains
2,107,907,215 compact
symbolic upper analyses. Applying the exact noun/adjective ownership delta to
the pinned relation inventory gives 2,381,414,364 paths; the global
lower-language audit has not been rerun while synthetic data
generation is active. The fixed vocabulary
manifest pins the FST artifacts and production entity-gazetteer checksums. It
reports zero blocking lemma issues, zero splitter-unreachable lemmas, and zero
exact signature round-trip failures.

Verb semantic output is canonical. Broad labels such as `<POS_VERB>`,
`<VERB_FINITE>`, `<VERB_NONFINITE>`, `<VERB_SIMPLE>`, `<VERB_COMPLEX>` and
verb-strength/class labels are not emitted when their information is already
implied by the model signature and the remaining morphology. Specific tense,
agreement, voice, aspect, polarity, nominalization, participle, infinitive and
typed-link tokens remain explicit.

## Fixed Token Families

The model vocabulary consists of:

1. Atomic lemmas and currently retained FST lexical strings.
2. Curated semantic morphology tokens.
3. Structural tokens for reading alternatives, word boundaries and fallback.
4. Bounded realization-choice tokens.
5. UTF-8 byte tokens for exact residual and unknown-text coverage.
6. Required BOS/EOS/padding/application tokens.

`<WORD_START>` is the sole general span boundary in the model stream. Exact
whitespace, punctuation and unknown material use direct contiguous `<BYTE_XX>`
tokens. `<WORD_END>`, `<BYTE_SPAN_START>` and `<BYTE_SPAN_END>` are excluded
because the decoder can infer those boundaries without losing information.

## HTTP API Contract

`POST /tokenize` returns one authoritative global `tokens` sequence and its
parallel `token_ids` sequence. Diagnostic `records` retain surfaces, analyses
and per-word semantic views but do not define the training token count. The API
does not trim input: leading and trailing whitespace participate in the same
exact reversible stream.

Generated inflected surface words are not vocabulary entries.

## Lemma Vocabulary

The lemma vocabulary is not identical to `lemma_dictionary.txt`.
`scripts/build_tokenizer_vocabulary.py` derives it by exhaustively enumerating
the upper language of every runtime FST, then augments it only with semantic,
structural, realization, model, byte and reserved tokens.

The emitted first field is not always an atomic linguistic lemma. A reviewed
map renders 78,538 FST-only productive compounds as a canonical base connected
to following lemmas by
`<LINK_VPART>` or `<LINK_INFINITIVE>`. Productive passive `படு` is normalized
to `<VOICE_PASSIVE>`. Unique chains recover the composite lemma from the typed
map; colliding chains use a bounded `<COMPOUND_VARIANT_n>` selector.

The vocabulary excludes those 78,538 reviewed decomposed strings from atomic
token IDs while retaining their FST analyses and typed decomposition records.
The released vocabulary contains 139,895 lemma tokens and no unresolved
connector or adjectival-participle FST-only compounds.

Every lemma entry must record:

```text
lemma
token_id
models
classes
lexical_sources
normalization
release_version
```

Source lemmas that no FST can emit remain research/coverage candidates and do
not automatically consume atomic model IDs.

## Ambiguity Contract

All FST analyses remain available in `analyses`. The deterministic best
analysis is the first reading and drives the exact FST signature and realization
selector. Every distinct semantic reading is also present in the same model
stream through `<READINGS>/<ALT>` grouping. The stream does not repeat the
surface and does not contain an unbounded or parallel candidate-token family.

## Compatibility and Versioning

Each released vocabulary has an immutable token-to-ID mapping and records:

```text
tokenizer schema version
morphology/FST release version
semantic-tag schema version
normalization version
fallback-codec version
vocabulary SHA-256
FST artifact SHA-256 values
```

Adding, removing or renumbering a token requires a tokenizer vocabulary
version change.
