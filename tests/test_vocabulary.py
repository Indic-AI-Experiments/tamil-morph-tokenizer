import json
from pathlib import Path
import shutil

import pytest

from tamil_morph_tokenizer import (
    FixedVocabulary,
    ProductiveCompoundLexicon,
    StructuredReversibleCodec,
)
from tamil_morph_tokenizer.codec import MODEL_TO_TOKEN
from tamil_morph_tokenizer.fallback import tamil_grapheme_token
from tamil_morph_tokenizer.signature import TAG_VARIANT_TOKENS


VOCABULARY_DIR = Path(__file__).parents[1] / "tamil_morph_tokenizer" / "data" / "vocabulary"


@pytest.fixture(scope="module")
def vocabulary():
    return FixedVocabulary(VOCABULARY_DIR)


def test_frozen_vocabulary_is_unique_and_matches_manifest(vocabulary):
    manifest = json.loads((VOCABULARY_DIR / "manifest.json").read_text(encoding="utf-8"))

    assert len(vocabulary.tokens) == len(set(vocabulary.tokens))
    assert len(vocabulary.tokens) == manifest["counts"]["tokens"]
    assert manifest["counts"]["lemmas"] > 0
    assert manifest["counts"]["fst_emitted_lexical_strings"] >= manifest["counts"]["lemmas"]
    assert manifest["counts"]["decomposition_only_lexical_strings"] == len(
        manifest["decomposition_only_lexical_strings"]
    )
    assert manifest["counts"]["excluded_productive_compounds"] == 78_538
    assert vocabulary.tokens[:4] == ("<PAD>", "<BOS>", "<EOS>", "<UNK>")


def test_frozen_vocabulary_contains_codec_alphabet_and_runtime_lemmas(vocabulary):
    for value in range(256):
        assert vocabulary.token_id(f"<BYTE_{value:02X}>") >= 0
    for grapheme in ("அ", "கா", "ஷெ", "ஹூ", "-", "௹"):
        assert vocabulary.token_id(tamil_grapheme_token(grapheme)) >= 0
    for model_token in MODEL_TO_TOKEN.values():
        assert vocabulary.token_id(model_token) >= 0
    for variant_token in TAG_VARIANT_TOKENS:
        assert vocabulary.token_id(variant_token) >= 0
    for lemma in ("மரம்", "படி", "பயன்படுத்து", "வேண்டு"):
        assert vocabulary.token_id(lemma) >= 0
    for composite in ("படித்துக்கொடு", "செய்துவிடு", "படிக்கப்படமுடி"):
        assert composite not in vocabulary
    for held in ("தொலை", "கோவை"):
        assert held in vocabulary
    for invalid in ("அவிழ்க்கூடு", "அட்டமுடி", "அவிழ்ப்படக்கூடு"):
        assert invalid not in vocabulary


def test_all_reviewed_composites_are_excluded_from_atomic_ids(vocabulary):
    entries = ProductiveCompoundLexicon().entries()
    required_lexemes = {
        lexical
        for decomposition in entries.values()
        for lexical in (
            decomposition.base_lemma,
            *(link.lemma for link in decomposition.links),
        )
    }
    for composite in entries:
        if composite in required_lexemes:
            assert composite in vocabulary
        else:
            assert composite not in vocabulary


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_ids_round_trip_independently_of_structured_metadata(vocabulary):
    codec = StructuredReversibleCodec()
    text = "மரங்களை  படித்தேன் xyz🙂"
    encoding = codec.encode(text)

    input_ids = vocabulary.encode(encoding.tokens)

    assert codec.decode_ids(input_ids, vocabulary) == text


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_tag_variant_ids_round_trip(vocabulary):
    codec = StructuredReversibleCodec()
    encoding = codec.encode("பயன்படுத்தப்படுகிறது")

    assert "<TAG_VARIANT_1>" in encoding.tokens
    assert codec.decode_ids(vocabulary.encode(encoding.tokens), vocabulary) == "பயன்படுத்தப்படுகிறது"


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_productive_compound_ids_round_trip_without_atomic_semantic_lemma(vocabulary):
    codec = StructuredReversibleCodec()
    text = "படிக்கப்படமுடியும்"
    encoding = codec.encode(text)

    input_ids = vocabulary.encode(encoding.tokens)

    assert encoding.spans[0].semantic_tokens[:5] == (
        "படி",
        "<VOICE_PASSIVE>",
        "<MODAL>",
        "<LINK_INFINITIVE>",
        "முடி",
    )
    assert "படிக்கப்படமுடி" not in encoding.tokens
    assert codec.decode_ids(input_ids, vocabulary) == text


def test_optional_entity_layer_has_frozen_semantic_ids(vocabulary):
    for token in (
        "<ENTITY_PERSON>",
        "<ENTITY_CITY>",
        "<ENTITY_ORG>",
    ):
        assert token in vocabulary
    assert "<READINGS>" in vocabulary
    assert "<ALT>" in vocabulary
    assert "<ANALYSIS_START>" not in vocabulary
    assert "<ANALYSIS_END>" not in vocabulary
    assert not any("_CAND_" in token or token.startswith("<CAND_") for token in vocabulary.tokens)


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_dynamic_entity_lemma_ids_round_trip_without_surface_bytes(vocabulary):
    codec = StructuredReversibleCodec()
    encoding = codec.encode("தமிழ்நாட்டிலிருந்து")

    assert "<LEXICAL_BYTES_START>" in encoding.tokens
    assert "<ENTITY_GAZETTEER_MODEL>" in encoding.tokens
    assert "<SURFACE_BYTES>" not in encoding.tokens
    assert codec.decode_ids(vocabulary.encode(encoding.tokens), vocabulary) == "தமிழ்நாட்டிலிருந்து"


def test_manifest_passes_lexical_and_splitter_release_gates(vocabulary):
    assert vocabulary.release_ready
    assert vocabulary.manifest["counts"]["blocking_lemma_issues"] == 0
    assert vocabulary.manifest["counts"]["splitter_unreachable_lemmas"] == 0


def test_release_ready_vocabulary_loads_without_audit_override():
    assert FixedVocabulary(VOCABULARY_DIR).release_ready


def test_vocabulary_rejects_unknown_tokens_and_ids(vocabulary):
    with pytest.raises(ValueError, match="absent"):
        vocabulary.encode(("<NOT_IN_VOCABULARY>",))
    with pytest.raises(ValueError, match="outside"):
        vocabulary.decode((len(vocabulary.tokens),))
