# License Status

Status date: 2026-07-23

Project-authored software is licensed under Apache-2.0. Project-authored
documentation, article material, figures, aggregate results, and independently
created non-software data are licensed under CC BY 4.0. The lexical/data layer
of the compiled FSTs and fixed tokenizer vocabulary is distributed under CC
BY-SA 4.0 so applicable Wiktionary ShareAlike terms are preserved. Third-party
terms are inventoried in the source document
`docs/THIRD_PARTY_DATA_AND_LICENSE_MATRIX.md` (bundled as
`THIRD_PARTY_DATA.md` in the morphology preview) and the machine-readable
`third-party-components.json`.

Verified inputs are:

- ThamizhiMorph: Apache-2.0, pinned at
  `a296417ac603fd44eda35645369f1257d96bed89`;
- Tamil Wiktionary: CC BY-SA/GFDL terms with attribution and share-alike
  obligations;
- Vuizur Wiktionary dictionaries: CC BY-SA 3.0/GFDL;
- Unicode CLDR: Unicode License v3;
- Wikidata structured entity data: CC0 1.0;
- Tamil Lexicon/DSAL public site: CC BY-NC-ND 2.0, supplemented by the project
  owner's confirmed authorization to use the supplied data freely and
  distribute derivative works freely.

The project owner confirms authorization to use the supplied Tamil Lexicon data
freely and distribute derivative works freely. The public package therefore
includes the compiled FSTs and fixed tokenizer vocabulary as derivative runtime
artifacts, while excluding the supplied raw list, cleaned and mixed lemma
dictionaries, and generated/heuristic word lists. The authorization record
should be retained in the private provenance archive; it is no longer a public
release blocker under the facts confirmed by the project owner.

Public distributions must include `LICENSE`, `LICENSE_POLICY.md`, `NOTICE`, the
component inventory, and the applicable license texts. No single license
relicenses every third-party component.
