# Semantic Tokens

This project exposes readable semantic tokens on top of the copied Tamil FST analyses. The FSTs produce raw tags such as `noun`, `pl`, `acc`, `loc`, `past=த்`, and `3sgm=ஆன்`. The tokenizer maps those tags to article-friendly tokens such as `<POS_NOUN>`, `<NUM_PL>`, `<CASE_ACC>`, and `<TENSE_PAST>`.

Most morphology tokens are FST-derived. The exact token strings are defined by this demo project in `tamil_morph_tokenizer/analysis.py`. A small number of tokens are manually curated lexical specials in `tamil_morph_tokenizer/tokenizer.py`, and a few are structural tokens used by ambiguity-preserving modes.

For the exhaustive release inventory—including every fixed token ID, Tamil
lexical factor, inherited FST label, source category and plain-English
description—see
[`SEMANTIC_TOKEN_VOCABULARY.md`](SEMANTIC_TOKEN_VOCABULARY.md). Its
machine-readable counterpart is
`tamil_morph_tokenizer/data/vocabulary/semantic_token_reference.json`.

## Sources

| Token source | Description |
| --- | --- |
| FST-derived mapped tokens | Raw FST tags mapped through `TAG_TOKEN_MAP`. |
| FST-derived generated tokens | Raw FST tags must be explicitly mapped for a frozen release; unexpected tags fail vocabulary validation. |
| Ambiguity structure | Fixed `<READINGS>` and `<ALT>` markers preserve complete alternative readings. |
| Structural tokens | Word, signature, realization, Tamil-grapheme fallback, and byte-escape boundaries used by the reversible codec. |
| Lexical special tokens | Hand-authored tokens for common postpositions/modals such as `க்குள்` and `வேண்டும்`. |

## Part-of-Speech Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<POS_NOUN>` | `noun` | Noun | `மரம்` in `மரங்களை` |
| `<POS_VERB>` | `verb` | Raw-analysis verb label; derivable and omitted from canonical public verb sequences | Exact FST signature only |
| `<POS_ADJ>` | `adj` | Adjective | Modifier/adjectival forms |
| `<COMPOUND_MODIFIER>` | `compoundmodifier` | Attributive/compound use of a lexical noun | `உலக` from `உலகம்` before a compound head |
| `<POS_ADV>` | `adv`, `adverb` | Adverb | `ஏன்` |
| `<POS_PART>` | `part`, `particle` | Generic particle/function word | Fallback for broad particle tags |
| `<POSTPOSITION>` | `pp-particle` | Postposition / postpositional particle | `வரை`, `முன்`, `மட்டும்` |
| `<POS_PRONOUN>` | `pron`, `pronoun` | Pronoun | `தங்கள்`, `என்ன` |
| `<POS_QUANTIFIER>` | `quant` | Quantifier | `எல்லா`, `எத்தனை` |

## Function-Word Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<COMPLEMENTIZER>` | `comp` | Complementizer / quotative function | `என`, `என்று`, `என்பதை` |
| `<COPULA>` | `cop`, `copula` | Copular or negative copular function word | `இல்லை` |
| `<ENTITY_PERSON>` ... `<ENTITY_OTHER>` | `entity_person` ... `entity_other` | Most-specific reviewed entity category; no redundant proper-noun token | `இந்தியா`, `தமிழ்நாடு`, `சென்னை`, `ஐக்கிய நாடுகள்` |
| `<MORPH_CONJUNCTION>` | `conjunction`, `conjuction` | Conjunction | `எனவே` |
| `<ABBREVIATION>` | `abbrev` | Abbreviation marker | `பி`, `ஜி`, `டி`, `எஸ்` |
| `<LETTER_NAME>` | `letter` | Letter-name abbreviation | `பி`, `ஜி`, `டி`, `எஸ்` |
| `<COMPARATIVE>` | `comparative` | Comparative relation: than / more-or-less comparison | `க்கும்` in `15 க்கும் குறைவாக` |

## Deictic Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<DEICTIC>` | `dem`, `demonstrative` | Deictic/demonstrative marker | `இந்த`, `இப்பொழுது` |
| `<DEICTIC_PROX>` | `prox`, `demonstrativeProx` | Proximal: this / here / now-near | `இந்த`, `இப்பொழுது` |
| `<DEICTIC_DIST>` | `dist`, `demonstrativeDist` | Distal: that / then-there | `அந்த`, `அப்பொழுது` |
| `<DEICTIC_MED>` | `med`, `demonstrativeMed` | Medial/intermediate demonstrative | `உந்த` |
| `<DEICTIC_INTERROGATIVE>` | `inter` | Interrogative deictic: which / when | `எந்த`, `எப்பொழுது` |
| `<DEICTIC_TIME>` | `time` | Deictic time expression | `இப்பொழுது`, `எப்போது`, `இம்மாசம்` |
| `<DEICTIC_TYPE>` | `type` | Deictic kind/type modifier | `இவ்வகை`, `எவ்வகை` |
| `<DEICTIC_SITUATION>` | `situation` | Deictic situation/context expression | `இந்நிலையில்` |
| `<DEICTIC_SAME>` | `same` | Same/identical deictic relation | `அதே` |
| `<DISTRIBUTIVE>` | `distrib` | Distributive: each/respective | `அந்தந்த` |
| `<DEGREE>` | `degree` | Degree/amount expression | `இவ்வளவு`, `அவ்வளவு` |

## Quantifier And Pronoun Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<QUANT_ALL>` | `all` | Universal/all quantification | `எல்லா`, `அனைவரும்` |
| `<INDEFINITE>` | `indef` | Indefinite quantification: any/some | `ஏதேனும்` |
| `<SEM_HUMAN>` | `human` | Human/person reference | `ஒருவர்`, `அனைவரும்` |
| `<PRON_POSSESSIVE>` | `poss` | Possessive/honorific pronoun function | `தங்கள்` |
| `<DETERMINER>` | `det` | Determiner/modifier function | `எல்லா` |

## Modal And Existential Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<MODAL>` | `modal` | Modal expression | `வேண்டாம்` |
| `<EXISTENTIAL>` | `exist` | Existential function | `உண்டா` |
| `<POLARITY_POS>` | `pos` | Positive existential polarity | `பயனுள்ள`, `இடமுண்டு` |
| `<MOOD_QUESTION>` | `ques` | Interrogative/question mood | `உண்டா` |
| `<MOOD_PROHIBITIVE>` | `prohib` | Prohibitive/negative imperative mood | `வேண்டாம்` |

## Number Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<NUM_SG>` | `sg` | Singular number | One item/person |
| `<NUM_PL>` | `pl` | Plural number | `மரங்களை` = trees |

## Clitic Tokens

| Token | FST tag | Linguistic function | Rough English gloss | Example |
| --- | --- | --- | --- | --- |
| `<CLITIC_ADD>` | `add` | Additive/enclitic `உம்`, including noun additive and function-particle uses | also / too / and | `மரங்களும்` = trees also / trees too; `க்கும்` in comparative use |
| `<CLITIC_FOCUS>` | `foc` | Focus/emphatic clitic, often corresponding to `தான்` | precisely / indeed / it is ... that | `அதனால்தான்` = for that reason indeed |
| `<SANDHI_K>` | `sandhik` | Sandhi/linking `க்` marker | k-linking | `எனக்` |
| `<SANDHI_C>` | `sandhic` | Sandhi/linking `ச்` marker | c-linking | case/infinitive-linked forms |
| `<SANDHI_P>` | `sandhip` | Sandhi/linking `ப்` marker | p-linking | case/infinitive-linked forms |
| `<SANDHI_T>` | `sandhit` | Sandhi/linking `த்` marker | t-linking | case/infinitive-linked forms |

## Case Tokens

| Token | FST tag | Linguistic function | Rough English gloss | Example |
| --- | --- | --- | --- | --- |
| `<CASE_NOM>` | `nom` | Nominative/base subject case | subject/base form | `மின்` |
| `<CASE_ACC>` | `acc` | Accusative case | direct object | `மாணவனை`, `மரங்களை` |
| `<CASE_DAT>` | `dat` | Dative case | to / for | `அவனுக்கு` |
| `<CASE_GEN>` | `gen` | Genitive case | of / possessive | `அவனுடைய` |
| `<CASE_INST>` | `inst` | Instrumental case | by / with / using | tool or means readings |
| `<CASE_TRANS>` | `trans` | Translative/adverbial case-like form | as / becoming / in the manner of | `காரணமாக` = as a reason / because of |
| `<CASE_LOC>` | `loc` | Locative case | in / at / on | `காட்டில்` = in the forest |
| `<CASE_ABL>` | `abl` | Ablative case | from / out of / away from | `மரங்களிலிருந்து` = from the trees |
| `<CASE_SOC>` | `soc` | Sociative case | with / together with | companionship/association readings |
| `<CASE_VOC>` | `voc` | Vocative case | direct address | calling/addressing someone |

## Verb Form Tokens

Canonical public verb output omits broad labels whose value is already
recoverable from the FST model and specific morphology: `<POS_VERB>`,
`<VERB_FINITE>`, `<VERB_NONFINITE>`, `<VERB_SIMPLE>`, `<VERB_STRONG>`,
`<VERB_WEAK>`, `<VERB_MIDDLE>`, `<VERB_COMPLEX>`, and generic `<ASPECT>` or
`<MOOD>`. They remain mapped for raw-analysis inspection and exact signature
recovery. Specific aspect, voice, tense, agreement, infinitive, participle,
polarity and nominalization tokens remain public.

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<VERB_FINITE>` | `fin` | Derivable raw finite label; not publicly emitted | Exact FST signature only |
| `<VERB_NONFINITE>` | `nonfin` | Derivable raw nonfinite label; not publicly emitted | Exact FST signature only |
| `<VERB_SIMPLE>` | `sim` | Derivable raw simple-class label; not publicly emitted | Exact FST signature only |
| `<VERB_STRONG>` | `strong` | Raw strength/class label; not publicly emitted | Exact FST signature only |
| `<VERB_WEAK>` | `weak` | Raw strength/class label; not publicly emitted | Exact FST signature only |
| `<VERB_MIDDLE>` | `middle` | Raw strength/class label; not publicly emitted | Exact FST signature only |
| `<VERB_COMPLEX>` | `complex` | Derivable raw complex label; typed links express structure publicly | Exact FST signature only |
| `<ASPECT>` | `aspect` | Generic raw aspect label; not publicly emitted | Exact FST signature only |
| `<ASPECT_PERFECT>` | `perfect` | Perfect/resultative aspect | `வந்துள்ளது`, `தெரிவித்துள்ளார்` |
| `<VOICE_PASSIVE>` | `passive` | Passive voice / undergoer-oriented complex verb | `பயன்படுத்தப்படுகிறது` |
| `<VERB_INFINITIVE>` | `inf` | Infinitive | `செலுத்த` |
| `<VERB_IMPERATIVE>` | `imp` | Imperative | Command form |
| `<POS_VERBAL_NOUN>` | `verbalnoun` | Verbal noun / gerund-like event nominal; replaces ordinary `<POS_VERB>` for this reading | `செயல்படுவது`, `தாக்கல்` |
| `<ACTION_NOMINAL>` | derived from `verbalnoun` | Event/action nominal semantics | `வழிபடுவதும்`, `வழங்கல்` |
| `<ADJECTIVAL_PARTICIPLE>` | `adjpart` | Adjectival/relative participle marker | `பேசிய`, `வருகின்ற` |
| `<VERBAL_PARTICIPLE>` | `vpart` | Verbal participle marker | `விமர்சித்து` |
| `<FUTURE_ADJECTIVAL_PARTICIPLE>` | `futANDadjpart` | Future/adjectival participle marker | Future relative participle readings |
| `<MANNER_PURPOSE>` | `vpart_maaru` | Directed manner or intended-outcome connector in `-உமாறு` | `செய்யுமாறு`, `வருமாறு` |
| `<NEGATIVE_PARTICIPLE>` | `negpart` | Negative participial marker | Negative non-finite forms |
| `<MOOD_PARTICLE>` | `moodpart` | Mood particle marker | Modal/mood non-finite forms |
| `<LINK_VPART>` | decomposition map | Internal verbal-participle link to the next predicate | `படித்துக்கொடு` |
| `<LINK_INFINITIVE>` | decomposition map | Internal infinitive link to the next predicate | `படிக்கமுடி` |

Literal raw tags such as `aux=விடு` emit `<LINK_VPART> விடு`, preserving both
the connector and the auxiliary lemma. The former generic `<AUXILIARY>` token
is not emitted because it would be redundant and less informative.
`<AUX_ATTITUDINAL>` and `<AUX_NONATTITUDINAL>` remain broad inherited FST
construction labels pending a separate semantic subclass audit; they do not
encode the internal nonfinite link.

## Productive Compound Decomposition

The patched FSTs emit many productive compound lexical strings as one lemma,
for example `படித்துக்கொடு`, `செய்துவிடு`, and `படிக்கப்படமுடி`. The tokenizer
uses a source-subclass-backed decomposition map for all 78,538 FST-only compounds:

```text
படித்துக்கொடு   -> படி <LINK_VPART> கொடு
செய்துவிடு      -> செய் <LINK_VPART> விடு
படிக்கப்படமுடி -> படி <VOICE_PASSIVE> <LINK_INFINITIVE> முடி
```

The map is not a suffix heuristic. Each entry belongs to a productive FST
subclass, and its connector surface was independently analyzed back to a base
verb. Source-attested productive strings remain atomic. The release has no
unresolved connector or adjectival-participle FST-only compounds.

Productive `படு` is represented by `<VOICE_PASSIVE>` rather than a redundant
generic auxiliary marker plus lemma. Sandhi remains realization information;
it is not encoded as a semantic link type.

## Tense and Polarity Tokens

| Token | FST tag | Linguistic function | Example |
| --- | --- | --- | --- |
| `<TENSE_PAST>` | `past` | Past tense | `படித்தான்` |
| `<TENSE_PRESENT>` | `pres` | Present tense | Present-marked verbs |
| `<TENSE_FUTURE>` | `fut` | Future tense | `வேண்டும்` FST readings |
| `<POLARITY_NEG>` | `neg` | Negative polarity | Negative verb forms |

## Person Tokens

| Token | FST tag | Linguistic function | Rough meaning |
| --- | --- | --- | --- |
| `<PERSON_1SG>` | `1sg` | First person singular | I |
| `<PERSON_2SG>` | `2sg` | Second person singular | you |
| `<PERSON_2SG_HON>` | `2sgh` | Second person singular honorific | respectful you |
| `<PERSON_3SG_MASC>` | `3sgm` | Third person singular masculine | he |
| `<PERSON_3SG_FEM>` | `3sgf` | Third person singular feminine | she |
| `<PERSON_3SG_EPICENE>` | `3sge` | Third person singular common/epicene | he/she/common |
| `<PERSON_3SG_HON>` | `3sghe` | Third person singular honorific | respected person |
| `<PERSON_3SG_NEUT>` | `3sgn` | Third person singular neuter | it |
| `<PERSON_1PL>` | `1pl` | First person plural | we |
| `<PERSON_2PL>` | `2pl` | Second person plural/honorific | you plural/respectful |
| `<PERSON_3PL>` | `3pl` | Third person plural | they |
| `<PERSON_3PL_HON>` | `3plh` | Third person plural/honorific | respected they |
| `<PERSON_3PL_EPICENE>` | `3ple` | Third person plural epicene/common | they/common |
| `<PERSON_3PL_NEUT>` | `3pln` | Third person plural neuter | they, non-human/neuter |

## Generated Unmapped Morphology Tokens

When the FST emits a tag that is not in `TAG_TOKEN_MAP`, the tokenizer generates a readable fallback token:

```text
raw tag -> <MORPH_RAWTAG>
```

The raw tag is uppercased and hyphens are converted to underscores. Realization material after `=` is removed before token creation, so `past=த்` maps through the normalized tag `past`.

Examples observed in current tokenizer output:

| Token | FST tag | Linguistic function |
| --- | --- | --- |
| `<STEM_OBLIQUE>` | `infInc` | Oblique noun stem used before case material |

This category is open-ended. Any future FST tag not explicitly mapped will produce a corresponding `<MORPH_...>` token.

## Canonical Ambiguity Structure

`compact_ambiguity` is the default tokenizer mode. It preserves the surface in
the structured record, not in the model token list. It emits shared lemma and
the longest shared semantic prefix once and preserves each residual reading as
a separate `<ALT>` group.

Example:

```text
காட்டில்
analyses:
  காடு+noun+loc
  காடு+noun+abl

tokens:
  காடு <POS_NOUN> <READINGS> <CASE_LOC> <ALT> <CASE_ABL>
```

The grammar uses only two fixed tokens:

| Token | Meaning |
| --- | --- |
| `<READINGS>` | Starts the residual readings after the factored common prefix |
| `<ALT>` | Separates one complete residual reading from the next |

Example with locative/sociative ambiguity:

```text
புத்தகத்தில்
analyses:
  புத்தகம்+noun+infInc+loc
  புத்தகம்+noun+infInc+soc

tokens:
  புத்தகம் <POS_NOUN> <STEM_OBLIQUE>
  <READINGS> <CASE_LOC> <ALT> <CASE_SOC>
```

When analyses have different lemmas, there is no shared lemma prefix:

```text
<READINGS>
எத்தனை <POS_QUANTIFIER> <DEICTIC_INTERROGATIVE>
<ALT>
எத்தன் <POS_NOUN> <CASE_ACC>
```

The best reading is first. `decode_readings()` reconstructs every complete
semantic sequence, proving that alternatives do not collapse into an invalid
cross-product. The previous candidate-token and per-analysis-boundary families
are not present in the fixed vocabulary.

## Lexical Special Tokens

These tokens are not raw FST outputs. They are a small hand-authored semantic layer in `SPECIAL_TOKENS`, used before grapheme fallback or as metadata supplements.

| Surface | Token | Function | Handling |
| --- | --- | --- | --- |
| `க்குள்` | `<POST_WITHIN_BY>` | Postposition meaning within / by a deadline | Emits token with `fallback="special"` when there is no FST analysis |
| `வரை` | `<POST_UNTIL>` | Postposition meaning until / up to | Emits token with `fallback="special"` when there is no FST analysis |
| `முன்` | `<POST_BEFORE>` | Postposition/adverbial meaning before | Emits token with `fallback="special"` when there is no FST analysis |
| `பின்` | `<POST_AFTER>` | Postposition/adverbial meaning after | Emits token with `fallback="special"` when there is no FST analysis |
| `வேண்டும்` | `<MODAL_MUST>` | Modal meaning must / should / need to | Preserves FST analysis and exposes this as `semantic_special` |
| `மட்டும்` | `<PART_ONLY>` | Focus/restrictive particle meaning only / just | Preserves FST analysis and exposes this as `semantic_special` |

Special tokens do not silently replace recognized FST analyses. If a special item has an FST analysis, the FST-derived tokens remain in `tokens`, while the special meaning is exposed through:

```text
semantic_special
special_handling
```

For example, `வேண்டும்` keeps its FST analyses, emits `<MODAL_MUST>` as an additional token, and adds:

```text
semantic_special = <MODAL_MUST>
special_handling = supplement
```

For `க்குள்`, when no FST analysis is available:

```text
tokens = <POST_WITHIN_BY>
fallback = special
semantic_special = <POST_WITHIN_BY>
special_handling = fallback_override
```

## Mode Summary

| Mode | Default? | Behavior |
| --- | --- | --- |
| `compact_ambiguity` | Yes | Surface stays in record metadata; tokens contain shared lemma/tags and fixed ambiguity structure |
| `best` | No | Chooses one best analysis and emits lemma plus morphology tokens; useful for token-count comparisons |
| `all_analyses` | No | Preserves complete readings with `<READINGS>/<ALT>` but does not factor their common prefix |

## Caveats

- The linguistic categories come from FST tags, but the angle-bracket token strings are project-defined labels.
- Generated `<MORPH_...>` tokens are not curated linguistic labels; they are readable fallbacks for unmapped FST tags.
- Ambiguity markers are tokenizer structure, not FST morphology labels.
- Lexical special tokens are manually curated and intentionally small.
- This is a demo tokenizer for an LLM tokenization article, not a complete Tamil grammar ontology.
