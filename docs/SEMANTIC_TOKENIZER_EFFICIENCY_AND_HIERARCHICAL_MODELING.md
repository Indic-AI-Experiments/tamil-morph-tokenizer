# Semantic tokenizer efficiency and hierarchical modeling ideas

Status: design notes for a future release and matched modeling experiments.
The frozen four-arm 42,364-row translation experiment is now complete; its
measured quality/efficiency trade-off informs the priorities below but does
not change the released tokenizer.

## Motivation

The current tokenizer proves that Tamil morphology can be represented with
explicit lemmas, grammatical features, ambiguity, deterministic provenance,
and exact reconstruction. Those properties are useful, but the current exact
model stream serializes every component into one flat token sequence.

External evaluation of `0.1.0-rc6` exposed the resulting efficiency problem.
On Tamil-script text, the evaluator measured approximately:

- 7.6 times the token fertility of a 64K BPE tokenizer;
- 12.4 tokens per word;
- 39% byte-fallback tokens;
- 22.6% of records containing at least one unsupported Tamil surface.

The exact definitions and failing examples from that evaluation should be
preserved before treating every number as a release result. In particular, a
record containing a reversible fallback is not necessarily a record containing
a model `<unk>` ID. Nevertheless, the fertility result is credible and
important.

The opening line of the Thirukkural illustrates the mechanism:

```text
அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு
```

With the externally tested `0.1.0-rc6` release it produced:

- 14 semantic morphology tokens before exact serialization;
- 95 tokens in the exact reversible model stream;
- 75 UTF-8 byte tokens;
- an exact successful round trip.

The three unsupported classical surfaces `அகர`, `எழுத்தெல்லாம்`, and
`முதற்றே` account for most of the expansion. The morphology representation
itself is not 7.6 times longer than BPE; the exact fallback and structural
serialization make it so.

The post-0437 coverage repair changes this specific line materially in the
deterministic `best` semantic mode used for the external comparison:

| Measure | rc6 observation | post-0437 |
| --- | ---: | ---: |
| analyzed word records | 4 of 7 | 7 of 7 |
| semantic morphology tokens | 14 | 21 |
| exact reversible model tokens | 95 | 41 |
| UTF-8 byte tokens | 75 | 6 |
| exact round trip | yes | yes |

The six remaining byte tokens are the six spaces, not unknown Tamil
surfaces. The exact stream is 54 positions shorter, a 56.8% reduction for
this line. Relative to the evaluator's nine BPE positions for the line, the
example-specific ratio falls from 10.6x to 4.6x. This is a targeted result,
not a replacement for the evaluator's full-corpus 7.6x measurement.

The default ambiguity-preserving codec emits 45 positions because `முதல`
retains its second valid reading; that four-token difference is ambiguity
information, not fallback.

The repair is deliberately split by cause:

- `எழுத்தெல்லாம்` exposed a class rule, not a missing lexeme. The same defect
  generated malformed `வீடுஎல்லாம்`, `மொட்டுஎல்லாம்`, and
  `ஆறுணெல்லாம்`. Patch 0437 changes the four affected short-`உ` noun paths
  to delete the final vowel before dependent `ெல்லாம்`; forward and inverse
  tests cover one representative of every class.
- `அகர` is a lexically licensed compound modifier of `அகரம்`. It is not
  evidence for deleting final `ம்` from every noun.
- `முதல` and `முதற்றே` are finite classical relations of `முதல்`. The latter
  retains an explicit focus clitic. These alternations are not generalized to
  arbitrary nouns or postpositions.

The development-corpus surface audit found 560 unknown types containing
`ல்லாம்`, covering 1,340 occurrences. That is an upper bound on the affected
surface area: it mixes nominative nouns with case-marked pronouns, adverbs,
verbal constructions, spelling fragments, and noise. Patch 0437 repairs only
the four demonstrated noun classes. The remaining families require separate
construction-level evidence rather than suffix-string acceptance. Across the
overlapping development snapshots, bare `அகர` occurred 10 times in six
documents and three corpus variants, including modern `அகர முதலி` usage;
this supported the constrained compound-modifier relation.

For a fixed training-token budget, high fertility means that a model sees less
actual text. It also increases attention cost, padding, memory use, and
preprocessing storage. These costs must be treated as first-class metrics
rather than accepted as the price of linguistic structure.

## Evidence from the 42,364-row translation comparison

The completed matched-example, matched-parameter experiment provides a useful
downstream measurement in addition to the external tokenizer audit. The
morphology-semantic arm led the four source-tokenizer arms at BLEU 15.94,
chrF++ 40.66, and reference-free COMETKiwi 0.6243. It also had the lowest
repeated-trigram rate at 10.35%. AI4Bharat was the nearest quality comparator
at BLEU 14.59 and chrF++ 39.89.

The quality gain came with a large efficiency cost. Mean Tamil source length
was 75.61 positions for morphology versus 27.05 for AI4Bharat, 33.89 for
Sarvam, and 48.28 for Brahmic. Morphology therefore used 2.80 times the mean
positions of AI4Bharat and trained 54.5% more slowly in the serial local run.

This one-seed result supports the hypothesis that explicit morphology carries
useful translation signal. It also strengthens the case that composition is
the next problem to solve: the current flat stream appears semantically useful
but computationally inefficient. The full run design, checksums, uncertainty
analysis, and 200-row Codex output review are maintained in
`TRANSLATION_FOUR_ARM_42364_RESULTS.md` in the separate
`tamil-tokenizer-experiments` repository.

## Central design hypothesis

Morphology is naturally factored and hierarchical:

```text
sentence
├── word
│   ├── lemma
│   ├── part of speech
│   ├── case or tense
│   ├── number/person/gender
│   └── realization information
└── word
    └── ...
```

The current model stream turns this tree into a long ordinary sequence. A flat
Transformer can learn that the tokens between word boundaries form one unit,
and successive layers can discover phrases and clauses. It is not guaranteed
to do so, however, and a small model must spend capacity and data rediscovering
structure that the tokenizer already knows.

A better interface may preserve morphology as factors attached to a word node,
compose those factors locally, and expose one or a small number of vectors per
word to sentence-level attention.

## Design goals

A future semantic tokenizer/model interface should aim for:

1. explicit, reusable Tamil morphological features;
2. approximately two to three model positions per Tamil word, including the
   unsupported tail;
3. near-zero raw byte fallback on ordinary Tamil, names, Latin text, and
   numerals;
4. no unknown model IDs;
5. exact reconstruction when the application requests it;
6. a faster, batched or persistent morphology runtime;
7. competitive translation or language-model quality per raw example and per
   compute unit;
8. a clean separation between semantic analysis, model representation, and
   lossless archival encoding.

The exact reversible stream need not be identical to the most efficient model
input stream. Exact surface bytes and offsets can be retained as a parallel
channel or dataset field when a training objective does not require the model
to predict them.

## Proposal A: factored word composer

Represent each analyzed word as a set or short ordered tuple of factors:

```text
lemma=படி
pos=verb
tense=past
person=third
number=singular
gender=masculine
```

Each factor receives an embedding. A word composer produces one word vector:

```text
lemma/features -> local composer -> word vector
```

The simplest composer is an additive factor embedding:

```text
h_word =
    E_lemma
  + E_pos
  + E_tense
  + E_person
  + E_number
  + E_gender
```

This is inexpensive and resembles factored neural machine translation. It
also makes a missing feature easy to represent with a typed null value.

More expressive alternatives include:

- a gated weighted sum of factor embeddings;
- a small MLP over concatenated factors;
- one intra-word attention layer with a learned word-summary query;
- a set encoder that is invariant to irrelevant factor ordering;
- a mixture over multiple valid morphological analyses.

The sentence encoder then receives one vector per word. Global attention no
longer operates over every lemma, tag, boundary marker, and realization token.

### Ambiguity

Ambiguity should not be flattened into an arbitrary best analysis without
measurement. Candidate strategies are:

- compose each analysis separately and use a learned weighted mixture;
- retain the deterministic best analysis plus an ambiguity summary vector;
- let sentence context attend over candidate analysis vectors;
- cap the number of candidates and record pruning explicitly.

Contextual analysis selection may be one of the strongest reasons to connect
the morphology system directly to a neural encoder.

## Proposal B: hierarchical or multiscale attention

Retain factor tokens but constrain early attention to operate inside words:

1. split the input into word groups using explicit boundaries;
2. run one or two local layers within each word;
3. create a summary node for each word;
4. run global sentence attention over word nodes;
5. optionally let global nodes retrieve detailed factor states through
   cross-attention.

This produces two positional coordinate systems:

- position of a word in the sentence;
- position or type of a factor inside the word.

A block-sparse attention mask can prevent every factor from attending to every
factor in the sentence. If a sentence contains `W` words and word `i` contains
`F_i` factors, the expensive global stage operates over `W` nodes instead of
`sum(F_i)` serialized positions.

Residual access to local states is important for translation phenomena that
depend on a specific case, agreement, or tense marker. Pooling must not erase
the very distinctions the semantic tokenizer was designed to expose.

## Proposal C: morphology-aware hybrid fallback

Raw UTF-8 bytes should be the final safety net, not the normal representation
of unsupported Tamil or mixed-script text.

### Implemented fixed-grapheme baseline (rc8)

Before introducing a learned fallback, rc8 adds a corpus-independent reversible
Tamil alphabet. It contains 378 grapheme tokens derived from the released
lexical inventory plus the assigned Tamil block and regular
consonant–dependent-vowel combinations. An ordinary unknown Tamil word is now
encoded as `<WORD_START>` plus one token per grapheme. A span containing an
unlisted grapheme, ZWNJ sequence, or malformed/mixed combining mark retains
whole-span UTF-8 byte fallback.

On the frozen 42,364-row translation training split, this alphabet compactly
covered 109,211 of the pre-repair 109,224 unknown records (99.988%). Its
estimated representation cost was 677,688 tokens including word boundaries,
versus 2,995,905 UTF-8 byte tokens, a 77.38% reduction. After the 0438
morphology repair, the remaining unknowns require an estimated 652,669
grapheme/boundary tokens instead of 2,885,592 bytes; 13 records still take the
intentional byte escape.

This is a strong deterministic baseline, not the final composer. It preserves
orthographic signal and exact reversal without learning units from protected
evaluation text.

A hierarchical fallback policy could be:

1. reviewed FST analysis and entity analysis;
2. learned Tamil subwords for unsupported Tamil surfaces;
3. multilingual subwords for names, English, Tanglish, and other scripts;
4. grapheme clusters where useful;
5. bytes only for genuinely exceptional or malformed input.

Unknown Tamil words would therefore look like:

```text
word node
├── Tamil subword
├── Tamil subword
└── optional coarse unknown-morphology marker
```

Their subwords can be composed into one word vector before sentence-level
attention. This preserves a bounded vocabulary without making every
three-byte Tamil code point consume three global model positions.

The fallback tokenizer must be trained only on permitted training data.
Protected evaluation text must not influence its vocabulary.

## Proposal D: separate semantic and exact channels

The current exact codec combines three responsibilities:

- linguistic analysis;
- model input;
- byte-identical reconstruction.

Those responsibilities can be exposed as separate synchronized channels:

```text
semantic factors: lemma, POS, case, tense, ...
model fallback:   learned subwords for unsupported spans
surface metadata: original bytes, offsets, normalization and realization data
```

Applications that require exact decoding can retain the surface channel.
Language-model training can consume the semantic and fallback channels without
forcing whitespace, punctuation, and every unknown surface byte through global
attention.

If exact generation from model IDs remains a requirement, a separate surface
decoder or auxiliary reconstruction objective may be more efficient than
placing all reconstruction instructions in the primary sequence.

## Proposal E: faster morphology runtime

`FlookupAnalyzer.analyze()` currently starts `flookup` once for each FST model
on every call. Large batches amortize that cost, but record-at-a-time use can
fall to only a few records per second.

Potential improvements:

- keep one persistent `flookup` worker per FST model;
- batch unique words across many documents;
- cache analyses by normalized surface and release checksum;
- use an on-disk cache for reproducible corpus preprocessing;
- investigate direct library bindings or a compiled unified analyzer;
- separate entity lookup and FST analysis so each can be profiled;
- make throughput, cache-hit rate, and batch size part of every manifest.

The runtime cache key must include the morphology release, FST checksums,
tokenizer configuration, normalization policy, and entity release.

## Proposal F: reduce structural overhead

Every structural token should justify a model-learning purpose. Audit the
frequency and predictive value of:

- `<WORD_START>`;
- FST model identifiers;
- tag and compound variant selectors;
- realization selectors;
- explicit ambiguity delimiters;
- whitespace and punctuation bytes.

Some information may be better represented as:

- segment IDs or attention masks rather than ordinary tokens;
- typed factor fields;
- side-channel metadata;
- position features;
- auxiliary targets used only during training;
- deterministic decoder state.

Removing a token from the model stream does not require removing the
corresponding provenance from the encoded dataset.

## What successive Transformer layers already provide

A standard Transformer can develop an implicit hierarchy:

- early layers often capture local and lexical relations;
- middle layers can combine morphology and short phrases;
- later layers can represent longer syntactic or semantic dependencies.

This flexibility is valuable and is the reason a flat baseline must remain in
the evaluation. But implicit hierarchy has costs:

- it consumes data and capacity;
- it may not align with word boundaries;
- dense attention still pays for every serialized position;
- small models may never learn the desired grouping robustly.

The research question is not whether Transformers can learn hierarchy. It is
whether supplying correct word-level structure improves quality or efficiency
enough to justify the additional architectural bias.

## Evaluation principles

Tokenizer and architecture effects must not be conflated.

The completed frozen four-arm translation experiment correctly gave every
tokenizer the same flat Transformer. A hierarchical encoder used only for
morphology remains a separate architecture ablation, not evidence from that
tokenizer-only comparison.

A future study should include at least:

1. BPE with the flat baseline encoder;
2. current semantic stream with the flat baseline encoder;
3. hybrid morphology/subword stream with the flat baseline encoder;
4. hybrid morphology with the word composer;
5. hybrid morphology with hierarchical attention.

Report two complementary budgets:

- equal raw examples or characters, measuring benefit from linguistic bias;
- equal training tokens or compute, measuring deployment efficiency.

Hold the cleaned dataset, split, target tokenizer, decoder, parameter budget,
optimizer, random seed, and evaluation settings constant where the comparison
permits it.

Required measurements include:

- SacreBLEU, chrF++, COMET, and qualitative adequacy;
- number and named-entity preservation;
- fallback and unknown behavior;
- model positions per word, character, and sentence;
- raw characters and examples processed per second;
- training and decoding throughput;
- peak memory and checkpoint size;
- preprocessing throughput and cache behavior;
- exact reconstruction rate when exact mode is enabled;
- performance by classical, modern, colloquial, entity-heavy, mixed-script,
  and noisy strata.

## Suggested gates before another large training run

Do not launch a large language-model experiment merely because a prototype is
linguistically appealing. Require the following preflight gates:

1. zero unexplained round-trip failures in exact mode;
2. approximately two to three positions per Tamil word on the intended corpus;
3. near-zero byte fallback on normal Tamil and mixed text;
4. no unknown model IDs;
5. tokenizer throughput compatible with corpus-scale preprocessing;
6. parameter-matched overfit and checkpoint/resume tests;
7. a small matched pilot showing coherent translations;
8. a measured projection for wall time, storage, memory, and external cost.

## Staged implementation plan

### Stage 0: preserve external evidence

- obtain the evaluator's exact corpus manifest, tokenizer commands, metric
  definitions, failing round-trip examples, and output checksums;
- reproduce the benchmark locally without using protected text for design;
- distinguish unsupported-surface incidence from literal unknown token IDs.

### Stage 1: representation audit

- attribute fertility to semantic factors, structural tokens, whitespace,
  punctuation, realization metadata, Tamil fallback, and non-Tamil fallback;
- publish per-domain and percentile distributions rather than one mean;
- identify tokens that can become fields, masks, or side-channel metadata.

### Stage 2: hybrid fallback prototype

- retain the implemented fixed 378-token Tamil grapheme baseline;
- train a permitted-data Tamil/multilingual subword fallback only if it beats
  that baseline on fertility and downstream quality;
- retain bytes only as the final total-coverage mechanism;
- verify exact mode independently;
- target the two-to-three-position-per-word gate.

### Stage 3: word composer prototype

- begin with additive factor embeddings as the transparent baseline;
- compare gated composition and one-layer intra-word attention;
- preserve per-feature ablations so gains can be interpreted.

### Stage 4: hierarchical encoder

- add word-local masks and word-summary nodes;
- compare full pooling, residual detail access, and cross-attention retrieval;
- measure whether global sequence reduction produces real wall-time and memory
  gains rather than only a lower token count.

### Stage 5: matched downstream pilot

- use a small, frozen translation treatment;
- compare quality per raw example and quality per unit compute;
- advance only if translations are coherent and efficiency is competitive.

## Risks and open questions

- A hard word hierarchy may be wrong for compounds, clitics, multiword
  entities, punctuation attachment, and orthographic variation.
- Pooling can hide information needed by the decoder.
- FST analysis errors may become more influential when encoded as explicit
  factors.
- A large lemma vocabulary may dominate parameters even if sequences shorten.
- A hybrid fallback may learn the same useful regularities as BPE and make
  some explicit morphological factors redundant.
- Contextual disambiguation may require more data than the small translation
  experiment provides.
- Exact surface reconstruction and optimal semantic modeling may require
  different representations.
- Efficiency improvements must be demonstrated in end-to-end wall time, not
  inferred only from sequence length.

## Current recommendation

Keep the current TamilLM or other already-tokenized large training pack on its
frozen BPE tokenizer. Do not retroactively change or rerun the completed
four-arm translation experiment.

Treat the post-0443/rc10 candidate as a strong morphology and provenance system
with a compact fixed-grapheme safety layer, but whose current flat exact
serialization is not yet an efficient general-purpose LM tokenizer. The next
design should preserve the linguistic analysis while changing how that
analysis is presented to a neural model. Compare the word-composed morphology
arm first against AI4Bharat on the frozen 42,364-row split, reporting both
matched-example and matched-source-token budgets.
