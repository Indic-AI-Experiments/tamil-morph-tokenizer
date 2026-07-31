from tamil_morph_tokenizer.analysis import parse_analysis
from tamil_morph_tokenizer.signature import TAG_VARIANT_TOKENS, TagSignatureCodebook


def test_tag_signature_codebook_is_checksum_pinned_and_bounded():
    codebook = TagSignatureCodebook()

    maximum_patterns = max(
        len(codebook.patterns(model, tokens))
        for model, tokens in codebook._load()
    )
    assert len(codebook) > 0
    assert TAG_VARIANT_TOKENS == tuple(
        f"<TAG_VARIANT_{index}>" for index in range(1, maximum_patterns)
    )
    for (model, morph_tokens), patterns in codebook._load().items():
        for raw_tags in patterns:
            analysis = parse_analysis(f"வேர்+{raw_tags}", model=model)
            assert analysis.morph_tokens == morph_tokens


def test_tag_signature_codebook_round_trips_exact_raw_suffix():
    codebook = TagSignatureCodebook()
    model = "noun.fst"
    morph_tokens = ("<POS_NOUN>", "<NUM_PL>", "<CASE_ACC>")
    patterns = codebook.patterns(model, morph_tokens)

    assert patterns
    for variant, raw_tags in enumerate(patterns):
        assert codebook.variant_for(model, morph_tokens, raw_tags) == variant
        assert codebook.raw_tags(model, morph_tokens, variant) == raw_tags
