# Third-Party Notices

This research preview contains software and data from multiple sources. The
license texts in `licenses/` apply to their respective components; no single
license relicenses the entire mixed repository.

## ThamizhiMorph

The Tamil finite-state morphology system is based on ThamizhiMorph:

- Copyright 2020 Kengatharaiyer Sarveswaran
  (`iamsarves@gmail.com`), NLPC, University of Moratuwa
- Source: `https://github.com/sarves/thamizhi-morph`
- Pinned revision: `a296417ac603fd44eda35645369f1257d96bed89`
- License: Apache License 2.0

The FST lexicons, rules, build process, and compiled models have been
substantially modified. The ordered patch archive and build manifest identify
the modifications and their provenance.

Please cite:

Kengatharaiyer Sarveswaran, Gihan Dias, and Miriam Butt. "ThamizhiMorph: A
morphological parser for the Tamil language." Machine Translation 35, 37-70
(2021). `https://doi.org/10.1007/s10590-021-09261-5`

## Tamil Wiktionary and Vuizur

Tamil Wiktionary content is used under its Wikimedia licensing terms. The
Vuizur Tamil-English dictionary is an extracted Wiktionary derivative whose
repository states CC BY-SA 3.0 or GFDL licensing. Source URLs and snapshot
details are recorded in `THIRD_PARTY_DATA.md` or
`docs/THIRD_PARTY_DATA_AND_LICENSE_MATRIX.md`.

## Unicode CLDR

Tamil territory display names are derived from Unicode CLDR 48.1.0. The
Unicode License v3 copyright and permission notice is included in
`licenses/Unicode-3.0.txt`.

## Wikidata

Selected Tamil entity labels were queried from Wikidata on 2026-07-14.
Wikidata structured data is available under CC0 1.0.

## Tamil Lexicon

The mixed lexical artifacts contain headwords supplied through the University
of Chicago from the University of Madras Tamil Lexicon. The DSAL page links CC
BY-NC-ND 2.0. Separately, the project owner confirms authorization to use the
supplied data freely and distribute derivative works freely. This repository
does not distribute the original, cleaned, or generated word lists. Its
compiled FSTs and tokenizer vocabulary are derivative runtime artifacts whose
combined lexical/data layer is distributed under CC BY-SA 4.0, preserving the
ShareAlike terms of incorporated Wiktionary-derived material.
