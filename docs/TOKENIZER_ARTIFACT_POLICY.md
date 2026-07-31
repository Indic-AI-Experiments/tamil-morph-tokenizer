# Tokenizer Artifact Policy

## Runtime artifacts

The installable tokenizer requires:

- the 12 compiled FST models;
- the frozen lexical, semantic, byte, and realization-token vocabulary;
- reversible signature and reviewed compound-decomposition tables;
- the optional checksum-pinned Tamil geography gazetteer and its manifest.

No generated surface inventory is consulted when an input word is analyzed.
An input is recognized only through an FST analysis or an explicitly labeled
fallback path. The conservative unknown-suffix heuristic can consult an
externally supplied private lemma inventory during development, but safely
degrades when no such inventory is present.

The geography gazetteer is a separate tokenizer analysis model. It is not
merged into the FST lexicons or ordinary lexical dictionary. Its reviewed entries may
analyze entity case forms, while unreviewed city candidates remain inactive.
The vocabulary manifest pins both the gazetteer and gazetteer-manifest
checksums so fixed-ID reversal cannot silently use a different entity release.

## Private development artifacts

The following files may exist in the private morphology development workspace,
but are excluded from this public repository and the Python package:

- `lemma_dictionary.txt`: normalized mixed source-lemma inventory;
- `tamil_dictionary.txt.gz`: losslessly compressed offline union of lexical and generated forms;
- `fst_generated_forms.txt.gz`: losslessly compressed, deduplicated union of direct and secondary forms;
- `fst_heuristic_forms.txt`: retained as an empty compatibility artifact.

`fst_generated_forms.txt.gz` is a bounded, forward-validated audit inventory. The
final release does not admit inferred citation-form predictions into generated
coverage, so `fst_heuristic_forms.txt` contains zero rows. Neither file is
consulted by tokenizer runtime.

## Trust levels

1. Runtime FST analysis is morphological evidence.
2. A source lemma is lexical evidence, not proof of a complete paradigm.
3. A heuristic classification is audit evidence only, not a tokenizer analysis
   and not a semantic-token training target.
4. The full surface dictionary is useful for offline coverage comparison but a
   dictionary hit must never be presented as an FST parse.

These inventories are private build and audit inputs, not tokenizer release
artifacts.
