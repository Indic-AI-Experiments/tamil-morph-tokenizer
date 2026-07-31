# Canonical Ambiguity Encoding

## Objective

Preserve every distinct FST semantic reading in one bounded model-token stream
without duplicating surfaces, losing feature co-occurrence, or maintaining a
parallel candidate-token ontology.

## Grammar

An unambiguous word emits its ordinary semantic sequence:

```text
lemma semantic-token ...
```

An ambiguous word emits:

```text
common-prefix <READINGS> best-residual <ALT> residual ...
```

The token tuple boundary terminates the list in `TamilMorphTokenizer`. In the
reversible codec, `<FST_SIGNATURE_START>` terminates it after the surrounding
`<WORD_START>` marker. An ambiguity-end token would therefore be
redundant.

## Factoring

The encoder computes the longest token prefix shared by every distinct
semantic reading. Only that order-preserving prefix is factored. Factoring an
unordered intersection could change compound-link order or create a sequence
that no analysis emitted.

For the locative/ablative ambiguity of `இந்தியாவில்`:

```text
இந்தியா <POS_NOUN> <READINGS> <CASE_LOC> <ALT> <CASE_ABL>
```

`decode_readings()` expands it to:

```text
இந்தியா <POS_NOUN> <CASE_LOC>
இந்தியா <POS_NOUN> <CASE_ABL>
```

For different lemmas, the common prefix can be empty:

```text
<READINGS>
எத்தனை <POS_QUANTIFIER> <DEICTIC_INTERROGATIVE>
<ALT>
எத்தன் <POS_NOUN> <CASE_ACC>
```

## Canonical Ordering

1. Rank all valid analyses with the normal context-free ranking policy.
2. Emit the selected best semantic reading first.
3. Sort remaining readings by their complete lexical/semantic token tuple,
   then model name and raw analysis as deterministic tie breakers.
4. Collapse analyses that have identical model-facing semantic sequences.
5. Retain every raw analysis in record metadata even when its semantic sequence
   is identical to another analysis.

This makes model tokens independent of FST process return order.

## Reversibility

The reversible stream contains all distinct semantic readings. The first
reading supplies the exact FST model signature, raw-tag variant, and surface
realization selector. Decoding expands the ambiguity grammar, selects the first
reading, and reconstructs the surface using only the flat token stream. No
surface metadata is consulted.

Unknown material continues to use bounded UTF-8 byte tokens. Ambiguity does not
change the unknown-text contract.

## Removed Redundancy

The fixed vocabulary no longer contains:

- 207 generated candidate-label entries such as `<CASE_CAND_LOC>` and
  `<CAND_TENSE_PAST>`;
- `<ANALYSIS_START>` and `<ANALYSIS_END>` around every alternative;
- `<LEMMA_CAND>` or dynamic `<LEMMA_CAND:...>` strings.

It adds only `<READINGS>` and `<ALT>`. The current vocabulary contains 140,922
tokens, including 139,895 lemma tokens and a 284-entry model-factor region
containing 222 grammatical or semantic labels plus 62 secondary lexical
components. The earlier 140,263-to-140,053 reduction belongs to the
ambiguity-encoding milestone, not the current lexical release.

## Validation Invariants

- `decode_readings(encode_readings(readings))` reproduces every complete
  semantic reading.
- Candidate and per-analysis boundary tokens are absent from the vocabulary.
- Ambiguous live FST words expose `<READINGS>` and `<ALT>` in both diagnostic
  tokenizer output and the reversible model stream.
- Exact token and token-ID decoding reconstruct the original input.
- The exhaustive raw-tag signature round-trip gate remains independent and
  must continue to report zero failures.

The release audit in `outputs/canonical_ambiguity_audit/summary.json` checks
all 3,486 distinct runtime ambiguity surfaces. It observes 3,224 grouped
semantic ambiguities, 48,465 model tokens, exact flat-token and token-ID round
trips, zero obsolete tokens, and zero failures.

That audit also guards two inverse-decoder interactions that unit examples did
not originally expose: the selected reading of an ambiguous decomposed
compound must drive compound reconstruction, and an FST-emitted postposition
token such as `<POST_WITHIN_BY>` must not be discarded merely because the same
label can also be a lexical refinement for a standalone word.
