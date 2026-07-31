# Colloquial and Participial Release 0352-0357

> Historical milestone record. Counts below describe releases 0352-0357 and
> are not current-release statistics; use `release/*.json` and
> `outputs/fst_system_audit/stats.json` for current values.

## Scope

This release closes a connected set of modern spoken-Tamil, participial-noun,
punctuation, and ambiguity defects reported through tokenizer testing. The
changes are class-level continuations or reviewed closed-class relations; no
tokenizer-only inflected-form exceptions were added.

## Morphology Changes

- C11 negative imperatives now realize `-க்காதே/-க்காதீர்கள்`, including
  `சோதிக்காதே` from `சோதி`.
- All verb models expose masculine and feminine singular human participial
  nouns, including `போனவன்`, `சென்றவன்`, and their case paradigms.
- C5 spoken presents retain final `உ` across the agreement matrix, including
  `பண்ணுறேன்`, `பண்ணுறார்`, `பண்ணுறீங்களா`, and `பண்ணுறாங்களா`.
- I-final C11 verbs receive the reviewed spoken `-ச்ச்-` past family, including
  `படிச்சு` and `படிச்சியா`.
- `பாரு` is an explicit colloquial second-person imperative of `பார்`.
- `செய் -> செஞ்ச்` preserves the conditional, past feminine, and
  agreement-neutral question readings of `செஞ்சா`; `செஞ்சு` and `செஞ்சால்`
  retain their verbal readings alongside valid lexical homographs.
- Spoken predicates ending in `-ங்க` insert `ள` before the polar question
  clitic, producing `பார்த்தீங்களா` and `வந்தாங்களா` rather than `-ங்கா`.
- Productive `விடு` auxiliary chains add the spoken contraction used by
  `விட்டுடு`, `சொல்லிடு`, `செய்துடு`, and their finite continuations.
- The finalized generator applies the imperative contraction systematically to
  standard `-இ/-உ/-ய்` participles and to the narrow colloquial-participle lane,
  covering forms such as `பார்த்துடு`, `வந்துடு`, `போயிடு`, and `படிச்சுடு`
  without admitting colloquial participles into every auxiliary continuation.
- `ரொம்ப` has an explicit intensifier/adverb reading. `பா` has an explicit
  colloquial interjection/vocative reading.

## Tokenizer Changes

- A single Tamil lexical word followed by `.` is split from punctuation;
  dotted abbreviations require at least two dotted initials.
- `compact_ambiguity` orders the selected analysis first.
- All distinct alternatives use the canonical factored grammar:
  `common <READINGS> residual <ALT> residual`. Semantic labels remain attached
  to a complete reading without parallel candidate labels or paired boundaries.
- Reviewed intensifier, vocative, and colloquial verbal readings outrank
  generic or rare homographs without deleting valid ambiguity.

## Reversible Release Gates

- compiled FST models: 12
- symbolic upper analyses used by the signature audit: 318,506,791
- semantic signature keys: 25,558
- exact raw-tag patterns: 43,420
- exhaustive witness analyses: 425,877,608
- exact inverse-forward round-trip failures: 0
- fixed vocabulary lemmas: 139,514
- fixed vocabulary tokens after the canonical ambiguity refinement and before
  the later minimal-boundary rc5 cleanup: 140,056

The fixed lexical inventory is unchanged because the corrected roots and
semantic labels already existed. The later ambiguity refinement removes 207
candidate labels and obsolete analysis boundaries; its vocabulary manifest is
therefore released separately from this morphology batch.
