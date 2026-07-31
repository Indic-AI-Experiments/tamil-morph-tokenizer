from __future__ import annotations

from tamil_morph_tokenizer.api import (
    TokenizeRequest,
    get_codec,
    get_tokenizer,
    get_vocabulary,
    tokenize,
)


def test_api_defaults_to_compact_ambiguity() -> None:
    request = TokenizeRequest(text="மரங்களை")

    assert request.mode == "compact_ambiguity"


def test_api_serializes_tokenizer_records() -> None:
    response = tokenize(TokenizeRequest(text="மரங்களை"), None)

    assert response.mode == "compact_ambiguity"
    assert response.records[0].surface == "மரங்களை"
    assert response.records[0].tokens
    assert response.records[0].analyses
    assert response.tokens[0] == "<WORD_START>"
    assert len(response.token_ids) == len(response.tokens)
    assert get_codec("compact_ambiguity").decode_ids(
        response.token_ids,
        get_vocabulary(),
    ) == "மரங்களை"


def test_api_preserves_whitespace_and_exposes_the_authoritative_stream() -> None:
    text = "  மரம்  காடு\n"

    response = tokenize(TokenizeRequest(text=text), None)

    assert response.tokens[:2] == ["<BYTE_20>", "<BYTE_20>"]
    assert response.tokens[-1] == "<BYTE_0A>"
    assert "<WORD_END>" not in response.tokens
    assert "<BYTE_SPAN_START>" not in response.tokens
    assert "<BYTE_SPAN_END>" not in response.tokens
    assert get_codec("compact_ambiguity").decode_ids(
        response.token_ids,
        get_vocabulary(),
    ) == text

    get_tokenizer.cache_clear()
    get_codec.cache_clear()


def test_api_labels_punctuation_as_intentional_byte_encoding() -> None:
    response = tokenize(TokenizeRequest(text="."), None)

    assert response.records[0].fallback == "punctuation"
    assert response.tokens == ["<BYTE_2E>"]
