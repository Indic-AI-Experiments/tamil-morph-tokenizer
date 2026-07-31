# Licensing Policy

Effective date: 2026-07-23

This project is intended to be reusable, modifiable, redistributable, and
commercially usable by the public. It uses component-level licensing because
no single permissive license can accurately cover its software, linguistic
data layers, documentation, and upstream materials.

## Component Map

| Component | License | What recipients may do |
| --- | --- | --- |
| Project-authored Python, JavaScript, shell code, build/evaluation tools, APIs, tests, and original FST program/rule contributions | Apache License 2.0 | Use, modify, distribute, sublicense, and use commercially, subject to the license and preserved notices. |
| ThamizhiMorph-derived FST program, rules, source, and compiled software layer | Apache License 2.0 | Use, modify, and redistribute, including commercially, with the upstream license, attribution, notices, and modification statements. |
| Lexical/data layer embodied in the public compiled FSTs and fixed tokenizer vocabulary | CC BY-SA 4.0 | Use, query, copy, modify, redistribute, and use commercially with attribution and ShareAlike for adaptations. |
| Project-authored documentation, article text, diagrams, figures, aggregate results, and independently created non-software data | CC BY 4.0 | Copy, adapt, redistribute, and use commercially with attribution. |
| Tamil Lexicon-derived runtime material | Included in the CC BY-SA 4.0 lexical/data layer under the project owner's separate authorization to use the supplied Lexicon data freely and distribute derivative works freely | Same downstream terms as the public lexical/data layer; the original and processed source lists are not distributed. |
| Tamil Wiktionary-derived material | CC BY-SA 4.0 or GFDL, with this project using CC BY-SA 4.0 for the combined public lexical/data layer | Commercial reuse and adaptation are allowed with attribution and ShareAlike. |
| Vuizur Tamil-English Wiktionary-derived material | CC BY-SA 3.0 or GFDL; adaptations may use a later CC BY-SA version, so the combined public lexical/data layer uses CC BY-SA 4.0 | Commercial reuse and adaptation are allowed with attribution and ShareAlike. |
| Unicode CLDR entity data | Unicode License v3 | Reuse subject to preservation of the Unicode notice. |
| Wikidata entity data | CC0 1.0 | Unrestricted reuse to the extent covered by CC0. |
| Third-party tokenizers, models, datasets, and evaluation corpora | Their respective upstream terms | Consult the experiment manifest or model/dataset card; this policy does not relicense them. |

## Public Runtime Boundary

The intended public tokenizer and morphology releases include:

- project-authored software;
- compiled FST models;
- the fixed tokenizer vocabulary and required codebooks;
- entity runtime resources whose licenses permit redistribution;
- manifests, checksums, notices, documentation, and aggregate statistics.

They exclude:

- the original Tamil Lexicon data supplied to the project owner;
- `lemma_dictionary.txt`, `tamil_dictionary.txt`, and cleaned headword exports;
- generated and heuristic form lists;
- detailed lexical candidate and audit tables; and
- third-party training or evaluation datasets unless their own release terms
  expressly permit bundling.

The compiled FSTs can be queried or enumerated, and the fixed vocabulary lists
token strings. They are therefore treated transparently as derivative runtime
artifacts, not as a way to conceal or evade data-license obligations.

## Tamil Lexicon Authorization

The project owner confirms that he was authorized to use the supplied Tamil
Lexicon data freely and to distribute derivative works freely. On that basis,
the project distributes only its derivative runtime artifacts, not the source
or processed Lexicon lists. The authorization record should be retained in the
private provenance archive even though the underlying correspondence need not
be published.

The project applies CC BY-SA 4.0 to its copyright and database rights in the
combined lexical/data layer so every recipient receives an explicit public
right to use, adapt, redistribute, and commercially use that layer. ShareAlike
is used because the combined layer also contains Wiktionary-derived material;
it is not an additional restriction originating from the Tamil Lexicon.

## Attribution

A redistribution should retain `LICENSE`, `LICENSE_POLICY.md`, `NOTICE`, and
the relevant texts in `release/licenses/` or an equivalent `licenses/`
directory. At minimum, acknowledge:

- Anand Murugan and the Tamil Morph Tokenizer project;
- Kengatharaiyer Sarveswaran, Gihan Dias, and Miriam Butt / ThamizhiMorph;
- University of Madras, *Tamil Lexicon*, via the University of Chicago Digital
  South Asia Library;
- Tamil Wiktionary and Wikimedia contributors;
- Vuizur's Wiktionary-Dictionaries project where its extract contributed;
- Unicode CLDR and Wikidata for included entity resources.

Recipients must identify modifications where the applicable Apache or Creative
Commons terms require it. Attribution does not imply endorsement.

## Articles, Experiments, Datasets, and Model Weights

- The planned public article and project-created figures use CC BY 4.0 unless
  explicitly marked otherwise.
- Evaluation code uses Apache 2.0.
- Aggregate measurements and project-created result tables use CC BY 4.0.
- Curated or synthetic parallel data must have a dataset card identifying every
  source and its controlling terms; no blanket repository license overrides
  those terms.
- Trained model weights receive a separate model card and license after the
  training-data and base-model terms are audited. They are not automatically
  covered by this repository policy.

## No Claim Over Language Facts

The project does not claim exclusive rights in individual Tamil words,
grammatical facts, paradigms, tags, or other material that is not protected by
applicable copyright or database law. The licenses apply only to rights that
the relevant licensor has authority to grant.

## Warranty

All components are provided without warranties, as stated in their controlling
licenses. This policy is an engineering distribution policy and component map;
it does not replace the legal text of any referenced license.
