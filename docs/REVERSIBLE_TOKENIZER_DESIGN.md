# Reversible Tamil Morphology Tokenizer Design

## Implemented Status

The package implements an independently decodable prototype in
`tamil_morph_tokenizer.codec.StructuredReversibleCodec`:

- analyzed spans use lemma and semantic morphology tokens;
- inverse lookup is restricted to the originating FST model;
- a bounded `<REALIZATION_n>` token is emitted only for a non-default exact
  inverse surface;
- unknown, non-Tamil, whitespace and non-round-trippable spans use the fixed
  256-token UTF-8 byte alphabet;
- productive compounds use typed `<LINK_VPART>` and `<LINK_INFINITIVE>` edges;
- a bounded `<COMPOUND_VARIANT_n>` selects among colliding typed chains;
- each analyzed word carries a lossless FST signature made from fixed model,
  structure and byte tokens, without carrying the input surface;
- span boundaries and every input code point are preserved;
- `decode(encode(text)) == text` is regression-tested for representative noun,
  verb, mixed-script, whitespace, emoji, unknown and decomposed-Unicode input.

`decode_tokens(encoding.tokens)` uses only the flat token stream. It does
not read `surface`, `selected_analysis`, candidate lists or other diagnostic
span metadata. The remaining step from tokens to IDs is to freeze and publish
the vocabulary mapping; it does not require a codec design change.

## Reversibility Requirement

For the selected reversibility mode:

```text
decode(encode(text).input_ids) == text
```

Byte-exact mode preserves the original UTF-8 text. An optional normalized mode
may instead guarantee equality after a declared normalization such as NFC.
The two claims must never be conflated.

Semantic, structural and conditional residual tokens share one model-facing
sequence. Their conceptual roles differ, but they are not separate channels.

## Encoding Record

```json
{
  "surface": "மரங்களை",
  "lemma": "மரம்",
  "tokens": [
    "<WORD_START>",
    "மரம்",
    "<POS_NOUN>",
    "<NUM_PL>",
    "<CASE_ACC>",
    "<FST_SIGNATURE_START>",
    "<FST_MODEL_NOUN>",
    "<TAG_VARIANT_1>",
    "<FST_SIGNATURE_END>",
    "<REALIZATION_1>"
  ]
}
```

The UI may filter or annotate this sequence for explanation, but there is only
one token channel. `surface`, analysis candidates and source spans are metadata.

## When a Realization Token Is Emitted

A realization token is emitted only when the selected exact FST analysis does
not deterministically identify the input surface under the released decoder.

Algorithm:

1. Preserve the selected raw analysis, including realization material after
   `=`.
2. Inverse-query the originating FST with that exact raw analysis.
3. Normalize, deduplicate and deterministically order the returned surfaces.
4. Confirm that the input surface occurs in the candidate set.
5. If there is one candidate, emit no realization token.
6. If there are multiple candidates and the input is the default candidate,
   emit no token when omission is unambiguous by contract.
7. Otherwise emit `<REALIZATION_n>` selecting the input candidate.
8. If the input cannot be reproduced, use residual/byte fallback rather than
   claiming FST reversibility.

The candidate ordering must be stable across platforms and recorded in the
codec version. A stronger implementation will use stable named variant IDs
derived from FST paths rather than relying permanently on lexical sort order.

## Genuine Realization Ambiguity

The current noun FST maps both surfaces below to the identical analysis:

```text
மரங்களை      -> மரம்+noun+pl+acc
மரங்களினை   -> மரம்+noun+pl+acc
```

Inverse lookup returns both:

```text
மரம்+noun+pl+acc -> மரங்களினை
மரம்+noun+pl+acc -> மரங்களை
```

Lemma and semantic tags alone cannot decide which input spelling occurred.
One form can be the decoder default; the other requires a realization choice.

## Why Past Allomorphs Usually Need No Realization Token

The earlier `past=த்` versus `past=இன்` example illustrates information that
the semantic mapper currently hides, but it is not automatically a surface
ambiguity.

```text
படித்தேன்
  படி+verb+fin+sim+strong+past=த்+1sg=ஏன்

பயன்படுத்தினேன்
  பயன்படுத்து+verb+fin+sim+strong+past=இன்+1sg=ஏன்
```

The lemmas, FST classes and raw analyses differ. Exact inverse lookup produces
one expected surface for each analysis, so no realization selector is needed.

If model tokens retain only `<TENSE_PAST>` and discard both raw analysis and
class information, reconstruction becomes under-specified. The codec should
first recover the allomorph from lemma/class rules or retain a bounded raw
realization feature. `<REALIZATION_n>` is reserved for a remaining choice
between multiple exact surfaces, not emitted for every past-tense word.

## Whitespace and Segmentation

The existing splitter drops whitespace, which prevents full-text round trips.
The reversible segmenter must preserve a sequence of spans covering every
input byte exactly:

```text
Tamil word
other-script word
number/date
punctuation/symbol
whitespace
unknown bytes
```

Whitespace is emitted directly as UTF-8 byte tokens. A space is `<BYTE_20>`, a
newline is `<BYTE_0A>`, and repeated or unusual whitespace remains an exact
ordered byte sequence. No byte-span wrapper is required because byte tokens are
self-identifying and the next `<WORD_START>` synchronizes lexical decoding.

Punctuation is surface realization rather than morphology. Sentence marks are
separate from neighboring lexical words and use the direct byte representation
for exact reconstruction. Structured numeric punctuation and genuine dotted
Tamil abbreviations remain intact. A trailing period alone never promotes a
Tamil word to an abbreviation; the complete boundary and disambiguation rules
are specified in `PUNCTUATION_AND_ABBREVIATION_POLICY.md`.

## Fallback and Residual Codec

Ordinary unknown Tamil words and names use a fixed, corpus-independent alphabet
of 378 Tamil grapheme tokens:

```text
<TAMIL_GRAPHEME_U....>
```

This preserves useful orthographic units and exact reversal at roughly one
token per displayed grapheme. UTF-8 byte tokens remain the final total-coverage
guarantee:

```text
<BYTE_00> ... <BYTE_FF>
```

Grapheme fallback is used for an otherwise unanalyzed Tamil span only when
every grapheme is in the released alphabet. Bytes are used for:

- non-Tamil text not covered by an optional subword layer;
- malformed or non-normalized Unicode in byte-exact mode;
- unsupported Tamil grapheme, joiner, or mixed combining sequences;
- a surface that does not round-trip through its selected analysis;
- the smallest residual needed to correct an FST-generated canonical surface.

The first implementation may encode the full affected span as bytes. A later
version may encode a compact edit script only after it has exhaustive tests.

## Minimal Stream Boundaries

`<WORD_START>` is the only general word-boundary token. It is retained as a
forward synchronization point before a variable-length semantic analysis.
`<WORD_END>` is unnecessary: `<FST_SIGNATURE_END>`, the bounded optional
realization selector, the next byte token, the next `<WORD_START>`, or end of
stream already determines where decoding continues.

Top-level `<BYTE_SPAN_START>` and `<BYTE_SPAN_END>` are also unnecessary.
Contiguous `<BYTE_XX>` tokens decode directly and may merge diagnostic spans
without changing a single output byte. Human-readable span boundaries remain
available in metadata and do not consume model tokens.

## Decode Procedure

1. Parse structural word/span boundaries.
2. Resolve lemma and raw morphological analysis features.
3. Inverse-generate candidates through the pinned FST model.
4. Apply an optional realization selection.
5. Apply residual bytes if present.
6. Concatenate preserved whitespace and non-word spans.
7. Verify exact equality in round-trip tests.

## Flat Token Stream Requirement

The decoder recovers all of the following without consulting the original
surface or diagnostic record:

```text
lemma
originating FST model/class
exact raw analysis tags and tag values
realization variant or byte fallback
span boundaries and whitespace
```

Semantic tokens such as `<TENSE_PAST>` deliberately abstract over raw values
such as `past=த்` and `past=இன்`. The codec recovers the exact suffix from a
checksum-pinned `(model, semantic morphology)` codebook. Variant zero is
implicit; a non-default pattern uses one `<TAG_VARIANT_n>`. Encoding the
complete input surface remains forbidden for successfully analyzed words.

The implemented token-level invariant is:

```text
decode_tokens(encode(text).tokens) == text
```

with no dependency on `surface`, `selected_analysis` or another side record.
`FixedVocabulary` maps string tokens to deterministic IDs, and `decode_ids`
satisfies the equivalent invariant on the regression suite. Its validation
manifest now passes both lexical-integrity and splitter-reachability gates.

The exhaustive codebook contains 1,525 canonical semantic keys and 3,784 exact
raw-tag patterns. Its maximum fan-out is 32, requiring 31 non-default variant
tokens. The weighted raw-tag cost falls from 33.9464 byte tokens to 0.2477 variant
tokens per upper analysis. See `REVERSIBLE_SIGNATURE_AUDIT.md`.

When productive-compound decomposition changes the semantic head, the typed
reverse map recovers the exact raw composite lemma. A bounded
`<COMPOUND_VARIANT_n>` handles the 4,155 colliding chain keys. Raw lemma bytes
remain only as a fallback for analyses outside the reviewed typed map.

## Failure Policy

Encoding must never silently emit a non-reversible semantic sequence. If FST
reconstruction cannot be proved, the encoder must fall back to bytes and mark
the diagnostic record with the reason.

## Required Tests

- Every analyzed fixture round-trips.
- Every ambiguous inverse surface round-trips independently.
- Every Unicode byte sequence accepted by the public API round-trips.
- NFC and decomposed Tamil inputs round-trip in byte-exact mode.
- Whitespace, punctuation, numbers, emoji and code-mixed inputs round-trip.
- Unknown words round-trip through bytes.
- Token IDs remain stable for a released vocabulary.
- Decoder behavior is identical across supported platforms.

## Current Vocabulary Audit

`scripts/build_tokenizer_vocabulary.py` requests the complete Foma upper
language with an explicit path limit; Foma's implicit default of 100 must not
be used. The current exhaustive build reports:

```text
compact symbolic upper analyses: 2,107,907,215
distinct emitted lexical strings:     218,419
fixed lemma tokens:                    139,895
excluded typed composites:             78,538
total vocabulary tokens:               140,922
blocking lemma issues:                       0
splitter-unreachable lemmas:           0
exact signature round-trip failures:   0
```

The builder records every FST SHA-256 and the vocabulary SHA-256, rejects
duplicates, and fails by default when lexical or splitter validation errors
remain. `--allow-validation-errors` exists only for diagnostic audit builds.

The published manifest includes the stricter Tamil combining-mark grammar
check and records a release-ready vocabulary with no blocking lexical issues.

Single-hyphen expressions are valid Tamil spans when every segment is Tamil.
The tokenizer preserves their written surface and FST lemma. It does not create
an unhyphenated alias without independent lexical or corpus evidence.
