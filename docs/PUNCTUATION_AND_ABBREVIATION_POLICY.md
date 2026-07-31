# Punctuation and Abbreviation Policy

## Purpose

Punctuation is part of the reversible surface stream, but it is not Tamil
morphology. The tokenizer therefore separates punctuation from neighboring
lexical words and preserves its exact UTF-8 bytes. It does not add semantic
punctuation labels that would duplicate the surface signal.

An abbreviation is different: it is a lexical interpretation. The
`<ABBREVIATION>` token is emitted only when the FST or the conservative dotted
Tamil abbreviation recognizer supports that reading.

## Boundary rules

1. Sentence and clause punctuation is split from adjacent Tamil words. This
   includes `.`, `,`, `?`, `!`, `:`, `;`, brackets, quotation marks, dashes and
   the Unicode ellipsis.
2. Repeated punctuation remains an ordered sequence of exact surface spans.
   For example, `என்ன?!` becomes `என்ன`, `?`, `!`, and `வா...` becomes `வா`,
   `.`, `.`, `.`.
3. Punctuation internal to a recognized structured numeric form stays inside
   that form. Examples include `3.14`, `1,23,456`, dates and numeric ranges.
   A following sentence-final mark is still separate: `3.14.` becomes `3.14`,
   `.`.
4. Tamil hyphenated lexical forms remain one lexical span when both sides are
   Tamil. Other dashes are separate punctuation.
5. Whitespace, punctuation choice, repetition and ordering round-trip exactly
   through the reversible codec.

In the model stream, punctuation and whitespace are direct `<BYTE_XX>` tokens.
They do not require byte-span wrappers. For example, two spaces followed by a
newline are `<BYTE_20> <BYTE_20> <BYTE_0A>`.

## Abbreviation rules

A period after one Tamil lexical word does not make that word an abbreviation.
Thus `பா.` is tokenized as `பா` plus `.`, allowing `பா` to receive its ordinary
lexical analysis.

A dotted Tamil form is treated as a surface abbreviation only when it contains
at least two Tamil segments, such as `மு.க.` or `தி.மு.க.`. A more specific
reviewed lexical or entity analysis may outrank that generic fallback; for
example, `தி.மு.க.` resolves to the known organization `திமுக`. Terminal
punctuation after a dotted form is separate, so `தி.மு.க.,` becomes
`தி.மு.க.` plus `,` before lexical/entity analysis.

Single Tamil letter names such as `பி`, `ஜி`, `டி` and `எஸ்` may still receive
`<ABBREVIATION>` when that is an explicit FST reading. The tokenizer preserves
all valid alternative readings under the canonical `<READINGS>` / `<ALT>`
grammar rather than forcing the abbreviation reading.

## Disambiguation principle

Orthographic shape supplies a candidate boundary, not a general semantic
claim. The policy intentionally avoids interpreting every word before a period
as an abbreviation. It also avoids stripping punctuation before morphology,
which would lose exact reconstruction. Lexical analysis and reversible surface
encoding remain separate responsibilities.

## Regression coverage

The automated suite covers:

- a lexical word followed by a period, including the informal vocative `பா.`;
- genuine two- and three-segment Tamil abbreviations;
- punctuation immediately following an abbreviation;
- sentence punctuation, quotes, brackets, dashes and repeated marks;
- decimals and grouped numbers;
- exact token-stream round trips including whitespace and newlines.

These boundary tests run alongside the exhaustive canonical ambiguity audit,
so a punctuation correction cannot silently weaken ambiguity preservation or
exact reconstruction.
