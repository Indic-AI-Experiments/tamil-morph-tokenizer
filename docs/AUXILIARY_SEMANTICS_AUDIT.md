# Auxiliary and Compound Semantics Audit

- Productive decompositions: `78,538`
- Distinct typed-chain shapes: `43`
- Representative chain failures: `0`
- Malformed emitted lexical strings: `0`
- Malformed atomic vocabulary lemmas: `0`
- Malformed canonical bases: `0`
- Reviewed auxiliary descriptions: `20/20`
- Release ready: `true`

Every chain representative is checked for runtime recognition, expected typed
semantic tokens, reverse lemma recovery and exact codec round trip. The lexical
auxiliary lemma plus `<LINK_VPART>` or `<LINK_INFINITIVE>` carries the specific
construction; a redundant generic `<AUXILIARY>` token is not required.

## Resolved release blocker

Earlier audits rejected inherited vowel-sign-plus-pulli corruption such as
`உயா்`, `சோ்த்து`, and `நிப்பாட்டு்`. The current audit reports zero malformed
emitted strings, atomic lemmas, or canonical bases. It also requires an exact
key match between the licensed auxiliary lemmas and their reviewed semantic
descriptions; `தீர்` is described as completive or exhaustive.

Machine-readable evidence is under `outputs/auxiliary_semantics_audit/`.
