import shutil

import pytest

from tamil_morph_tokenizer.codec import (
    StructuredReversibleCodec,
    WORD_START,
    decode_utf8_bytes,
    encode_utf8_bytes,
)
from tamil_morph_tokenizer.fallback import tamil_grapheme_token
from tamil_morph_tokenizer.tokenizer import TamilMorphTokenizer


def test_utf8_byte_tokens_round_trip_arbitrary_unicode():
    text = "தமிழ் e\u0301 🙂\n"

    tokens = encode_utf8_bytes(text)

    assert decode_utf8_bytes(tokens) == text
    assert all(token.startswith("<BYTE_") for token in tokens)


def test_utf8_byte_decoder_rejects_non_byte_token():
    with pytest.raises(ValueError, match="Not a UTF-8 byte token"):
        decode_utf8_bytes(("<POS_NOUN>",))


@pytest.fixture(scope="module")
def codec():
    return StructuredReversibleCodec()


def test_reversible_codec_uses_compact_ambiguity_by_default():
    assert StructuredReversibleCodec().tokenizer.mode == "compact_ambiguity"


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
class TestStructuredReversibleCodec:
    def test_thirukkural_first_line_is_semantic_compact_and_exact(self):
        text = "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு"
        tokenizer = TamilMorphTokenizer(mode="best", use_default_entities=False)
        codec = StructuredReversibleCodec(tokenizer)

        encoding = codec.encode(text)

        assert codec.decode(encoding) == text
        assert len(encoding.tokens) == 41
        assert sum(token.startswith("<BYTE_") for token in encoding.tokens) == 6
        assert all(
            record.fallback is None for record in tokenizer.tokenize(text)
        )

    def test_ambiguity_is_canonical_in_the_reversible_token_stream(self):
        codec = StructuredReversibleCodec()
        encoding = codec.encode("எத்தனை")

        assert "<READINGS>" in encoding.tokens
        assert "<ALT>" in encoding.tokens
        assert "<ANALYSIS_START>" not in encoding.tokens
        assert "<ANALYSIS_END>" not in encoding.tokens
        assert not any(
            "_CAND_" in token or token.startswith("<CAND_")
            for token in encoding.tokens
        )
        assert codec.decode_tokens(encoding.tokens) == "எத்தனை"

    def test_ambiguous_decomposed_compound_uses_selected_reading_for_inverse(self, codec):
        encoding = codec.encode("ஆகக்கூடி")
        span = encoding.spans[0]

        assert span.selected_analysis is not None
        assert span.selected_analysis.lemma == "ஆகக்கூடு"
        assert "<READINGS>" in span.tokens
        assert "<LINK_INFINITIVE>" in span.tokens
        assert codec.decode_tokens(encoding.tokens) == "ஆகக்கூடி"

    @pytest.mark.parametrize("surface", ["அடிக்குள்", "உள்ளடிக்குள்"])
    def test_postposition_semantic_token_is_not_stripped_from_fst_signature(
        self,
        codec,
        surface,
    ):
        encoding = codec.encode(surface)

        assert "<POST_WITHIN_BY>" in encoding.tokens
        assert "<READINGS>" in encoding.tokens
        assert codec.decode_tokens(encoding.tokens) == surface

    def test_literal_auxiliary_is_lexical_semantic_and_reversible(self, codec):
        encoding = codec.encode("செய்யாவிட்டால்")

        assert encoding.spans[0].semantic_tokens == (
            "செய்",
            "<POLARITY_NEG>",
            "<LINK_VPART>",
            "விடு",
            "<MOOD_CONDITIONAL>",
        )
        assert "<AUXILIARY>" not in encoding.tokens
        assert codec.decode(encoding) == "செய்யாவிட்டால்"

    def test_nondefault_noun_realization_is_surface_free_and_reversible(self, codec):
        encoding = codec.encode("மரங்களை")
        span = encoding.spans[0]

        assert span.surface == "மரங்களை"
        assert span.lemma == "மரம்"
        assert span.semantic_tokens == (
            "மரம்",
            "<POS_NOUN>",
            "<NUM_PL>",
            "<CASE_ACC>",
        )
        assert span.realization is not None
        assert span.realization.tokens == ("<REALIZATION_1>",)
        assert "மரங்களை" not in span.tokens
        assert codec.decode(encoding) == "மரங்களை"
        assert codec.decode_tokens(encoding.tokens) == "மரங்களை"

    def test_default_noun_realization_needs_no_extra_token(self, codec):
        encoding = codec.encode("மரங்களினை")
        span = encoding.spans[0]

        assert span.realization is not None
        assert span.realization.strategy == "default"
        assert span.realization.tokens == ()
        assert codec.decode(encoding) == "மரங்களினை"

    @pytest.mark.parametrize("surface", ["படித்தேன்", "பயன்படுத்தினேன்"])
    def test_exact_past_forms_need_no_realization_token(self, codec, surface):
        encoding = codec.encode(surface)
        span = encoding.spans[0]

        assert span.realization is not None
        assert span.realization.strategy == "unique"
        assert span.realization.tokens == ()
        assert codec.decode(encoding) == surface

    def test_curated_lexical_semantics_are_retained(self, codec):
        encoding = codec.encode("வேண்டும்")
        span = encoding.spans[0]

        assert "<MODAL_MUST>" in span.semantic_tokens
        assert "<MODAL_MUST>" in span.tokens
        assert codec.decode(encoding) == "வேண்டும்"

    def test_equivalent_multi_model_analysis_uses_one_model_consistently(self, codec):
        encoding = codec.encode("முடியும்")
        span = encoding.spans[0]

        assert "<FST_MODEL_VERB_C4>" in span.tokens
        assert "<FST_MODEL_VERB_C11>" not in span.tokens
        assert codec.decode(encoding) == "முடியும்"

    @pytest.mark.parametrize(
        ("surface", "expected_lexical_tokens", "raw_lemma"),
        [
            ("படித்துக்கொடுத்தான்", ("படி", "<LINK_VPART>", "கொடு"), "படித்துக்கொடு"),
            ("செய்துவிட்டான்", ("செய்", "<LINK_VPART>", "விடு"), "செய்"),
            (
                "படிக்கப்படமுடியும்",
                ("படி", "<VOICE_PASSIVE>", "<MODAL>", "<LINK_INFINITIVE>", "முடி"),
                "படி",
            ),
        ],
    )
    def test_productive_compounds_are_semantic_and_reversible(
        self,
        codec,
        surface,
        expected_lexical_tokens,
        raw_lemma,
    ):
        encoding = codec.encode(surface)
        span = encoding.spans[0]

        assert span.semantic_tokens[:len(expected_lexical_tokens)] == expected_lexical_tokens
        assert span.selected_analysis is not None
        assert span.selected_analysis.lemma == raw_lemma
        assert span.lemma == expected_lexical_tokens[0]
        assert span.fst_lemma == raw_lemma
        if raw_lemma != expected_lexical_tokens[0]:
            assert raw_lemma not in span.tokens
        assert "<FST_LEMMA_BYTES_START>" not in span.tokens
        assert "<FST_TAGS_START>" not in span.tokens
        assert codec.decode_tokens(encoding.tokens) == surface

    @pytest.mark.parametrize(
        ("surface", "expected_variant"),
        [
            ("அகைக்கக்கூடும்", ()),
            ("அகையக்கூடும்", ("<REALIZATION_1>",)),
        ],
    )
    def test_compound_connector_spelling_variants_use_realization_selector(
        self,
        codec,
        surface,
        expected_variant,
    ):
        encoding = codec.encode(surface)
        span = encoding.spans[0]

        assert not any(token.startswith("<COMPOUND_VARIANT_") for token in span.tokens)
        assert tuple(token for token in span.tokens if token.startswith("<REALIZATION_")) == expected_variant
        assert "<FST_LEMMA_BYTES_START>" not in span.tokens
        assert codec.decode(encoding) == surface

    def test_mixed_text_preserves_unknowns_punctuation_and_whitespace(self, codec):
        text = "மரங்களை  xyz🙂\nஅறியாதசொல்!"

        encoding = codec.encode(text)

        assert codec.decode(encoding) == text
        assert codec.decode_tokens(encoding.tokens) == text
        assert any(span.kind == "whitespace" for span in encoding.spans)
        assert any(
            span.surface == "அறியாதசொல்"
            and span.kind == "tamil_grapheme_fallback"
            for span in encoding.spans
        )
        assert all(
            token.startswith("<BYTE_")
            for span in encoding.spans
            if span.kind in {"whitespace", "byte_fallback"}
            for token in span.tokens
        )
        assert all(
            obsolete not in encoding.tokens
            for obsolete in ("<WORD_END>", "<BYTE_SPAN_START>", "<BYTE_SPAN_END>")
        )

    def test_unknown_tamil_uses_compact_exact_graphemes(self, codec):
        surface = "அறியாதசொல்"

        encoding = codec.encode(surface)
        span = encoding.spans[0]

        assert span.kind == "tamil_grapheme_fallback"
        assert span.fallback == "tamil_graphemes"
        assert span.tokens == (
            WORD_START,
            *(
                tamil_grapheme_token(grapheme)
                for grapheme in ("அ", "றி", "யா", "த", "சொ", "ல்")
            ),
        )
        assert len(span.tokens) == 7
        assert len(span.tokens) < len(surface.encode("utf-8"))
        assert codec.decode_tokens(encoding.tokens) == surface

    def test_malformed_tamil_grapheme_retains_byte_escape(self, codec):
        surface = "பஂ"

        encoding = codec.encode(surface)
        span = encoding.spans[0]

        assert span.kind == "byte_fallback"
        assert span.fallback == "utf8_bytes"
        assert all(token.startswith("<BYTE_") for token in span.tokens)
        assert codec.decode_tokens(encoding.tokens) == surface

    def test_analyzed_words_need_only_a_start_boundary(self, codec):
        encoding = codec.encode("மரம் காடு")

        assert encoding.tokens.count(WORD_START) == 2
        assert "<WORD_END>" not in encoding.tokens
        assert "<FST_SIGNATURE_START>" not in encoding.tokens
        assert "<FST_SIGNATURE_END>" not in encoding.tokens
        assert encoding.tokens.count("<FST_MODEL_NOUN>") == 2
        assert codec.decode_tokens(encoding.tokens) == "மரம் காடு"

    def test_common_whitespace_is_encoded_as_direct_bytes(self, codec):
        encoding = codec.encode("மரம்  காடு\n")

        whitespace = [span for span in encoding.spans if span.kind == "whitespace"]
        assert [span.tokens for span in whitespace] == [
            ("<BYTE_20>", "<BYTE_20>"),
            ("<BYTE_0A>",),
        ]
        assert codec.decode_tokens(encoding.tokens) == "மரம்  காடு\n"

    @pytest.mark.parametrize(
        "text",
        [
            "பா. என்ன?! வா...",
            "“தமிழ்,” என்றார்.",
            "தி.மு.க., 3.14; 1,23,456 பேர்",
            "தமிழ்—மொழி (சோதனை)\nஅடுத்த வரி!",
        ],
    )
    def test_punctuation_abbreviations_and_spacing_roundtrip_exactly(self, codec, text):
        encoding = codec.encode(text)

        assert codec.decode_tokens(encoding.tokens) == text
        assert codec.decode(encoding) == text

    def test_non_normalized_tamil_is_preserved_byte_for_byte(self, codec):
        text = "கொ"

        encoding = codec.encode(text)

        assert codec.decode(encoding) == text
        assert codec.decode(encoding).encode("utf-8") == text.encode("utf-8")

    def test_decode_uses_only_flat_tokens_not_record_surface_metadata(self, codec):
        encoding = codec.encode("மரங்களை படித்தேன்")

        assert codec.decode_tokens(encoding.tokens) == "மரங்களை படித்தேன்"

    def test_structured_fallback_semantics_and_surface_are_both_reversible(self, codec):
        text = "18ம் தி.மு.க"
        encoding = codec.encode(text)

        assert codec.decode_tokens(encoding.tokens) == text
        ordinal = next(span for span in encoding.spans if span.surface == "18ம்")
        assert ordinal.semantic_tokens == ("18", "<NUM_ORDINAL>")
        assert ordinal.kind == "structured_byte_fallback"
