# Third-Party Data and License Matrix

Status date: 2026-07-23

This document is an engineering release inventory, not legal advice. It records
the upstream terms we can verify, the project artifacts affected by each input,
and the actions required before public distribution.

## Release Decision Summary

| Component | Verified terms | Current decision |
| --- | --- | --- |
| ThamizhiMorph source, lexicons, rules, and models | Apache License 2.0 | Redistributable with the Apache license, preserved notices, attribution, and prominent modification notices. |
| Tamil Lexicon database published by UChicago DSAL | CC BY-NC-ND 2.0 Generic is linked from the dictionary page; separately, the project owner confirms authorization to use the supplied data freely and distribute derivative works freely | Cleared for the intended derivative runtime distribution. Original and processed Lexicon word lists remain excluded. The combined lexical/data layer of the FSTs and tokenizer vocabulary uses CC BY-SA 4.0 because it also incorporates Wiktionary-derived material. |
| Tamil Wiktionary dumps | Dual licensed: CC BY-SA 4.0 or GFDL, subject to source-page terms | Redistributable with attribution, license notice, source/revision information, and share-alike handling. |
| Vuizur Tamil-English Wiktionary TSV | Dual licensed: CC BY-SA 3.0 Unported or GFDL | Redistributable under the repository's stated dual license with attribution and license notices. |
| Unicode CLDR data | Unicode License v3 | Redistributable when the Unicode copyright and permission notice accompanies the data or documentation. |
| Wikidata structured entity data | CC0 1.0 | Redistributable; retain provenance and a CC0 notice as good practice. |
| Original tokenizer code and project documentation | Apache-2.0 for software; CC BY 4.0 for documentation, article material, figures, and independently created non-software data | Publicly reusable, modifiable, redistributable, and commercially usable under the applicable component license. |

## Provenance and Scope

### ThamizhiMorph

- Project: `https://github.com/sarves/thamizhi-morph`
- Website: `http://nlp-tools.uom.lk/thamizhi-morph/`
- Pinned source commit: `a296417ac603fd44eda35645369f1257d96bed89`
- Pinned upstream source: the morphology build records commit
  `a296417ac603fd44eda35645369f1257d96bed89` from the GitHub project.
- Verified license: Apache License 2.0.
- Copyright notice in the upstream license: Copyright 2020 Kengatharaiyer
  Sarveswaran (NLPC, University of Moratuwa).

The license covers source and object forms. Our patches, rebuilt LexC/Foma
sources, and compiled FSTs must therefore ship with a copy of Apache-2.0,
retain applicable notices, and clearly state that the files were modified.

The fallback ZIP archives do not contain embedded license or README files.
They must be documented as mirrors of the pinned Apache-2.0 upstream project,
not treated as independently licensed anonymous archives.

### Tamil Lexicon Headwords

- Described in the build as University of Madras Tamil Lexicon headwords
  supplied through the University of Chicago Digital South Asia Library.
- Dictionary page: `https://dsal.uchicago.edu/dictionaries/tamil-lex/`.
- License link on that page:
  `https://creativecommons.org/licenses/by-nc-nd/2.0/`.
- Verified on: 2026-07-23.
- Build input: the private Tamil Lexicon headword snapshot used by the
  morphology release pipeline.
- Current clean count: 106,486 lemmas in the release statistics.
- Verified site license: Creative Commons Attribution-NonCommercial-NoDerivs
  2.0 Generic (`CC BY-NC-ND 2.0`).
- Supplemental-permission status: the project owner confirms that he was
  authorized to use the supplied Lexicon data freely and distribute derivative
  works freely. The authorization record is retained as private provenance;
  the original and processed word lists are not public release artifacts.

The DSAL dictionary page identifies the work as the University of Madras
*Tamil lexicon* (1924-1936), says that its errata were applied when the text
was converted into a database, reports a September 2023 data update, and links
the database page's license notice to CC BY-NC-ND 2.0. Under that license:

1. unmodified material may be copied and redistributed with appropriate
   attribution and a link to the license;
2. use under the license must be noncommercial; and
3. adapted material may be made for private use, but may not be distributed
   under the license.

The current pipeline removes hyphens, filters characters, deduplicates and
normalizes headwords; classifies selected roots; incorporates them into
modified FST lexicons; and generates inflected forms. Those operations would
raise a NoDerivatives question under the public site license alone. The
project's separate authorization permits its derivative use and distribution,
so the intended compiled-FST and tokenizer-vocabulary release is cleared on the
facts confirmed by the project owner. This is an engineering release record,
not a determination that every headword or transformation is copyrightable.

The authorization record should remain in private provenance. The public
license policy records the usable downstream grant rather than publishing
private correspondence.

The public release must explicitly exclude the supplied raw headword file,
`lemma_dictionary.txt`, cleaned/normalized headword exports, generated and
heuristic word lists, and any other source-style lexical inventory. Compiled
FSTs can often be queried or enumerated, so they remain derivative artifacts
whose redistribution must fall within the 2022 authorization; merely omitting
the text lists does not turn them into non-derivative code. Detailed audit CSVs
that enumerate lexical surfaces or candidates are also private build artifacts;
only aggregate statistics belong in the default public bundle.

The original or processed DSAL-supplied material is not distributed. A verbatim
redistribution of such material would be a different release mode governed by
its own terms and is outside this policy.

### Tamil Wiktionary

- Namespace-0 title dump:
  `https://dumps.wikimedia.org/tawiktionary/latest/tawiktionary-latest-all-titles-in-ns0.gz`
- Page dump used for POS hints:
  `https://dumps.wikimedia.org/tawiktionary/latest/tawiktionary-latest-pages-articles.xml.bz2`
- Release statistics identify 98,104 source lemmas.

Wikimedia text is available under CC BY-SA 4.0 and GFDL, subject to the
license and attribution information attached to the relevant pages. A public
snapshot must pin its dump date or digest, link the source, retain attribution
and license notices, identify modifications, and satisfy share-alike terms.

### Vuizur

- Project: `https://github.com/Vuizur/Wiktionary-Dictionaries`
- Input: `Tamil-English Wiktionary dictionary.tsv`
- Release statistics identify 5,509 source lemmas.

The repository states that its extracted dictionaries are dual-licensed under
CC BY-SA 3.0 Unported and GFDL. Treat it as a separately attributed Wiktionary
derivative even when a lemma overlaps the official Tamil Wiktionary dump.

### Unicode CLDR

- Project: `https://github.com/unicode-org/cldr-json`
- Pinned release: 48.1.0
- Input: Tamil territory display names.
- License: Unicode License v3.

The Unicode permission notice must appear with distributed data or associated
documentation. Preserve the existing source commit and input digest.

### Wikidata

- Endpoint: `https://query.wikidata.org/sparql`
- Snapshot date: 2026-07-14
- Inputs: Tamil labels for countries, selected cities, and Indian/Sri Lankan
  regions.
- License: CC0 1.0 for structured data in the main, property, lexeme, and
  EntitySchema namespaces.

The entity source manifests and query text should remain in the public source
repository so the snapshot can be reproduced and audited.

## Artifact Impact Matrix

| Artifact | Inputs represented | Public status now |
| --- | --- | --- |
| Tokenizer Python code without bundled data | Project-authored code | Publicly released under Apache-2.0. |
| Documentation and aggregate statistics | Project-authored text plus factual source attribution | Can be published with citations; do not embed restricted lexical dumps. |
| Detailed lexical audit CSVs | FST-enumerated surfaces, source-backed candidates, and review decisions | Private build artifacts; exclude from the public runtime release. |
| Original and patched ThamizhiMorph build source | ThamizhiMorph plus project modifications | Software/FST-program layer may be released under Apache-2.0 with required upstream notices; source-style lexical inventories remain excluded. |
| Compiled FST models | ThamizhiMorph, local rules, source-backed lexical additions including Tamil Lexicon | Cleared for public release: Apache-2.0 governs the software/FST-program layer and CC BY-SA 4.0 governs the combined lexical/data layer, with all notices preserved. |
| `lemma_dictionary.txt` | Tamil Lexicon, Tamil Wiktionary, Vuizur | Private build input; explicitly excluded from public wheels and release archives. |
| Fixed tokenizer `tokens.txt` | Emittable lexical strings from mixed FST/source inventory plus project semantic and byte tokens | Cleared for public release under CC BY-SA 4.0 with attribution and source notices. |
| Generated and heuristic form lists | Mixed FST lexicons and source-derived classifications | Private build/audit inputs; explicitly excluded from the intended public runtime release. Any future dataset release requires a separate scope decision. |
| Full static Tamil dictionary | Mixed lexical inputs and generated forms | Private build/game artifact; explicitly excluded from the intended public tokenizer and FST release. |
| Geography entity JSONL and pinned source snapshots | CLDR and Wikidata | Redistributable with Unicode notice and CC0 provenance, independently of the lexical release. |
| Allowlisted runtime archives | Mixed artifacts | Publicly distributable when they contain the component policy, notices, applicable license texts, and no excluded source/audit lists. |

## Recommended Repository Licensing Layout

Use component-level licensing rather than one statement over the entire
repository:

- `LICENSE`: component-license summary and pointers.
- `LICENSE_POLICY.md`: authoritative component map and public release boundary.
- `NOTICE`: ThamizhiMorph attribution, modification statement, citations, and
  third-party component summary.
- `licenses/Apache-2.0.txt`: upstream ThamizhiMorph license.
- `licenses/CC-BY-4.0.txt`: project-authored documentation, article material,
  figures, aggregate results, and independently created non-software data.
- `licenses/CC-BY-NC-ND-2.0.txt`: Tamil Lexicon/DSAL license text or canonical
  license link and attribution notice for any permitted unmodified,
  noncommercial distribution; including this notice does not authorize the
  current transformed artifacts.
- `licenses/CC-BY-SA-4.0.txt` and `licenses/GFDL-1.3.txt`: official
  Wiktionary notices as applicable to the selected snapshot.
- `licenses/CC-BY-SA-3.0.txt`: Vuizur notice.
- `licenses/Unicode-3.0.txt`: CLDR notice.
- `licenses/CC0-1.0.txt`: Wikidata notice.
- `THIRD_PARTY_DATA.md`: human-readable provenance and artifact matrix.
- a machine-readable source manifest containing URLs, versions/dates,
  digests, transformations, counts, and license identifiers.

Do not state that the mixed vocabulary or FST release is Apache-2.0-only. The
Apache license can cover the code and ThamizhiMorph-derived work, while lexical
inputs and data snapshots retain their own terms.

## Immediate Release Gates

1. Record the verified DSAL CC BY-NC-ND 2.0 notice and preserve a dated
   snapshot or digest of the page and canonical license URL.
2. Preserve the Tamil Lexicon authorization record in private provenance and
   retain the public component-policy statement confirming the derivative-use
   and distribution rights relied upon by the release.
3. Preserve or fetch the exact Apache-2.0 license at the pinned ThamizhiMorph
   commit and verify the fallback ZIP contents against that source tree.
4. Pin Wiktionary and Vuizur snapshot commits/dates and retain their notices.
5. Retain the required license texts, `LICENSE_POLICY.md`, and `NOTICE` in each
   extracted public repository and release archive.
6. Mark project-authored software Apache-2.0 and project-authored documentation
   and article material CC BY 4.0.
7. Rebuild public archives from an explicit allowlist and automatically fail a
   release if any source, cleaned, generated, or heuristic word-list file is
   present or any included component has an unresolved status.
