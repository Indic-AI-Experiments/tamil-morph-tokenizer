# Proper-Noun and Entity Policy

## Purpose

Proper names are an open vocabulary. Treating every person, place, company,
brand, title, transliteration, and spelling variant as an ordinary noun root
would make the FST lexicon unbounded, inflate the LLM vocabulary, and create
false analyses. Conversely, leaving every inflected name opaque loses useful
case and number information.

The tokenizer therefore separates **entity identity** from **entity
morphology**. Core lexical FST coverage and entity-aware coverage are reported
as different metrics.

## Representation

The semantic token stream should contain the Tamil entity lemma, one most
specific entity token, and any genuine morphology:

```text
சென்னையில்  -> சென்னை <ENTITY_CITY> <CASE_LOC>
இந்தியாவுக்கு -> இந்தியா <ENTITY_COUNTRY> <CASE_DAT>
ராமனின்     -> ராமன் <ENTITY_PERSON> <CASE_GEN>
```

`<POS_PROPN>` is not emitted when a specific `<ENTITY_*>` token is present;
that would be redundant. The fixed-ID codec represents an out-of-vocabulary
entity lemma with its existing reversible byte tokens. Entity identity is
therefore lossless without putting every name in the fixed vocabulary.

Recommended mutually exclusive entity tokens are:

- `<ENTITY_PERSON>`
- `<ENTITY_COUNTRY>`
- `<ENTITY_CITY>`
- `<ENTITY_REGION>`
- `<ENTITY_PLACE>`
- `<ENTITY_ORG>`
- `<ENTITY_BRAND>`
- `<ENTITY_WORK>` for named books, films, songs, and similar works
- `<ENTITY_OTHER>` only for confirmed entities outside these categories

An external knowledge-base identifier may be returned as annotation metadata,
but must not replace the Tamil lemma or participate in reversible decoding.

## Resource Architecture

Entity entries belong in a separate, versioned gazetteer, not ordinary noun
LexC roots. Each entry should record:

- Tamil lemma and attested Tamil aliases;
- one entity category;
- declension/phonological template when inflection is licensed;
- evidence source, license, and source revision;
- reviewed versus automatically imported status;
- optional stable external entity identifier.

The morphology repository may compile this as an optional `proper-noun.fst`.
The tokenizer may load it after the core lexical FSTs, while keeping entity
coverage separate from the ordinary lexical morphology inventory.

Multiword organizations, companies, institutions, and work titles require a
phrase-level entity matcher. Morphology normally attaches to the final word or
to the whole recognized span; individual component words must not be inserted
as company-name noun roots merely because they occur inside an entity.

## Admission Rules

An item may enter the entity gazetteer when at least one of these holds:

1. It is present in a curated geographic, person, organization, or brand
   resource with an acceptable license and stable identifier.
2. It has an explicit `name`/proper-noun classification in a reviewed lexical
   source and its entity type can be established.
3. Corpus context provides high-confidence repeated entity evidence and a
   reviewer confirms the lemma, category, and inflection template.

Tamil Grantha letters (`ஜ`, `ஷ`, `ஸ`, `ஹ`, `க்ஷ`) are evidence of borrowing
or transliteration, **not evidence of entity status**. Capitalization is not
available in Tamil and cannot be used. Frequency alone is also insufficient.

For an unseen name, the tokenizer may apply a conservative suffix analysis
only when a contextual NER model or phrase matcher independently establishes
the entity span. Otherwise it must retain reversible unknown-surface fallback.

## Category Rules

### People

Store the full attested name and useful aliases. Do not automatically add every
given-name or surname component as an independent entity. Titles and honorifics
such as `திரு`, `டாக்டர்`, and occupational descriptions remain separate
closed-class or common lexical tokens. Honorific and plural-looking endings
must not be interpreted as grammatical number without evidence.

### Countries, cities, regions, and places

Curated geographic names are suitable for entity morphology because their
inventory is relatively stable and case marking is frequent. Demonyms,
language names, and relational adjectives are separate lexical readings:
`இந்தியா` is an entity, while `இந்தியர்` and `இந்திய` require their own noun or
adjective analyses.

### Organizations and companies

Prefer longest-span phrase matching. Legal suffixes and generic heads such as
`நிறுவனம்`, `பல்கலைக்கழகம்`, and `வங்கி` retain their ordinary lexical
analyses. A company name does not authorize those component surfaces as new
entity lemmas.

### Brands and products

Keep brands out of the common noun FST until independent evidence shows
lexicalization as a generic Tamil noun. Preserve spelling variants rather than
silently canonicalizing them; optional entity linking can associate variants.

### Ambiguous names

When a surface is both a common word and a name, preserve both analyses.
Contextual ranking may prefer the entity reading, but the entity gazetteer must
not delete a valid common-noun, adjective, verb, or closed-class reading.

## Coverage Metrics

Report at least three separate rates:

1. **Core morphology coverage:** analyses from ordinary lexical FSTs only.
2. **Entity-aware coverage:** additional analyses from the proper-name FST and
   phrase entity matcher.
3. **Unknown fallback:** surfaces handled losslessly without a linguistic
   analysis.

Translation experiments must freeze entity resources together with the
tokenizer. Evaluation entities must not be imported after inspecting the test
set; otherwise tokenizer coverage and translation results are contaminated.

## Current Corpus Policy

The current Mozhi bucket formerly called `loan_or_foreign_name` is only a
foreign-phoneme/transliteration heuristic. It includes ordinary borrowed words
and must not be counted as confirmed entities. Until a gazetteer audit exists,
these rows remain `foreign_phoneme_or_entity_candidate` and are excluded from
automatic noun-root patches.

## Implemented Runtime And Geography Release

`tamil_morph_tokenizer.entity` provides a validated JSONL gazetteer,
review-state and provenance enforcement, alias lookup, and an
`EntityAnalyzer` implementing the same batch interface as an FST analyzer.
Only `reviewed` entries are exposed at runtime. An alias remains its own Tamil
lexical lemma instead of being silently replaced by a canonical spelling; the
stable entity identifier remains metadata. Candidate and rejected rows fail
closed. When a reviewed entity is also an ordinary lexical word, both analyses
are preserved, and context-neutral ranking prefers the common-word reading for
collision-prone person, city, brand, work, and generic-place categories.

The production geography artifact contains 3,626 source-validated entries:
203 countries, 3,298 cities, 122 regions, two CLDR organizations, and one
world/place entry. It is generated reproducibly from Unicode CLDR 48.1 and
CC0 Wikidata query snapshots. Seventy-two reviewed major/local city forms are
active; 3,226 city entries remain candidates because context-free activation
of every city produced false readings such as ordinary `மொபைல்` and `மசாலா`.
The generator rejects 116 mixed-script or punctuation-bearing source labels
instead of silently normalizing them.

The entity morphology layer covers nominative, accusative, dative, genitive,
instrumental, locative, ablative, and sociative forms through declared
declension templates. Separate templates cover வ்/ய் vowel joins, `ம் -> த்த்`,
short-`உ` deletion, `டு -> ட்ட்`, `று -> ற்ற்`, selected stop gemination, and
ordinary pulli-final attachment. Ambiguous `-உ` names remain indeclinable until
an override supplies evidence. Phrase matching uses deterministic longest-span
selection and applies case morphology to the final component.

`StructuredReversibleCodec` represents an out-of-vocabulary entity lemma with
the fixed UTF-8 byte alphabet between lexical boundaries, followed by the same
entity and case tokens. The entity model marker plus the checksum-pinned
gazetteer reconstruct the surface without `<SURFACE_BYTES>` duplication.
The 32-case gold fixture covers all cases, multiword entities, spelling aliases,
declension subclasses, exact reversal, candidate suppression, and a reviewed
surface collision exclusion.

The schema is `configs/entity_gazetteer.schema.json`; source queries, revisions,
licenses, and checksums are documented under `resources/entity_sources/`.
Person, brand, work, and general organization coverage still requires licensed
typed resources or contextual NER. Grantha spelling and corpus frequency alone
remain insufficient evidence.
