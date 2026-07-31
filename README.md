# Tamil Morphology-Aware Reversible Tokenizer

> The current package is an audited research release with an independently
> decodable reversible token stream. The fixed token-ID vocabulary is specified
> in `docs/TOKENIZER_OUTPUT_CONTRACT.md` and
> `docs/REVERSIBLE_TOKENIZER_DESIGN.md`.

A Python package for a morphology-aware Tamil tokenizer. It consumes versioned
runtime assets from the independent Tamil morphology repository:

- 12 patched ThamizhiMorph/Foma runtime models
- a checksum-pinned fixed vocabulary and reversible signature codebook
- checksum-pinned entity and realization resources

The package calls `flookup` only for Tamil words, parses FST analyses, maps morphology tags to readable tokens, preserves all analyses, and picks a deterministic best analysis when requested. The reversible codec uses fixed Tamil grapheme tokens for ordinary unknown Tamil and bounded UTF-8 bytes as the final escape for malformed or unsupported input. The older demonstration tokenizer can still preserve an unknown Tamil surface as one diagnostic token.

The installable tokenizer package includes the compiled FSTs and frozen token
vocabulary. Original, cleaned, and generated word lists are excluded from both
the public repository and Python wheel. `TamilWordLists` can inspect an
explicitly supplied private development directory when source-membership audits
are needed; missing lists resolve to empty inventories and are not required for
runtime tokenization.

## Documentation

The morphology and token-stream contracts are documented in `docs/`:

- `docs/TOKENIZER_FST_DATA_PROVENANCE.md` explains the source and checksums of the packaged FST and lexical assets.
- `docs/CANONICAL_AMBIGUITY_ENCODING.md` defines the non-redundant `<READINGS>/<ALT>` model-stream grammar.
- `docs/PUNCTUATION_AND_ABBREVIATION_POLICY.md` defines lexical boundaries, exact punctuation preservation, and conservative abbreviation recognition.
- `docs/FST_CLASS_RULE_VOCABULARY_REFERENCE.md` records generated class, rule, tag, and vocabulary statistics.
- `docs/SEMANTIC_TOKEN_VOCABULARY.md` lists and explains all 222 fixed
  grammatical and semantic labels and their release token IDs. The manifest's
  broader 284-entry model-factor region also contains 62 secondary lexical
  components.
- `docs/DEVELOPMENT_CORPUS_COVERAGE_2026_07_23.md` reports the current pinned
  multi-corpus development coverage, UD agreement, and entity stress results.

The same complete inventory is available as machine-readable JSON at
`tamil_morph_tokenizer/data/vocabulary/semantic_token_reference.json`. The
interactive public interface is
[anandmurugan.me/resources/tamil-tokenizer](https://anandmurugan.me/resources/tamil-tokenizer).

## Setup

From this folder:

```bash
./scripts/setup.sh
source .venv/bin/activate
```

The setup script installs Foma when `flookup` is absent, creates `.venv`, and
installs the package with development dependencies. It supports Homebrew on
macOS and `apt`, `dnf`, or `pacman` on Linux. To install additional Python
dependency groups, pass a comma-separated extras list:

```bash
./scripts/setup.sh dev,hf,server
```

For manual setup, install Foma first (`brew install foma` on macOS or
`sudo apt-get install foma-bin` on Debian/Ubuntu), verify `flookup` is on
`PATH`, create a virtual environment, and run `pip install -e '.[dev]'`.

Optional Hugging Face comparison dependencies:

```bash
pip install -e '.[hf]'
```

Optional HTTP API dependencies:

```bash
pip install -e '.[server]'
tamil-morph-tokenizer-api
```

The service exposes `POST /tokenize`, `GET /health`, and interactive OpenAPI
documentation at `/docs`. Tokenization defaults to `compact_ambiguity`. Set
`TOKENIZER_API_TOKEN` to require a bearer token in hosted deployments.

## Quick Demo

```bash
tamil-morph-tokenize மரங்களிலிருந்து படித்தான் xyz
```

Expected behavior:

- `மரங்களிலிருந்து` is analyzed as a noun with plural + ablative case morphology.
- `மரங்களும்` is analyzed as a plural nominative noun plus additive `உம்`, emitted as `<CLITIC_ADD>`.
- common function words such as `என`, `மட்டும்`, `இல்லை`, and `ஏன்` are FST-backed rather than unknown-surface fallbacks.
- deictic forms such as `இப்பொழுது`, `எப்பொழுது`, `இந்நிலையில்`, and `இவ்வகை` are FST-backed with explicit proximity/time/type/situation tags.
- corpus-audit fallbacks such as `தேர்தல்`, `பாலம்`, `நடவடிக்கை`, `சுமார்`, and `அதனால்` are now FST-backed.
- pronoun/quantifier/function forms such as `தங்கள்`, `ஒருவர்`, `அனைவரும்`, `எல்லா`, `எத்தனை`, `வேண்டாம்`, and `உண்டா` are FST-backed with explicit semantic tags.
- `படித்தான்` is analyzed as a finite verb with past/masculine singular morphology.
- modern spoken forms such as `பண்ணுறார்`, `பார்த்தீங்களா`, `படிச்சியா`,
  `செஞ்சு`, and `விட்டுடு` retain explicit tense, agreement, question,
  nonfinite-link, and colloquial information.
- gendered participial nouns such as `போனவன்` and `சென்றவன்` are analyzed
  productively rather than stored as isolated surface forms.
- unknown Tamil text preserves the surface word as one token by default with `fallback="unknown_tamil_surface"`.
- grapheme-cluster fallback using the `regex` package (`\X`) is still available with `TamilMorphTokenizer(unknown_tamil_fallback="grapheme")`.
- simple unknown Tamil case forms can use suffix fallback, for example `இந்தியாவை -> இந்தியா <CASE_ACC>`, marked with `fallback="suffix_heuristic"`.
- non-Tamil spans such as `xyz` are preserved as one surface token.
- sentence punctuation is split from adjacent lexical words and round-trips exactly; a single Tamil word followed by `.` is not classified as an abbreviation.

Ambiguous analyses can be rendered without collapsing to one best reading:

```bash
tamil-morph-tokenize --mode compact_ambiguity காட்டில் புத்தகத்தில்
tamil-morph-tokenize --mode all_analyses காட்டில் புத்தகத்தில்
```

`compact_ambiguity` is the default mode. Analyzed surface text is retained in
the structured record and omitted from the model token list. Shared semantic
prefixes are emitted once; complete residual readings are separated by
`<READINGS>` and `<ALT>`. Use `--mode best` for token-count comparisons that
need one selected analysis per word.

The exact codec preserves whitespace and unknown text and uses
conditional inverse-FST realization tokens:

```python
from tamil_morph_tokenizer import FixedVocabulary, StructuredReversibleCodec

codec = StructuredReversibleCodec()
vocabulary = FixedVocabulary()
encoded = codec.encode("மரங்களை  xyz🙂")
assert codec.decode(encoded) == "மரங்களை  xyz🙂"
assert codec.decode_tokens(encoded.tokens) == "மரங்களை  xyz🙂"
input_ids = vocabulary.encode(encoded.tokens)
assert codec.decode_ids(input_ids, vocabulary) == "மரங்களை  xyz🙂"
```

`decode_tokens` and `decode_ids` read only the flat bounded stream. The current
140,922-token vocabulary is a deterministic, checksum-pinned build containing
139,895 lemma tokens. The FST upper language emits 218,419 lexical strings;
78,538 reviewed productive composites are represented by typed chains and
intentionally have no atomic token ID. Splitter reachability and the strict
Tamil combining-mark audit both pass with zero blocking lexical entries; see
`docs/AUXILIARY_SEMANTICS_AUDIT.md`.

Post-0443 morphology adds productive, class-constrained nominal modifiers in
`-ஆன` and `-அற்ற` plus reviewed compositional manner and distributive
adverbials. The productive noun grammar adds about 1.01 million licensed paths;
the lexical seed counts are not the total coverage. Noun-derived modifier
relations now have one owner, `noun.fst`; `adj.fst` contains no copied
noun-led analyses. See
`docs/PRODUCTIVE_MODIFIER_COVERAGE_2026_07_26.md`.

The HTTP API exposes this exact global model stream as `tokens` plus parallel
`token_ids`; per-word `records` are diagnostic metadata. It preserves leading,
internal and trailing whitespace. `<WORD_START>` synchronizes analyzed words,
while whitespace, punctuation and unknown material are emitted directly as
`<BYTE_XX>` tokens without redundant end or byte-span wrappers.

The semantic layer decomposes 78,538 reviewed productive compounds:

```text
படித்துக்கொடுத்தான் -> படி <LINK_VPART> கொடு <TENSE_PAST> ...
செய்துவிட்டான்      -> செய் <LINK_VPART> விடு <TENSE_PAST> ...
படிக்கப்படமுடியும்  -> படி <VOICE_PASSIVE> <LINK_INFINITIVE> முடி ...
```

The typed links preserve the internal nonfinite construction. Productive `படு`
is normalized to `<VOICE_PASSIVE>`. Unique typed chains no longer serialize the
raw composite lemma; colliding chains use a bounded compound variant when needed.
Exact raw FST tag suffixes use a checksum-pinned codebook: the default pattern
costs no residual token and non-default patterns use one `<TAG_VARIANT_n>`.

Valid single-hyphen lexical expressions such as `நேருக்கு-நேர்` remain one
Tamil morphology span. Unhyphenated variants are added only when independently
attested; the tokenizer does not mechanically fuse phrase-like expressions.

## Compare Against Hugging Face Tokenizers

```bash
python scripts/compare_hf_tokenizers.py --text "மரங்களிலிருந்து படித்தான் கொடுப்பேன் வருகிறேன்"
```

This compares token counts against:

- `gpt2`
- `bert-base-multilingual-cased`
- `google/mt5-small`
- `xlm-roberta-base`

The first run may download model tokenizer files from Hugging Face.

## Evaluate Coverage on Hugging Face Datasets

```bash
python scripts/evaluate_tokenizer_on_hf_dataset.py \
  --dataset mozhi-ai/tamil-corpus \
  --split train \
  --text-column text \
  --limit 1000
```

The evaluator streams dataset rows, runs `TamilMorphTokenizer`, and writes coverage triage files under `outputs/hf_dataset_eval/`: a summary JSON/Markdown file, unknown Tamil surfaces, suffix-heuristic hits, ambiguous surfaces, semantic specials, unknown suffixes, and sample records. Use `--min-quality-score`, `--min-language-score`, or repeated `--filter-field FIELD=VALUE` options when a dataset exposes quality metadata.

## Data Provenance

The 12 FSTs and tokenizer-facing lexical assets are checksum-pinned releases
from the independent
[`tamil-morphology`](https://github.com/Indic-AI-Experiments/tamil-morphology)
repository. The morphology release records the complete ThamizhiMorph patch
history, source evidence, build manifest, and regression results.

## License

This is a component-licensed open project. Project-authored software uses
Apache-2.0; documentation and article material use CC BY 4.0; and the
lexical/data layer of the compiled FSTs and fixed tokenizer vocabulary uses CC
BY-SA 4.0 to preserve applicable Wiktionary ShareAlike terms. Commercial use,
modification, and redistribution are allowed subject to the component terms and
attribution requirements. Original and processed Tamil Lexicon word lists are
not distributed. See `LICENSE`, `LICENSE_POLICY.md`, `NOTICE`, and
`docs/THIRD_PARTY_DATA_AND_LICENSE_MATRIX.md`.
